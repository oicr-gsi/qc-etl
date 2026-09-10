import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import UltimaMethylControlColumn as Column

METRIC_DETAIL_TO_COLUMN = {
    "PercentMethylation_mean": {
        "Lambda": Column.PercentMethylationMeanLambda,
        "pUC19": Column.PercentMethylationMeanPuc19,
        "hg": Column.PercentMethylationMeanHg,
    },
    "Coverage_mean": {
        "Lambda": Column.CoverageMeanLambda,
        "pUC19": Column.CoverageMeanPuc19,
        "hg": Column.CoverageMeanHg,
    },
}


def parse_record(path: str) -> DataFrame:
    """
    Parses a single Ultima EM-seq `_mergeContext.csv` file into a single row
    with the mean percent-methylation and mean coverage of each control
    (Lambda, pUC19, hg) as its own column.

    Args:
        path: File path of the `_mergeContext.csv` file

    Returns: DataFrame with a single row

    Raises:
        InvalidRecordError: If the file has no PercentMethylation_mean rows

    """
    df = pandas.read_csv(path)
    df = df[df["metric"].isin(METRIC_DETAIL_TO_COLUMN)]

    if df[df["metric"] == "PercentMethylation_mean"].empty:
        raise InvalidRecordError(
            "File {} has no PercentMethylation_mean rows".format(path)
        )

    row = {}
    for metric, detail, value in zip(df["metric"], df["detail"], df["value"]):
        detail_to_column = METRIC_DETAIL_TO_COLUMN[metric]
        if detail in detail_to_column:
            row[detail_to_column[detail]] = value

    return DataFrame([row])
