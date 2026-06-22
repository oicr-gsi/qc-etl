from typing import List, Dict
from pandas import DataFrame
import pandas
import numpy

from qcetl.column import Bcl2BarcodeCallerKnownColumn as KnownCol
from qcetl.column import Bcl2BarcodeCallerSummaryColumn as SummaryCol


def match(a: str, b: str, mismatch: int) -> bool:
    """
    Do the two string match, given the mismatch allowed

    Works for both single ("ATCG") and dual index ("ATCG-GTAC").
    Indices must be the same length for comparison.

    Args:
        a: First index to compare
        b: Second index to compare
        mismatch: How many base pairs are allowed to be different

    Returns: Did the two strings match?

    """
    if len(a) != len(b):
        return False

    dist = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            dist += 1

    return dist <= mismatch


def assign_library(df: DataFrame, known: List[List[str]], mismatch: int):
    """
    Adds the library the barcode is associated with and fixes the barcode. This happens in place.

    Args:
        df: The parsed bcl2barcode DataFrame
        known: A list of known barcodes. Each element is a list: [library, barcode]
        mismatch: How many mismatches are allowed
    """
    hit = []
    hit_barcode = []
    for barcode in df[KnownCol.Barcodes]:
        lib = numpy.nan
        bar = barcode
        for lib_bar in known:
            if match(barcode, lib_bar[1], mismatch):
                lib = lib_bar[0]
                bar = lib_bar[1]
                break

        hit.append(lib)
        hit_barcode.append(bar)

    df[KnownCol.Barcodes] = hit_barcode
    df[KnownCol.LibraryAlias] = hit


def parse_record(path: str, known: List[List[str]]) -> Dict[str, DataFrame]:
    """
    Splits bcl2barcode output into general metrics, known and error corrected barcodes, and unknown barcodes

    1 or 0 mismatches will be allowed. This approach assumes that all known indices are 2 or more mismatches apart.

    As mismatch calculations are expensive, only barcodes that have more than 1 millionth of the total reads
    will be considered. Excluded read number will be recorded.

    There will be thousands of unknown indices. Only the top 50 will be kept. Total number will be recorded.

    Args:
        path: Path to bcl2barcode output
        known: A list of known barcodes. Each element is a list: [library, barcode]

    Returns: A `summary` DataFrame with total read information, a `known` DataFrame with error corrected indices
        and their libraries, and an `unknown` DataFrame of unknown indices
    """

    barcodes = pandas.read_csv(
        path,
        header=None,
        names=["count", "Barcodes"],
    )
    total_reads = barcodes["count"].sum()
    # Filter out any barcodes that contribute negligibly to the overall read count; they are noise
    barcodes = barcodes[barcodes[KnownCol.Count].ge(total_reads / 1000000)]
    excluded_reads = total_reads - barcodes[KnownCol.Count].sum()

    assign_library(barcodes, known, 1)
    # As unknown barcodes have NaN in library, they will be excluded by the groupby
    known_df = barcodes.groupby(
        [KnownCol.Barcodes, KnownCol.LibraryAlias], as_index=False
    ).sum(numeric_only=True)
    # If the output is empty, the count column will be missing (but not the group columns)
    if known_df.empty:
        known_df[KnownCol.Count] = []

    known_reads = known_df[KnownCol.Count].sum()

    unknown_df = barcodes[barcodes[KnownCol.LibraryAlias].isna()].copy()
    unknown_df.drop(columns=KnownCol.LibraryAlias, inplace=True)
    unknown_reads = unknown_df[KnownCol.Count].sum()
    unknown_df = unknown_df.sort_values(
        [KnownCol.Count, KnownCol.Barcodes], ascending=False
    ).head(50)

    summary = pandas.json_normalize(
        {
            SummaryCol.TotalClusters: total_reads,
            SummaryCol.ExcludedClusters: excluded_reads,
            SummaryCol.KnownClusters: known_reads,
            SummaryCol.UnknownClusters: unknown_reads,
        }
    )

    return {
        "summary": summary,
        "known": known_df,
        "unknown": unknown_df,
    }
