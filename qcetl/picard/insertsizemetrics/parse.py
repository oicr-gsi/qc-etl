from typing import Tuple
import numpy
import pandas
from pandas import DataFrame

from qcetl.column import (
    InsertSizeMetricsColumn as Column,
    InsertSizeMetricsHistogramColumn as HistColumn,
)

metrics_dtypes = {
    Column.MedianInsertSize: float,
    Column.ModeInsertSize: float,
    Column.MedianAbsoluteDeviation: float,
    Column.MinInsertSize: int,
    Column.MaxInsertSize: int,
    Column.MeanInsertSize: float,
    Column.StandardDeviation: float,
    Column.ReadPairs: int,
    Column.PairOrientation: str,
    Column.WidthOf10Percent: int,
    Column.WidthOf20Percent: int,
    Column.WidthOf30Percent: int,
    Column.WidthOf40Percent: int,
    Column.WidthOf50Percent: int,
    Column.WidthOf60Percent: int,
    Column.WidthOf70Percent: int,
    Column.WidthOf80Percent: int,
    Column.WidthOf90Percent: int,
    Column.WidthOf95Percent: int,
    Column.WidthOf99Percent: int,
}


def parse_record(path: str) -> Tuple[DataFrame, DataFrame]:
    """
    Convert the InsertSizeMetrics output to DataFrames

    Args:
        path: File path to file

    Returns: The METRICS CLASS data. The insert size histogram

    """
    with open(path, "r") as f:
        metrics_data = []
        metrics_cols = []

        for line in f:
            if line.startswith("## METRICS CLASS"):
                # Ignore newlines
                metrics_cols = f.readline()[:-1].split("\t")
                metrics_data = f.readline()[:-1].split("\t")
                break

        df = pandas.DataFrame.from_records([metrics_data], columns=metrics_cols)

        # For the histogram, insert sizes are broken into three possible columns
        # All_Reads.fr_count, All_Reads.rf_count, All_Reads.tandem_count
        # Add one column, count, that sums them all together
        for line in f:
            if line.startswith("## HISTOGRAM"):
                hist = pandas.read_csv(f, sep="\t")

        hist_sum = hist.loc[:, hist.columns.str.startswith("All_Reads")].sum(
            axis=1
        )
        hist_sum.name = HistColumn.Count
        hist = hist.merge(hist_sum, left_index=True, right_index=True)

    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.replace(["", "?"], numpy.nan)
    df = df.astype(metrics_dtypes)
    return df, hist
