import logging
import pandas
from typing import Tuple, Optional

from qcetl.common import InvalidRecordError

logger = logging.getLogger(__name__)


def parse_line(line: str) -> Optional[Tuple[str, int, Optional[float]]]:
    """
    Convert a single record line into a parsed tuple

    Args:
        line: A line from the bwamem record

    Returns: The first element is the name of the record, the second element is the
        metric, and the third element is the optional percentage of the metric

    """
    split = line.split(":")

    if len(split) < 2:
        return None
    elif len(split) > 2:
        raise InvalidRecordError(
            "Line had more than one : separator: {}".format(line)
        )

    name = split[0].strip()
    metrics = split[1].strip().split()
    metric = int(metrics[0])

    percentage = metrics[-1]
    if percentage.endswith("%)"):
        percentage = float(percentage[1:-2])
    else:
        percentage = None

    return name, metric, percentage


def parse_record(path: str) -> pandas.DataFrame:
    """
    Convert bwamem record into dictionary

    Args:
        path: File path to record to parse

    Returns: Extracts each metric and its associated percentage.

    """
    record = {}
    # Read 1 and Read 2 fields are used repeatedly. The parent variable is the field
    # under which they are nested
    parent = ""

    with open(path, "r") as f:
        for line in f:
            parsed = parse_line(line)

            if parsed is None:
                continue
            else:
                name, metric, percentage = parsed

            if name == "Read 1" or name == "Read 2":
                name = parent + " " + name
            else:
                parent = name

            record[name] = metric

            if percentage is not None:
                record[name + " percentage"] = percentage

    return pandas.json_normalize(record)
