import csv
import re
from typing import Dict, List, Optional

import pandas
from pandas import DataFrame

from qcetl.common import InvalidRecordError
from qcetl.column import DragenCoverageUniformityCoverageColumn as CovColumn
from qcetl.column import DragenCoverageUniformityCnvColumn as CnvColumn

COVERAGE_SECTION = "COVERAGE SUMMARY"
CNV_SECTION = "CNV SUMMARY"
SEX_GENOTYPER_SECTION = "SEX GENOTYPER"

# Metric columns are named after the normalized DRAGEN label, so the label is
# also the lookup key. Some lines carry a second value (a percentage), stored
# in the paired PCT column.
COVERAGE_METRICS = [
    CovColumn.AlignedBases,
    CovColumn.AlignedBasesInGenome,
    CovColumn.AverageAlignmentCoverage,
    CovColumn.UniformityPct02Mean,
    CovColumn.UniformityPct04Mean,
    CovColumn.PctCoverage1500xInf,
    CovColumn.PctCoverage1000xInf,
    CovColumn.PctCoverage500xInf,
    CovColumn.PctCoverage100xInf,
    CovColumn.PctCoverage50xInf,
    CovColumn.PctCoverage20xInf,
    CovColumn.PctCoverage15xInf,
    CovColumn.PctCoverage10xInf,
    CovColumn.PctCoverage3xInf,
    CovColumn.PctCoverage1xInf,
    CovColumn.PctCoverage0xInf,
    CovColumn.PctCoverage1000x1500x,
    CovColumn.PctCoverage500x1000x,
    CovColumn.PctCoverage100x500x,
    CovColumn.PctCoverage50x100x,
    CovColumn.PctCoverage20x50x,
    CovColumn.PctCoverage15x20x,
    CovColumn.PctCoverage10x15x,
    CovColumn.PctCoverage3x10x,
    CovColumn.PctCoverage1x3x,
    CovColumn.PctCoverage0x1x,
    CovColumn.MedianChrXCoverage,
    CovColumn.MedianChrYCoverage,
    CovColumn.AverageMitochondrialCoverage,
    CovColumn.AverageAutosomalCoverage,
    CovColumn.MedianAutosomalCoverage,
    CovColumn.MeanMedianAutosomalCoverageRatio,
    CovColumn.AlignedReads,
    CovColumn.AlignedReadsInGenome,
]
COVERAGE_PCT = {
    CovColumn.AlignedBasesInGenome: CovColumn.AlignedBasesInGenomePct,
    CovColumn.AlignedReadsInGenome: CovColumn.AlignedReadsInGenomePct,
}
COVERAGE_REQUIRED = [
    CovColumn.UniformityPct02Mean,
    CovColumn.UniformityPct04Mean,
    CovColumn.AverageAutosomalCoverage,
    CovColumn.MedianAutosomalCoverage,
    CovColumn.AlignedReads,
]

CNV_METRICS = [
    CnvColumn.BasesInReferenceGenome,
    CnvColumn.AverageAlignmentCoverage,
    CnvColumn.NumberOfAlignmentRecords,
    CnvColumn.FilteredRecordsTotal,
    CnvColumn.FilteredRecordsDuplicates,
    CnvColumn.FilteredRecordsMAPQ,
    CnvColumn.FilteredRecordsUnmapped,
    CnvColumn.PMAD,
    CnvColumn.CoverageUniformity,
    CnvColumn.NumberOfTargetIntervals,
    CnvColumn.NumberOfSegments,
    CnvColumn.NumberOfAmplifications,
    CnvColumn.NumberOfDeletions,
    CnvColumn.NumberOfPassingAmplifications,
    CnvColumn.NumberOfPassingDeletions,
]
CNV_PCT = {
    CnvColumn.FilteredRecordsTotal: CnvColumn.FilteredRecordsTotalPct,
    CnvColumn.FilteredRecordsDuplicates: CnvColumn.FilteredRecordsDuplicatesPct,
    CnvColumn.FilteredRecordsMAPQ: CnvColumn.FilteredRecordsMAPQPct,
    CnvColumn.FilteredRecordsUnmapped: CnvColumn.FilteredRecordsUnmappedPct,
    CnvColumn.NumberOfPassingAmplifications: (
        CnvColumn.NumberOfPassingAmplificationsPct
    ),
    CnvColumn.NumberOfPassingDeletions: CnvColumn.NumberOfPassingDeletionsPct,
}
CNV_REQUIRED = [
    CnvColumn.PMAD,
    CnvColumn.CoverageUniformity,
    CnvColumn.NumberOfAmplifications,
    CnvColumn.NumberOfDeletions,
]


