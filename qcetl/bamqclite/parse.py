"""
BamQcLite parsing module.

Parse individual BamQcLite records and combine them into master data table. Cache
master data tables for quick retrieval.
"""

import json
import logging
from typing import Dict, List, Any, Optional

import numpy
import pandas
from pandas import DataFrame, Series

from qcetl.column import (
    BamQcLiteColumn as Column,
    BamQcLiteIntHistColumn,
)
from qcetl.common.utility import (
    median_from_frequency_table,
    quantile_from_frequency_table,
)

logger = logging.getLogger(__name__)


def extract_flat_fields(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the flat fields (int, float, str) from the json

    Args:
        input_data: The loaded BamQC JSON
    Returns:
        a dictionary with a row
    """

    int_columns = {
        Column.ReadsOnTarget,
        Column.TotalBasesOnTarget,
    }
    result = {}
    for column in [
        Column.AlignedReference,
        Column.AverageReadLength,
        Column.BasesMapped,
        Column.DeletedBases,
        Column.DownsampledTotal,
        Column.HardClipBases,
        Column.InsertMax,
        Column.InsertMean,
        Column.InsertSD,
        Column.InsertCount,
        Column.Instrument,
        Column.Library,
        Column.MappedReads,
        Column.MismatchBases,
        Column.NonPrimaryReads,
        Column.NumberOfTargets,
        Column.PackageVersion,
        Column.PairedEnd,
        Column.PairedReads,
        Column.PairsMappedAbnormallyFar,
        Column.PairsMappedToDifferentChr,
        Column.ProperlyPairedReads,
        Column.Read1AverageLength,
        Column.Read2AverageLength,
        Column.ReadsMappedAndPaired,
        Column.ReadsOnTarget,
        Column.ReadsPerStartPoint,
        Column.ReadsMissingMDTags,
        Column.Sample,
        Column.SoftClipBases,
        Column.TargetFile,
        Column.TotalBasesOnTarget,
        Column.TotalReads,
        Column.TotalTargetSize,
        Column.UnmappedReads,
        Column.WorkflowVersion,
    ]:
        if column in int_columns:
            result[column] = input_data.get(column, 0)
        else:
            result[column] = input_data.get(column, numpy.nan)

    md = input_data.get("mark duplicates") or {}

    for md_column in [
        "PERCENT_DUPLICATION",
        "READ_PAIR_DUPLICATES",
        "READ_PAIRS_EXAMINED",
        "UNPAIRED_READ_DUPLICATES",
        "UNPAIRED_READS_EXAMINED",
    ]:
        result["mark duplicates_" + md_column] = md.get(md_column, numpy.nan)

    return result


def parse_int_histogram(input_json: Dict[str, Any]) -> DataFrame:
    """
    Extracts the histograms that have an int as the value being counted. Currently, this
    is true of all histograms produced by BamQcLite.

    Args:
        input_json: The loaded BamQcLite JSON

    Returns: The DataFrame with the added IUS columns and the `name` columns (which
        field did they come from)

    """
    results = []
    fields = [
        "read 1 length histogram",
        "read 2 length histogram",
        "read ? length histogram",
        "read 1 quality histogram",
        "read 2 quality histogram",
        "read ? quality histogram",
        "insert size histogram",
        "coverage histogram",
    ]
    for f in fields:
        df = DataFrame(
            {
                BamQcLiteIntHistColumn.Value: list(input_json[f].keys()),
                BamQcLiteIntHistColumn.Count: list(input_json[f].values()),
            }
        )
        df[BamQcLiteIntHistColumn.Name] = f
        # Category values will reduce size, but require extra fixes (run tests)
        # df[BamQc3IntHistColumn.Name] = df[BamQc3IntHistColumn.Name].astype("category")
        # JSON keys are strings
        df[BamQcLiteIntHistColumn.Value] = df[
            BamQcLiteIntHistColumn.Value
        ].astype(int)

        results.append(df)

    df = pandas.concat(results)
    return df


def calculate_downsampling_normalization(df: DataFrame) -> Series:
    """
    Bedtools data is normalized. Get the normalization factor to get it to
    reflect input BAM metrics

    In the `samtools stats` documentation, `raw total sequences` are documented
    to include secondary (non-primary) reads, but that is not the case.
    Non-Primary reads no not need to be subtracted from the total reads.

    Args:
        df: The parsed BamQcLite dataframe

    Returns: The normalization factors for each row

    """
    norm = df[Column.TotalReads] / df[Column.DownsampledTotal]

    # DownsampledTotal is NaN if no downsampling occurred
    with pandas.option_context("future.no_silent_downcasting", True):
        norm = norm.fillna(1)

    return norm


def parse_record(
    path: str, workflow_version: Optional[List[int]] = None
) -> DataFrame:
    """
    Parse a single BamQCLite record

    Args:
        path: Path to the BamQcLite JSON File
        workflow_version: What version of the workflow created file

    Returns:

    """
    with open(path, "r") as f:
        loaded = json.load(f)

    # GR-1243: `coverage_histogram` should have been `coverage histogram`
    if "coverage_histogram" in loaded:
        loaded["coverage histogram"] = loaded["coverage_histogram"]

    if "reads_on_target" in loaded:
        loaded["reads on target"] = loaded["reads_on_target"]

    hist = parse_int_histogram(loaded)

    df = extract_flat_fields(loaded)

    # Shesmu workflow version should be trusted over embedded one
    if workflow_version is not None:
        df[Column.WorkflowVersion] = ".".join(str(x) for x in workflow_version)
    else:
        workflow_version = [
            int(x) for x in loaded[Column.WorkflowVersion].split(".")
        ]

    insert_size_hist = hist[
        hist[BamQcLiteIntHistColumn.Name] == "insert size histogram"
    ]
    df[Column.InsertMedian] = median_from_frequency_table(insert_size_hist)
    df[Column.Insert10Percentile] = quantile_from_frequency_table(
        insert_size_hist, 0.1
    )
    df[Column.Insert90Percentile] = quantile_from_frequency_table(
        insert_size_hist, 0.9
    )
    df[Column.TotalClusters] = df[Column.TotalReads] / (
        2 if df[Column.PairedEnd] else 1
    )

    # Before 4.0.3, coverage histogram was down-sampled and median cannot
    # be easily calculated
    if workflow_version >= [4, 0, 3]:
        coverage_hist = hist[
            hist[BamQcLiteIntHistColumn.Name] == "coverage histogram"
        ]
        df[Column.CoverageMedian] = median_from_frequency_table(coverage_hist)
        df[Column.CoverageMedian10Percentile] = quantile_from_frequency_table(
            coverage_hist, 0.1
        )
        df[Column.CoverageMedian90Percentile] = quantile_from_frequency_table(
            coverage_hist, 0.9
        )
    else:
        df[Column.CoverageMedian] = numpy.nan
        df[Column.CoverageMedian10Percentile] = numpy.nan
        df[Column.CoverageMedian90Percentile] = numpy.nan

    df = pandas.json_normalize(df)
    # JSON null is converted to None. Covert that to NaN for consistency
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)

    # Add additional columns if the DataFrame is not empty
    if not df.empty:
        df[Column.Coverage] = (
            df[Column.ReadsOnTarget]
            * df[Column.AverageReadLength]
            / df[Column.TotalTargetSize]
        )
        df[Column.CoverageDeduplicated] = df[Column.Coverage] * (
            1 - df[Column.MarkDuplicates_PERCENT_DUPLICATION]
        )

    return df
