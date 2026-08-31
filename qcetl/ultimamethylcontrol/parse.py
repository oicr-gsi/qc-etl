import os
import re

import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import UltimaMethylControlColumn as Column

BARCODE_INDEX_PATTERN = re.compile(r"-(Z\d+)-")


def parse_record(path: str) -> DataFrame:
    """
    Parses a single Ultima EM-seq `_mergeContext.csv` file into the mean
    percent-methylation rows for each control (e.g. Lambda, pUC19, hg).

    `library` and `index` are derived from the filename, following the same
    convention as `Examples/ultima_methyl_control.py`:
    `<project>-<library>-<Zbarcode>-<indexSequence>_mergeContext.csv`

    Args:
        path: File path of the `_mergeContext.csv` file

    Returns: DataFrame with one row per control

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

    df = df.rename(columns={"value": Column.PercentMethylationMean})
    df = df.assign(**{Column.Library: library, Column.BarcodeName: index})

    return df[
        [
            Column.PercentMethylationMean,
            Column.Detail,
            Column.Library,
            Column.BarcodeName,
        ]
    ]
