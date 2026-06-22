import logging

import json
import numpy
import pandas
import pandas.errors
from pandas import DataFrame

from qcetl.column import MutetctCallabilityColumn as Column

logger = logging.getLogger(__name__)


def parse_record(path: str) -> DataFrame:
    """
    Parse a single JSON record into a DataFrame

    Args:
        path: Path to raw record file

    Returns:

    """
    with open(path, "r") as f:
        row = json.load(f)

    df = pandas.json_normalize(row)

    # If all records are Mutect workflow, need to add normal and tumor min cov columns
    if Column.NormalMinCoverage not in df.columns:
        df[Column.NormalMinCoverage] = numpy.nan
    if Column.TumorMinCoverage not in df.columns:
        df[Column.TumorMinCoverage] = numpy.nan

    # Mutect has hardcoded callability values that are not in the JSON and are NaN
    df[Column.NormalMinCoverage] = (
        df[Column.NormalMinCoverage].fillna(8).infer_objects(copy=False)
    )
    df[Column.TumorMinCoverage] = (
        df[Column.TumorMinCoverage].fillna(14).infer_objects(copy=False)
    )

    return df
