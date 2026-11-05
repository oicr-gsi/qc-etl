import csv
from typing import Dict, List, Optional

import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import GermlineCoverageUniformityCoverageColumn as CovColumn
from qcetl.column import GermlineCoverageUniformityCnvColumn as CnvColumn

COVERAGE_SECTION = "COVERAGE SUMMARY"
CNV_SECTION = "CNV SUMMARY"

# Metric columns are named after the DRAGEN label, so the label is also the
# lookup key.
COVERAGE_METRICS = [
    CovColumn.UniformityPct02Mean,
    CovColumn.UniformityPct04Mean,
    CovColumn.AverageAutosomalCoverage,
    CovColumn.MedianAutosomalCoverage,
    CovColumn.AlignedReads,
]

CNV_METRICS = [
    CnvColumn.PMAD,
    CnvColumn.CoverageUniformity,
    CnvColumn.NumberOfAmplifications,
    CnvColumn.NumberOfDeletions,
]


def metrics_row(path: str, section: str, metrics: List[str]) -> Dict[str, str]:
    """
    Picks the metrics out of the `SECTION,,label,value[,pct]` rows of a DRAGEN
    metrics CSV. Fields are stripped of surrounding whitespace, and labels not
    in `metrics` are ignored.

    Args:
        path: File path of the DRAGEN metrics CSV
        section: Section (first field) the metrics are in
        metrics: Columns (labels) to extract

    Returns: Column name to string value

    Raises:
        InvalidRecordError: If any of the metrics is missing

    """
    found = {}
    with open(path, newline="") as f:
        for row in csv.reader(f):
            fields = [x.strip() for x in row]
            if len(fields) >= 4 and fields[0] == section:
                found[fields[2]] = fields[3]

    missing = [m for m in metrics if m not in found]
    if missing:
        raise InvalidRecordError(
            "File {} is missing required metrics {}".format(path, missing)
        )
    return {m: found[m] for m in metrics}


def parse_coverage(path: str) -> DataFrame:
    """
    Parses the COVERAGE SUMMARY of a DRAGEN `.wgs_coverage_metrics.csv` file.

    Args:
        path: File path of the `.wgs_coverage_metrics.csv` file

    Returns: DataFrame with a single row

    """
    row = metrics_row(path, COVERAGE_SECTION, COVERAGE_METRICS)
    return DataFrame([row]).apply(pandas.to_numeric)


def parse_cnv(path: Optional[str]) -> DataFrame:
    """
    Parses the CNV SUMMARY of a DRAGEN `.cnv_metrics.csv` file and adds the
    amplification/deletion ratio. The ratio is None when there are no
    deletions.

    Args:
        path: File path of the `.cnv_metrics.csv` file. The CNV output is
            optional, so None returns an empty DataFrame.

    Returns: DataFrame with a single row, or no rows if path is None

    """
    if path is None:
        return DataFrame(
            columns=CNV_METRICS + [CnvColumn.AmplificationDeletionRatio]
        )

    row = metrics_row(path, CNV_SECTION, CNV_METRICS)
    df = DataFrame([row]).apply(pandas.to_numeric)

    amplifications = df.at[0, CnvColumn.NumberOfAmplifications]
    deletions = df.at[0, CnvColumn.NumberOfDeletions]
    df[CnvColumn.AmplificationDeletionRatio] = (
        amplifications / deletions if deletions != 0 else None
    )
    return df
