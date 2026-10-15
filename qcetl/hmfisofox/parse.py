"""
hmftools Isofox RNA QC parsing module.

Parses the per-sample Isofox summary (``*.isf.summary.csv``) for a
merged/call-ready RNA BAM. ``TotalFragments`` is the pipeline filtered cluster
count (fragments are already read pairs). rRNA contamination is taken from
Picard ``PCT_RIBOSOMAL_BASES`` (see ``hmfrnaseqmetrics``), not from Isofox.
"""

import logging

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import HmfIsofoxSummaryColumn as Column

logger = logging.getLogger(__name__)

# Map the raw isf.summary.csv header to the declared DataFrame column name.
SUMMARY_COLUMN_MAP = {
    "TotalFragments": Column.TotalFragments,
}


def parse_record(path: str) -> DataFrame:
    """
    Parse the single-row Isofox summary table.

    Args:
        path: Path to ``*.isf.summary.csv``

    Returns: A one-row DataFrame with declared column names
    """
    df = pandas.read_csv(path)
    df = df.rename(columns=SUMMARY_COLUMN_MAP)
    # Keep only known columns so a new upstream column does not break the schema
    df = df[list(SUMMARY_COLUMN_MAP.values())]
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df
