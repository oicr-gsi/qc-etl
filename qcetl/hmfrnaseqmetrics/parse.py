"""
Picard CollectRnaSeqMetrics parsing module.

Parses the single-row metrics section of a Picard ``CollectRnaSeqMetrics``
output file (``*.rna_seq_metrics.txt``) produced for a merged/call-ready RNA
BAM. The trailing normalized-coverage histogram is skipped. ``PCT_CODING_BASES``
provides the "mapped to coding" metric.
"""

import io
import logging

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import HmfRnaSeqMetricsColumn as Column

logger = logging.getLogger(__name__)

# The metric columns kept from the Picard metrics section (raw Picard names),
# pared to the metrics the QC report needs: mapped-to-coding and rRNA fractions.
METRIC_COLUMNS = [
    Column.PctCodingBases,
    Column.PctRibosomalBases,
]


def parse_record(path: str) -> DataFrame:
    """
    Parse the metrics section of a Picard CollectRnaSeqMetrics file.

    Args:
        path: Path to ``*.rna_seq_metrics.txt``

    Returns: A one-row DataFrame of the declared metric columns
    """
    section = None
    metrics = ""

    with open(path, "r") as f:
        for line in f:
            if line.startswith("## METRICS CLASS"):
                section = "metrics"
            elif line.startswith("## HISTOGRAM"):
                section = "histogram"
            elif section is None:
                continue
            elif not line.strip():
                section = None
            elif section == "metrics":
                metrics += line

    df = pandas.read_csv(io.StringIO(metrics), sep="\t").replace("?", numpy.nan)
    # Keep only the declared metric columns
    df = df[METRIC_COLUMNS]
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df
