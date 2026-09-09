"""
hmftools bam-tools (BamMetrics) parsing module.

Parses the per-sample QC summary produced by hmftools ``bam-tools`` for a
merged/call-ready BAM. A single build record points at the
``*.bam_metric.summary.tsv`` file. The sibling ``*.bam_metric.frag_length.tsv``
histogram is read only to derive a mean insert size; it is not stored as its
own table.
"""

import logging
from typing import Dict

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import HmfBamToolsSummaryColumn as Summary

logger = logging.getLogger(__name__)

SUMMARY_SUFFIX = ".summary.tsv"

# Map the raw summary.tsv header to the declared DataFrame column name.
SUMMARY_COLUMN_MAP = {
    "TotalRegionBases": Summary.TotalRegionBases,
    "TotalReads": Summary.TotalReads,
    "DuplicateReads": Summary.DuplicateReads,
    "DualStrandReads": Summary.DualStrandReads,
    "MeanCoverage": Summary.MeanCoverage,
    "StdDevCoverage": Summary.StdDevCoverage,
    "MedianCoverage": Summary.MedianCoverage,
    "MadCoverage": Summary.MadCoverage,
    "LowMapQualPercent": Summary.LowMapQualPercent,
    "DuplicatePercent": Summary.DuplicatePercent,
    "UnpairedPercent": Summary.UnpairedPercent,
    "LowBaseQualPercent": Summary.LowBaseQualPercent,
    "OverlappingReadPercent": Summary.OverlappingReadPercent,
    "CappedCoverage": Summary.CappedCoverage,
    "DepthCoverage_1": Summary.DepthCoverage1,
    "DepthCoverage_5": Summary.DepthCoverage5,
    "DepthCoverage_10": Summary.DepthCoverage10,
    "DepthCoverage_15": Summary.DepthCoverage15,
    "DepthCoverage_20": Summary.DepthCoverage20,
    "DepthCoverage_25": Summary.DepthCoverage25,
    "DepthCoverage_30": Summary.DepthCoverage30,
    "DepthCoverage_40": Summary.DepthCoverage40,
    "DepthCoverage_50": Summary.DepthCoverage50,
    "DepthCoverage_60": Summary.DepthCoverage60,
    "DepthCoverage_70": Summary.DepthCoverage70,
    "DepthCoverage_80": Summary.DepthCoverage80,
    "DepthCoverage_90": Summary.DepthCoverage90,
    "DepthCoverage_100": Summary.DepthCoverage100,
}


def sibling_path(summary_path: str, suffix: str) -> str:
    """
    Derive a sibling bam_metric file path from the summary file path.

    Args:
        summary_path: Path to the ``*.bam_metric.summary.tsv`` file
        suffix: The replacement suffix, e.g. ``.frag_length.tsv``

    Returns: The sibling file path
    """
    if not summary_path.endswith(SUMMARY_SUFFIX):
        raise ValueError(
            "Expected a path ending in {} but got {}".format(
                SUMMARY_SUFFIX, summary_path
            )
        )
    return summary_path[: -len(SUMMARY_SUFFIX)] + suffix


def mean_insert_size(frag_length_path: str) -> float:
    """
    Compute the mean insert size from the fragment-length histogram.

    Args:
        frag_length_path: Path to ``*.bam_metric.frag_length.tsv``

    Returns: The count-weighted mean fragment length, or NaN if empty
    """
    hist = pandas.read_csv(frag_length_path, sep="\t")
    total = hist["Count"].sum()
    if total == 0:
        return numpy.nan
    return (hist["FragmentLength"] * hist["Count"]).sum() / total


def parse_summary(path: str) -> DataFrame:
    """
    Parse the single-row summary metrics table and add the derived mean
    insert size from the sibling fragment-length histogram.

    Args:
        path: Path to ``*.bam_metric.summary.tsv``

    Returns: A one-row DataFrame with declared column names
    """
    df = pandas.read_csv(path, sep="\t")
    df = df.rename(columns=SUMMARY_COLUMN_MAP)
    # Keep only known columns so a new upstream column does not break the schema
    df = df[list(SUMMARY_COLUMN_MAP.values())]

    df[Summary.MeanInsertSize] = mean_insert_size(
        sibling_path(path, ".frag_length.tsv")
    )

    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df


def parse_record(summary_path: str) -> Dict[str, DataFrame]:
    """
    Parse the summary table for a single sample.

    Args:
        summary_path: Path to the ``*.bam_metric.summary.tsv`` file

    Returns: A mapping of table name to parsed DataFrame
    """
    return {"summary": parse_summary(summary_path)}
