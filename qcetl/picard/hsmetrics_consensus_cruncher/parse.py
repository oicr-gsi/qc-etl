import io
import logging
import numpy
import pandas
from pandas import DataFrame
from typing import Tuple

from qcetl.common import InvalidRecordError

logger = logging.getLogger(__name__)


def parse_record(
    path: str,
) -> Tuple[DataFrame, DataFrame]:
    """
    Covert Picard record into a DataFrame and add necessary metadata

    Args:
        path: Path to Picard file

    Returns: Metrics data (first element) and histogram data (second element)

    """
    section = None
    metrics = ""
    histogram = ""

    with open(path, "r") as f:
        for line in f:
            if line.startswith("## METRICS CLASS"):
                section = "metrics"
            elif line.startswith("## HISTOGRAM"):
                section = "histogram"
            elif section is None:
                continue
            elif not line.strip():
                section = None
            elif section == "metrics":
                metrics += line
            elif section == "histogram":
                histogram += line
            else:
                raise InvalidRecordError(
                    "Unexpected line in {}: {}".format(path, line)
                )

        dfs = (
            pandas.read_csv(io.StringIO(metrics), sep="\t").replace(
                "?", numpy.nan
            ),
            pandas.read_csv(io.StringIO(histogram), sep="\t"),
        )
        # Some consensus_cruncher workflow output hsmetrics files missing "MIN_TARGET_COVERAGE" column
        if "MIN_TARGET_COVERAGE" not in dfs[0]:
            # If mising, add it with value None
            dfs[0]["MIN_TARGET_COVERAGE"] = None

        return dfs