def normalize_label(label: str) -> str:
    """
    Collapses runs of whitespace and removes the padding DRAGEN puts inside
    coverage bins, so `[  20x:  50x)` becomes `[20x:50x)`.

    Args:
        label: Metric label as written in the DRAGEN file

    Returns: The normalized label

    """
    label = re.sub(r"\s+", " ", label).strip()
    return re.sub(
        r"\[([^\[\)]*)\)",
        lambda m: "[" + m.group(1).replace(" ", "") + ")",
        label,
    )


def read_sections(path: str) -> Dict[str, List[List[str]]]:
    """
    Groups the rows of a DRAGEN metrics CSV by section (first field), with
    every field stripped of surrounding whitespace.

    Args:
        path: File path of the DRAGEN metrics CSV

    Returns: Section name to the list of its rows

    """
    sections = {}
    with open(path, newline="") as f:
        for row in csv.reader(f):
            fields = [x.strip() for x in row]
            if len(fields) < 4:
                continue
            sections.setdefault(fields[0], []).append(fields)
    return sections


def metrics_row(
    rows: List[List[str]],
    metrics: List[str],
    pct: Dict[str, str],
    required: List[str],
    path: str,
) -> Dict[str, Optional[str]]:
    """
    Picks the expected metrics out of `SECTION,,label,value[,pct]` rows.
    Unknown labels are ignored and missing optional metrics are set to None.

    Args:
        rows: Rows of a single section
        metrics: Columns (normalized labels) to extract
        pct: Metric column to the column holding its second (percent) value
        required: Metrics that must be present
        path: File path, for error messages

    Returns: Column name to string value

    Raises:
        InvalidRecordError: If a required metric is missing

    """
    found = {normalize_label(r[2]): r[3:] for r in rows}
    missing = [m for m in required if m not in found]
    if missing:
        raise InvalidRecordError(
            "File {} is missing required metrics {}".format(path, missing)
        )

    result = {}
    for metric in metrics:
        values = found.get(metric, [])
        result[metric] = values[0] if len(values) > 0 else None
        if metric in pct:
            result[pct[metric]] = values[1] if len(values) > 1 else None
    return result


def parse_coverage(path: str) -> DataFrame:
    """
    Parses the COVERAGE SUMMARY of a DRAGEN `.wgs_coverage_metrics.csv` file.

    Args:
        path: File path of the `.wgs_coverage_metrics.csv` file

    Returns: DataFrame with a single row

    """
    rows = read_sections(path).get(COVERAGE_SECTION, [])
    row = metrics_row(
        rows, COVERAGE_METRICS, COVERAGE_PCT, COVERAGE_REQUIRED, path
    )
    return DataFrame([row]).apply(pandas.to_numeric)


def parse_cnv(path: Optional[str]) -> DataFrame:
    """
    Parses the SEX GENOTYPER and CNV SUMMARY sections of a DRAGEN
    `.cnv_metrics.csv` file and adds the amplification/deletion ratio. The
    ratio is None when there are no deletions.

    Args:
        path: File path of the `.cnv_metrics.csv` file. The CNV output is
            optional, so None returns an empty DataFrame.

    Returns: DataFrame with a single row, or no rows if path is None

    """
    if path is None:
        columns = [
            CnvColumn.SexGenotyperSample,
            CnvColumn.SexGenotyperKaryotype,
        ]
        columns += [CnvColumn.SexGenotyperConfidence]
        columns += CNV_METRICS + list(CNV_PCT.values())
        columns += [CnvColumn.AmplificationDeletionRatio]
        return DataFrame(columns=columns)

    sections = read_sections(path)
    rows = sections.get(CNV_SECTION, [])
    row = metrics_row(rows, CNV_METRICS, CNV_PCT, CNV_REQUIRED, path)
    df = DataFrame([row]).apply(pandas.to_numeric)

    amplifications = df.at[0, CnvColumn.NumberOfAmplifications]
    deletions = df.at[0, CnvColumn.NumberOfDeletions]
    df[CnvColumn.AmplificationDeletionRatio] = (
        amplifications / deletions if deletions != 0 else None
    )

    # SEX GENOTYPER,,sample,karyotype,confidence
    sex = sections.get(SEX_GENOTYPER_SECTION, [[]])[0]
    sex = sex + [None] * (5 - len(sex))
    df[CnvColumn.SexGenotyperSample] = sex[2]
    df[CnvColumn.SexGenotyperKaryotype] = sex[3]
    df[CnvColumn.SexGenotyperConfidence] = float(sex[4]) if sex[4] else None
    return df
