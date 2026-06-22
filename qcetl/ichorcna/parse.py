import logging
from typing import Dict

import numpy
import pandas
import pandas.errors
from pandas import DataFrame

import qcetl.column
from qcetl.common import InvalidRecordError

logger = logging.getLogger(__name__)


def parse_record(path: str, schema: Dict[str, str]) -> DataFrame:
    """
    Combine IchorCNA data into one DataFrame

    Args:
        path: File path to record
        schema: Type annotation for columns

    Returns:

    """

    row = {}
    for column in qcetl.column.BaseIchorCnaColumn.values():
        row[column] = numpy.nan

    with open(path, "r") as f:
        f.readline()  # Discard header
        sample = f.readline().split("\t")[0]
        line = f.readline().strip()
        while line is not None and line != sample:
            line = f.readline().strip()
        line = f.readline().strip()
        while line:
            key, value = line.split(":", 2)
            if key in row:
                type_signature = schema[key]
                if type_signature == "i":
                    value = int(value)
                elif type_signature == "f":
                    if value.strip() == "NA":
                        value = numpy.nan
                    else:
                        value = float(value)
                elif type_signature == "s":
                    value = value.strip()
                else:
                    raise InvalidRecordError(
                        "Cannot convert column %s with type %s."
                        % (key, type_signature)
                    )
                row[key] = value
            line = f.readline().strip()

    return pandas.json_normalize(row)
