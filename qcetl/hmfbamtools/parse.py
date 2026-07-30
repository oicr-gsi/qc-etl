"""
hmftools bam-tools (BamMetrics) parsing module.

Parses the QC output produced by hmftools ``bam-tools`` for a merged/call-ready
BAM. A single build record points at the ``*.bam_metric.summary.tsv`` file; the
sibling metric files (coverage histogram, fragment-length histogram and
flag counts) are derived from it as they share the ``*.bam_metric.`` prefix.
"""

import logging
import re
from typing import Dict

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import (
    HmfBamToolsSummaryColumn as Summary,
    HmfBamToolsCoverageColumn as Coverage,
    HmfBamToolsFragmentLengthColumn as FragLength,
    HmfBamToolsFlagstatColumn as Flagstat,
)

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

# `<passed> + <failed> <description>`, e.g. "73098 + 0 properly paired (98.64% : N/A)"
_FLAGSTAT_LINE = re.compile(r"^(\d+)\s*\+\s*(\d+)\s+(.*)$")
# A trailing percentage annotation, e.g. "(98.64% : N/A)". Distinct from a
# category qualifier such as "(mapQ>=5)", which carries no percent sign.
_FLAGSTAT_PERCENT = re.compile(r"\(([\d.]+)%[^)]*\)\s*$")


def sibling_path(summary_path: str, suffix: str) -> str:
    """
    Derive a sibling bam_metric file path from the summary file path.

    Args:
        summary_path: Path to the ``*.bam_metric.summary.tsv`` file
        suffix: The replacement suffix, e.g. ``.coverage.tsv``

    Returns: The sibling file path
    """
    if not summary_path.endswith(SUMMARY_SUFFIX):
        raise ValueError(
            "Expected a path ending in {} but got {}".format(
                SUMMARY_SUFFIX, summary_path
            )
        )
    return summary_path[: -len(SUMMARY_SUFFIX)] + suffix


def parse_summary(path: str) -> DataFrame:
    """
    Parse the single-row summary metrics table.

    Args:
        path: Path to ``*.bam_metric.summary.tsv``

    Returns: A one-row DataFrame with declared column names
    """
    df = pandas.read_csv(path, sep="\t")
    df = df.rename(columns=SUMMARY_COLUMN_MAP)
    # Keep only known columns so a new upstream column does not break the schema
    df = df[list(SUMMARY_COLUMN_MAP.values())]
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df


def parse_coverage(path: str) -> DataFrame:
    """
    Parse the coverage-depth histogram.

    Args:
        path: Path to ``*.bam_metric.coverage.tsv``

    Returns: A DataFrame of coverage depth to base count
    """
    df = pandas.read_csv(path, sep="\t")
    return df.rename(
        columns={"Coverage": Coverage.Coverage, "Count": Coverage.Count}
    )


def parse_fragment_length(path: str) -> DataFrame:
    """
    Parse the fragment-length histogram.

    Args:
        path: Path to ``*.bam_metric.frag_length.tsv``

    Returns: A DataFrame of fragment length to read count
    """
    df = pandas.read_csv(path, sep="\t")
    return df.rename(
        columns={
            "FragmentLength": FragLength.FragmentLength,
            "Count": FragLength.Count,
        }
    )


def parse_flagstat(path: str) -> DataFrame:
    """
    Parse the samtools-flagstat style flag counts into a tidy table.

    Args:
        path: Path to ``*.bam_metric.flag_counts.tsv``

    Returns: A DataFrame with one row per flagstat category
    """
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = _FLAGSTAT_LINE.match(line)
            if match is None:
                logger.warning("Unparsed flagstat line: %s", line)
                continue

            passed, failed, description = match.groups()
            percentage = numpy.nan
            percent_match = _FLAGSTAT_PERCENT.search(description)
            if percent_match is not None:
                percentage = float(percent_match.group(1))
                description = description[: percent_match.start()].strip()

            rows.append(
                {
                    Flagstat.Category: description,
                    Flagstat.QcPassedReads: int(passed),
                    Flagstat.QcFailedReads: int(failed),
                    Flagstat.Percentage: percentage,
                }
            )

    return DataFrame(
        rows,
        columns=[
            Flagstat.Category,
            Flagstat.QcPassedReads,
            Flagstat.QcFailedReads,
            Flagstat.Percentage,
        ],
    )


def parse_record(summary_path: str) -> Dict[str, DataFrame]:
    """
    Parse all bam_metric tables for a single sample.

    Args:
        summary_path: Path to the ``*.bam_metric.summary.tsv`` file. The sibling
            coverage, fragment-length and flag-count files are derived from it.

    Returns: A mapping of table name to parsed DataFrame
    """
    return {
        "hmfbamtools": parse_summary(summary_path),
        "coverage": parse_coverage(
            sibling_path(summary_path, ".coverage.tsv")
        ),
        "fragment_length": parse_fragment_length(
            sibling_path(summary_path, ".frag_length.tsv")
        ),
        "flagstat": parse_flagstat(
            sibling_path(summary_path, ".flag_counts.tsv")
        ),
    }
