import logging
import pandas
from pandas import DataFrame

from qcetl.column import SamtoolsStatsV112Column as Column

FLOAT_COLUMNS = {
    Column.ErrorRate,
    Column.AverageLength,
    Column.AverageFirstFragmentLength,
    Column.AverageLastFragmentLength,
    Column.AverageQuality,
    Column.InsertSizeAverage,
    Column.InsertSizeStandardDeviation,
    Column.PercentageOfProperlyPairedReads,
    Column.PercentageTargetsWithCoverage,
}
logger = logging.getLogger(__name__)


def parse_sn(path: str) -> DataFrame:
    """
    Parse the SN fields of samtools stats

    Args:
        path: Path to file

    Returns: Single row DataFrame

    """
    # Borrowed from MultiQC
    # https://github.com/ewels/MultiQC/blob/master/multiqc/modules/samtools/stats.py#L15
    with open(path, "r") as f:
        parsed_data = dict()
        for line in f:
            if not line.startswith("SN"):
                continue
            sections = line.split("\t")
            field = sections[1].strip()[:-1]
            #
            value = sections[2].strip()
            value = float(value) if field in FLOAT_COLUMNS else int(value)
            parsed_data[field] = value

    return pandas.json_normalize(parsed_data)
