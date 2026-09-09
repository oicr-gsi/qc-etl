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

# The metric columns kept from the Picard metrics section (raw Picard names).
METRIC_COLUMNS = [
    Column.PfBases,
    Column.PfAlignedBases,
    Column.RibosomalBases,
    Column.CodingBases,
    Column.UtrBases,
    Column.IntronicBases,
    Column.IntergenicBases,
    Column.IgnoredReads,
    Column.CorrectStrandReads,
    Column.IncorrectStrandReads,
    Column.NumR1TranscriptStrandReads,
    Column.NumR2TranscriptStrandReads,
    Column.NumUnexplainedReads,
    Column.PctR1TranscriptStrandReads,
    Column.PctR2TranscriptStrandReads,
    Column.PctRibosomalBases,
    Column.PctCodingBases,
    Column.PctUtrBases,
    Column.PctIntronicBases,
    Column.PctIntergenicBases,
    Column.PctMrnaBases,
    Column.PctUsableBases,
    Column.PctCorrectStrandReads,
    Column.MedianCvCoverage,
    Column.Median5PrimeBias,
    Column.Median3PrimeBias,
    Column.Median5PrimeTo3PrimeBias,
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
    # Keep only the declared metric columns (drops SAMPLE/LIBRARY/READ_GROUP)
    df = df[METRIC_COLUMNS]
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df
