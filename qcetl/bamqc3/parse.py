"""
BamQC parsing module.

Parse individual BamQC records and combine them into master data table. Cache
master data tables for quick retrieval.
"""

import json
import logging
from typing import Dict, Any, Tuple

import numpy
import pandas
from pandas import DataFrame, Series

from qcetl.column import (
    BamQc3Column as Column,
    BamQc3IntHistColumn,
    BamQc3MergedColumn,
)
from qcetl.common.utility import (
    median_from_frequency_table,
    quantile_from_frequency_table,
)

logger = logging.getLogger(__name__)


def extract_flat_fields(
    input_data: Dict[str, Any], merged: bool
) -> Dict[str, Any]:
    """
    Extract the flat fields (int, float, str) from the json

    Args:
        input_data: The loaded BamQC JSON
        merged: Is this data from a merged BAM file
    Returns:
        a dictionary with a row
    """

    result = {}
    for column in [
        Column.AlignedReference,
        Column.AverageReadLength,
        Column.BasesMapped,
        Column.DeletedBases,
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
        Column.QualityCutoff,
        Column.QualityFailedReads,
        Column.Read1AverageLength,
        Column.Read2AverageLength,
        Column.ReadsMappedAndPaired,
        Column.ReadsOnTarget,
        Column.ReadsPerStartPoint,
        Column.ReadsMissingMDTags,
        Column.Sample,
        Column.SampleLevel,
        Column.SampleTotal,
        Column.SoftClipBases,
        Column.TargetFile,
        Column.TotalBasesOnTarget,
        Column.TotalReads,
        Column.TotalTargetSize,
        Column.UnmappedReads,
        Column.WorkflowVersion,
    ]:
        result[column] = input_data[column]

    for md_column in [
        "ESTIMATED_LIBRARY_SIZE",
        "LIBRARY",
        "PERCENT_DUPLICATION",
        "READ_PAIR_DUPLICATES",
        "READ_PAIR_OPTICAL_DUPLICATES",
        "READ_PAIRS_EXAMINED",
        "UNMAPPED_READS",
        "UNPAIRED_READ_DUPLICATES",
        "UNPAIRED_READS_EXAMINED",
    ]:
        result["mark duplicates_" + md_column] = input_data["mark duplicates"][
            md_column
        ]

    if merged:
        result[BamQc3MergedColumn.Donor] = input_data["donor"]
        result[BamQc3MergedColumn.GroupID] = input_data["group id"]
        result[BamQc3MergedColumn.LibraryDesign] = input_data["library design"]
        result[BamQc3MergedColumn.TissueOrigin] = input_data["tissue origin"]
        result[BamQc3MergedColumn.TissueType] = input_data["tissue type"]
    else:
        result[Column.Run] = input_data["run name"]
        result[Column.Lane] = input_data["lane"]
        result[Column.Barcodes] = input_data["barcode"]
        result[Column.Reference] = input_data.get("reference", "Unknown")

    return result


def parse_int_histogram(input_json: Dict[str, Any]) -> DataFrame:
    """
    Extracts the histograms that have an int as the value being counted. Currently, this
    is true of all histograms produced by BamQC.

    Args:
        input_json: The loaded BamQC JSON

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
                BamQc3IntHistColumn.Value: list(input_json[f].keys()),
                BamQc3IntHistColumn.Count: list(input_json[f].values()),
            }
        )
        df[BamQc3IntHistColumn.Name] = f
        # Category values will reduce size, but require extra fixes (run tests)
        # df[BamQc3IntHistColumn.Name] = df[BamQc3IntHistColumn.Name].astype("category")
        # JSON keys are strings
        df[BamQc3IntHistColumn.Value] = df[BamQc3IntHistColumn.Value].astype(
            int
        )

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
        df: The parsed BamQC3 dataframe

    Returns: The normalization factors for each row

    """
    norm = df[Column.TotalReads] / df[Column.SampleTotal]

    # Sample Total is NaN if no downsampling occurred
    norm = norm.fillna(1)

    return norm


def parse_record(path: str, merged: bool) -> Tuple[DataFrame, DataFrame]:
    """
    Parse a single BamQC record

    Args:
        path: Path to the BamQC JSON File
        merged: Is this record from merged BAM data.

    Returns:

    """
    with open(path, "r") as f:
        loaded = json.load(f)

    hist = parse_int_histogram(loaded)

    df = extract_flat_fields(loaded, merged)

    insert_size_hist = hist[
        hist[BamQc3IntHistColumn.Name] == "insert size histogram"
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

    df = pandas.json_normalize(df)
    # JSON null is converted to None. Covert that to NaN for consistency
    df = df.fillna(value=numpy.nan)

    # Add additional columns if the DataFrame is not empty
    if not df.empty:
        df[Column.Coverage] = (
            df[Column.TotalBasesOnTarget]
            / df[Column.TotalTargetSize]
            * calculate_downsampling_normalization(df)
        )
        df[Column.CoverageDeduplicated] = df[Column.Coverage] * (
            1 - df[Column.MarkDuplicates_PERCENT_DUPLICATION]
        )

        if merged:
            hist[BamQc3MergedColumn.Donor] = loaded["donor"]
            hist[BamQc3MergedColumn.GroupID] = loaded["group id"]
            hist[BamQc3MergedColumn.LibraryDesign] = loaded["library design"]
            hist[BamQc3MergedColumn.TissueOrigin] = loaded["tissue origin"]
            hist[BamQc3MergedColumn.TissueType] = loaded["tissue type"]
        else:
            hist[BamQc3IntHistColumn.Run] = loaded["run name"]
            hist[BamQc3IntHistColumn.Lane] = loaded["lane"]
            hist[BamQc3IntHistColumn.Barcodes] = loaded["barcode"]
            hist[BamQc3IntHistColumn.Reference] = loaded.get(
                "reference", "Unknown"
            )

    return df, hist.reset_index(drop=True)
