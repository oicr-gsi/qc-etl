"""
bcl2barcode parsing module.
"""

import logging
from typing import Tuple

import pandas
from pandas import DataFrame

from qcetl.column import Bcl2BarcodeColumn, Bcl2BarcodeRunSummaryColumn

logger = logging.getLogger(__name__)


def parse_record(path: str) -> Tuple[DataFrame, DataFrame]:
    """
    Creates the master DataFrame

    Args:
        path: File path to record
    Returns:
        The first DataFrame is the parsed barcode counts, the second DataFrame is
        the calculated run metrics
    """
    barcodes = pandas.read_csv(
        path,
        header=None,
        names=[Bcl2BarcodeColumn.Count, Bcl2BarcodeColumn.Barcodes],
    )
    total_reads = barcodes[Bcl2BarcodeColumn.Count].sum()
    # Filter out any barcodes that contribute negligibly to the overall read count; they are noise
    barcodes = barcodes[
        barcodes[Bcl2BarcodeColumn.Count].ge(total_reads / 10000)
    ]

    run_summary = pandas.json_normalize(
        {Bcl2BarcodeRunSummaryColumn.TotalClusters: total_reads}
    )

    return barcodes, run_summary
