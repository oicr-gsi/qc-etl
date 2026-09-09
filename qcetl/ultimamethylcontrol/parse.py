import os
import re

import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import UltimaMethylControlColumn as Column

BARCODE_INDEX_PATTERN = re.compile(r"-(Z\d+)-")

DETAIL_TO_COLUMN = {
    "Lambda": Column.PercentMethylationMeanLambda,
    "pUC19": Column.PercentMethylationMeanPuc19,
    "hg": Column.PercentMethylationMeanHg,
}


def parse_record(path: str) -> DataFrame:
    """
    Parses a single Ultima EM-seq `_mergeContext.csv` file into a single row
    with the mean percent-methylation of each control (Lambda, pUC19, hg) as
    its own column.

    `library` and `index` are derived from the filename, following the same
    convention as `Examples/ultima_methyl_control.py`:
    `<project>-<library>-<Zbarcode>-<indexSequence>_mergeContext.csv`

    Args:
        path: File path of the `_mergeContext.csv` file

    Returns: DataFrame with a single row

    Raises:
        InvalidRecordError: If the file has no PercentMethylation_mean rows,
            or the filename doesn't contain a `Z####`-style index token

    """
    df = pandas.read_csv(path)
    df = df[df["metric"] == "PercentMethylation_mean"]

    if df.empty:
        raise InvalidRecordError(
            "File {} has no PercentMethylation_mean rows".format(path)
        )

    basename = os.path.basename(path)
    match = BARCODE_INDEX_PATTERN.search(basename)
    if not match:
        raise InvalidRecordError(
            "Could not find a Z####-style index in filename {}".format(basename)
        )

    library = basename.split("-", 1)[1].rsplit("-", 2)[0]
    index = match.group(1)

    row = {Column.Library: library, Column.BarcodeName: index}
    for detail, value in zip(df["detail"], df["value"]):
        if detail in DETAIL_TO_COLUMN:
            row[DETAIL_TO_COLUMN[detail]] = value

    return DataFrame([row])
