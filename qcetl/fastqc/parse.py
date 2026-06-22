import logging
from typing import Dict, Any

import crimson.fastqc
import numpy
import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import FastqcColumn as Column

logger = logging.getLogger(__name__)


def convert_fastqc_to_json(path: str) -> Dict[str, Any]:
    """
    Uses the crimson package to convert a zipped FastQC file to JSON

    Args:
        path: File path of FastQC file

    Returns:

    Raises:
        InvalidRecordError: If file cannot be parsed

    """
    try:
        return crimson.fastqc.parse(path)
    except UnicodeDecodeError as e:
        raise InvalidRecordError(
            "File {} has invalid encoding: {}".format(path, e)
        ) from e
    except AttributeError as e:
        raise InvalidRecordError(
            "File {} lacks expected FastQC fields: {}".format(path, e)
        ) from e


def parse_record(path: str) -> DataFrame:
    """
    Converts a zipped fastqc record into a single row DataFrame

    Only the `Basic Statistics` and `version` keys are completely parsed.
    For all other fields, only the status is extracted.

    Args:
        path: File path to FastQC output

    Returns: Single row DataFrame

    Raises:
        InvalidRecordError: If the DataFrame does not produce 1 row

    """
    record = convert_fastqc_to_json(path)
    result = dict()
    result["version"] = record["version"]

    for k in record:
        # The version field does not contain a nested dictionary with status
        if k != "version":
            new_k = "Status " + k
            status = record[k]["status"]
            result[new_k] = status

    # Python's way of combining two dictionaries
    result = {**record["Basic Statistics"]["contents"], **result}
    del result["Filename"]

    # If Sequence length is a range, split into a second column
    if isinstance(result[Column.SequenceLength], str):
        l, max_l = result[Column.SequenceLength].split("-")
        result[Column.SequenceLength] = int(l)
        result[Column.SequenceLengthMax] = int(max_l)

    for col in [
        Column.FilteredSequences,
        Column.SequenceLengthMax,
        Column.StatusBasicStatistics,
        Column.StatusKmerContent,
        Column.StatusOverrepresentedSequences,
        Column.StatusPerBaseGCContent,
        Column.StatusPerBaseNContent,
        Column.StatusPerBaseSequenceContent,
        Column.StatusPerBaseSequenceQuality,
        Column.StatusPerSequenceGCContent,
        Column.StatusPerSequenceQualityScores,
        Column.StatusSequenceDuplicationLevels,
        Column.StatusSequenceLengthDistribution,
    ]:
        if col not in result:
            result[col] = numpy.nan

    df = pandas.DataFrame.from_records([result])

    if len(df) != 1:
        raise InvalidRecordError(
            "Expected 1 row for parsed DataFrame {}".format(result)
        )

    return df
