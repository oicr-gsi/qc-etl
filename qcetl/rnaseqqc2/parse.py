"""
RNAseqQC parsing module.
"""

import json
import logging

import pandas
from pandas import DataFrame

from qcetl.column import BaseRnaSeqQc2Column as Column
from qcetl.common.utility import (
    none_to_nan_json_hook,
    median_from_frequency_table,
    quantile_from_frequency_table,
)

logger = logging.getLogger(__name__)


def parse_record(path: str) -> DataFrame:
    """
    Convert RNAseqQC JSON to DataFrame.

    Args:
        path: File path to RNAseqQC JSON file
    Returns:
        a dictionary with a row
    """

    result = {}
    with open(path, "r") as f:
        input_data = json.load(f, object_hook=none_to_nan_json_hook)

    for column in [
        Column.AlignedReference,
        Column.AverageReadLength,
        Column.BasesMapped,
        Column.DeletedBases,
        Column.InsertMax,
        Column.InsertMean,
        Column.InsertSD,
        Column.InsertCount,
        Column.MappedReads,
        Column.MismatchBases,
        Column.NonPrimaryReads,
        Column.PackageVersion,
        Column.PairedEnd,
        Column.PairedReads,
        Column.PairsMappedAbnormallyFar,
        Column.PairsMappedToDifferentChr,
        Column.ProperlyPairedReads,
        Column.Read1AverageLength,
        Column.Read2AverageLength,
        Column.ReadsMappedAndPaired,
        Column.TotalReads,
        Column.UnmappedReads,
    ]:
        result[column] = input_data["bamqc"][column]

    for column in [
        "duplicates",
        "in total (QC-passed reads + QC-failed reads)",
        "mapped",
        "paired in sequencing",
        "properly paired",
        "read1",
        "read2",
        "secondary",
        "singletons",
        "supplementary",
        "with itself and mate mapped",
        "with mate mapped to a different chr",
        "with mate mapped to a different chr (mapQ>=5)",
    ]:
        result["rrna contamination " + column] = input_data[
            "rrna_contamination"
        ][column]

    for metric_column, correction in [
        (Column.MetricsCorrectStrandReads, 1),
        (Column.MetricsIntronicBases, 1),
        (Column.MetricsIgnoredReads, 1),
        (Column.MetricsIncorrectStrandReads, 1),
        (Column.MetricsIntergenicBases, 1),
        (Column.MetricsMedian5PrimeTo3PrimeBias, 1),
        (Column.MetricsMedian3PrimeBias, 1),
        (Column.MetricsMedian5PrimeBias, 1),
        (Column.MetricsMedianCVCoverage, 1),
        (Column.MetricsNumRead1TranscriptStrandReads, 1),
        (Column.MetricsNumRead2TranscriptStrandReads, 1),
        (Column.MetricsNumUnexplainedReads, 1),
        (Column.MetricsPassedFilterAlignedBases, 1),
        (Column.MetricsPassedFilterBases, 1),
        (Column.MetricsPercentCodingBases, 100),
        (Column.MetricsPercentCorrectStrandReads, 100),
        (Column.MetricsPercentIntergenicBases, 100),
        (Column.MetricsPercentIntronicBases, 100),
        (Column.MetricsPercentMRnaBases, 100),
        (Column.MetricsPercentRead1TranscriptStrandReads, 100),
        (Column.MetricsPercentRead2TranscriptStrandReads, 100),
        (Column.MetricsPercentRibosomalBases, 100),
        (Column.MetricsPercentUTRBases, 100),
        (Column.MetricsPercentUsableBases, 100),
        (Column.MetricsRibosomalBases, 1),
        (Column.MetricsUTRBases, 1),
    ]:
        result[metric_column] = (
            input_data["picard"]["metrics"][metric_column] * correction
        )

    result[Column.UniqueReads] = input_data[Column.UniqueReads]
    result[Column.TotalClusters] = result[Column.TotalReads] / (
        2 if result[Column.PairedEnd] else 1
    )

    hist = input_data["bamqc"]["insert size histogram"]
    hist_df = pandas.DataFrame(
        {"value": [int(x) for x in hist.keys()], "count": list(hist.values())}
    )
    result[Column.InsertMedian] = median_from_frequency_table(hist_df)
    result[Column.InsertMedian10Percentile] = quantile_from_frequency_table(
        hist_df, 0.1
    )
    result[Column.InsertMedian90Percentile] = quantile_from_frequency_table(
        hist_df, 0.9
    )

    df = pandas.json_normalize(result)
    # The column name is too long and would get truncated in postgres
    df = df.rename(
        columns={
            "rrna contamination with mate mapped to a different chr (mapQ>=5)": Column.RRnaContaminationWithMateMappedToDifferentChrAndGoodMapQ
        }
    )
    return df
