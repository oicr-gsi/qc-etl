import logging
from typing import Dict, Tuple
from collections import OrderedDict
import numpy
import pandas
import pandas.errors
from pandas import DataFrame
import json

from qcetl.common import InvalidRecordError
from qcetl.bamqc4.parse import parse_record as parse_bamQC

logger = logging.getLogger(__name__)


def parse_main_matrics(path: str, schema: Dict[str, str]) -> DataFrame:
    """
    Parse main metrics, including metrics from best solution from params.txt

    """

    row = {}
    for column in schema.keys():
        row[column] = numpy.nan

    with open(path, "r") as f:
        f.readline()  # Discard header
        sample = f.readline().split("\t")[0]
        line = f.readline().strip()
        # skip blank lines
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


def parse_solution_table(path: str, schema: Dict[str, str]) -> DataFrame:
    """
    Parse solution table, metrics of alternate solutions from params.txt

    """
    schema = OrderedDict(schema)
    rows = []

    with open(path, "r") as f:
        for line in f:
            line = line.rstrip().split("\t")
            if len(line) > 5 and line[0] != "init":
                tumor_fraction = line[2]
                line.insert(1, tumor_fraction)
                ploidy = round(1 - float(line[2]), 3)
                line.insert(2, ploidy)
                row = {}
                for idx, key in enumerate(schema.keys()):
                    type_signature = schema[key]
                    if type_signature == "i":
                        row[key] = int(line[idx])
                    elif type_signature == "f":
                        if line[idx] == "NA":
                            row[key] = numpy.nan
                        else:
                            row[key] = float(line[idx])
                    elif type_signature == "s":
                        row[key] = line[idx]
                    else:
                        raise InvalidRecordError(
                            "Cannot convert column %s with type %s."
                            % (key, type_signature)
                        )
                rows.append(row)

    return pandas.json_normalize(rows)


def parse_record(
    path: str,
    bamQC_path: str,
    main_schema: Dict[str, str],
    sol_schema: Dict[str, str],
) -> Tuple[DataFrame, DataFrame, DataFrame]:
    """
    Combine IchorCNA data into three DataFrames

    Args:
        path: File path to input params.txt file
        bamQC_path: File path to input bamQC metrics
        main_schema: Type annotation for columns for main metrics table,
        sol_schema: Columns and their types for solution table

    Returns: Tree Dataframes of main metrics, alternate solution table and bamQC metrics

    """
    main_table = parse_main_matrics(path, main_schema)
    solution_table = parse_solution_table(path, sol_schema)
    with open(bamQC_path, "r") as f:
        bamMetrics = json.load(f)
        bamqc_version = [
            int(x) for x in bamMetrics["workflow version"].split(".")
        ]
    bamQC_table = parse_bamQC(bamQC_path, bamqc_version)
    return (main_table, solution_table, bamQC_table)
