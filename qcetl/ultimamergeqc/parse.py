import pandas as pd

from qcetl.column import UltimaMergeQcColumn as Column
from qcetl.common import InvalidRecordError


ALN_COLUMNS = [
    Column.Category,
    Column.TotalReads,
    Column.PfReads,
    Column.PercentPFReads,
    Column.PfNoiseReads,
    Column.PfReadsAligned,
    Column.PercentPFReadsAligned,
    Column.PfAlignedBases,
    Column.PfHqAlignedReads,
    Column.PfHqAlignedBases,
    Column.PfHqAlignedQ20Bases,
    Column.PfHqMedianMismatches,
    Column.PfMismatchRate,
    Column.PfHqErrorRate,
    Column.PfIndelRate,
    Column.MeanReadLength,
    Column.SdReadLength,
    Column.MedianReadLength,
    Column.MadReadLength,
    Column.MinReadLength,
    Column.MaxReadLength,
    Column.MeanAlignedReadLength,
    Column.ReadsAlignedInPairs,
    Column.PercentReadsAlignedInPairs,
    Column.PfReadsImproperPairs,
    Column.PercentPfReadsImproperPairs,
    Column.BadCycles,
    Column.StrandBalance,
    Column.PercentChimeras,
    Column.PercentAdapter,
    Column.PercentSoftclip,
    Column.PercentHardclip,
    Column.AvgPos3PrimeSoftclipLength,
]

DUP_COLUMNS = [
    Column.Library,
    Column.UnpairedReadsExamined,
    Column.ReadPairsExamined,
    Column.SecondaryOrSupplementaryReads,
    Column.UnmappedReads,
    Column.UnpairedReadDuplicates,
    Column.ReadPairDuplicates,
    Column.ReadPairOpticalDuplicates,
    Column.PercentDuplication,
]

WGS_COLUMNS = [
    Column.GenomeTerritory,
    Column.MeanCoverage,
    Column.SdCoverage,
    Column.MedianCoverage,
    Column.MadCoverage,
    Column.PercentExcAdapter,
    Column.PercentExcMapq,
    Column.PercentExcDupe,
    Column.PercentExcUnpaired,
    Column.PercentExcBaseq,
    Column.PercentExcOverlap,
    Column.PercentExcCapped,
    Column.PercentExcTotal,
    Column.Percent1X,
    Column.Percent5X,
    Column.Percent10X,
    Column.Percent15X,
    Column.Percent20X,
    Column.Percent25X,
    Column.Percent30X,
    Column.Percent40X,
    Column.Percent50X,
    Column.Percent60X,
    Column.Percent70X,
    Column.Percent80X,
    Column.Percent90X,
    Column.Percent100X,
    Column.Fold80BasePenalty,
    Column.Fold90BasePenalty,
    Column.Fold95BasePenalty,
    Column.HetSnpSensitivity,
    Column.HetSnpQ,
]

# Values Picard writes when a metric can't be calculated
MISSING_VALUES = ("", "?")


def read_picard_metrics(path):
    """
    (str) -> list of dicts

    Reads the METRICS CLASS section of an input metrics file.

    Parameters
    ----------
    - path (str): path to the metrics file

    Returns
    -------
    - list of rows, each a dict of {column name: value}
    - raises InvalidRecordError if there is no METRICS CLASS section or no data rows
    """
    with open(path, "r") as f:
        for line in f:
            if line.startswith("## METRICS CLASS"):
                break
        else:
            raise InvalidRecordError(f"No METRICS CLASS section found in {path}")

        header = next(f, "").rstrip("\r\n").split("\t")
        rows = []
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip() or line.startswith("#"):
                break
            rows.append(dict(zip(header, line.split("\t"))))

    if not rows:
        raise InvalidRecordError(f"File {path} contains headers but no metrics")
    return rows


def convert_value(value, column, column_type, path):
    """
    Converts a value to the type given in the cache schema:
    "s" = string, "i" = int, "f" = float.
    A "q" prefix (e.g. "qf") means the value may be missing and is stored as None.

    Raises InvalidRecordError if a required value is missing or can't be converted.
    """
    value = value.strip()
    if value in MISSING_VALUES:
        if column_type.startswith("q"):
            return None
        raise InvalidRecordError(f"Missing value for {column} in {path}")

    base_type = column_type.lstrip("q")
    try:
        if base_type == "s":
            return value
        if base_type == "i":
            return int(value)
        if base_type == "f":
            return float(value)
    except ValueError:
        raise InvalidRecordError(
            f"Value '{value}' for {column} in {path} is not of type {column_type}"
        )
    raise InvalidRecordError(f"Unsupported type '{column_type}' for {column}")


def extract_columns(row, columns, schema, path):
    """
    Selects the required columns from a metrics row and converts each value
    to the type given in the schema.

    Raises InvalidRecordError if a required column is missing.
    """
    result = {}
    for column in columns:
        try:
            value = row[column]
        except KeyError:
            raise InvalidRecordError(f"Column {column} not found in {path}.")
        result[column] = convert_value(value, column, schema[column], path)
    return result


def parse_record(alignment_summary_file, duplicate_metrics_file, wgs_metrics_file, schema):
    """
    (str, str, str, dict) -> pandas dataframe

    Selects Ultima merge QC metrics from Picard alignment summary,
    duplicate and WGS metrics files

    Parameters
    ----------
    - alignment_summary_file (str): path to .alignment_summary_metrics
    - duplicate_metrics_file (str): path to .duplicate_metrics
    - wgs_metrics_file (str): path to .wgs_metrics.txt
    - schema (dict): {column: type code} from the cache's schema_versions

    Returns
    -------
    - single-row pandas dataframe with merged sample metrics
    - raises InvalidRecordError if a file is empty, malformed, or missing a required column
    """
    aln_row = read_picard_metrics(alignment_summary_file)[0]
    dup_row = read_picard_metrics(duplicate_metrics_file)[0]
    wgs_row = read_picard_metrics(wgs_metrics_file)[0]

    record = {}
    record.update(extract_columns(aln_row, ALN_COLUMNS, schema, alignment_summary_file))
    record.update(extract_columns(dup_row, DUP_COLUMNS, schema, duplicate_metrics_file))
    record.update(extract_columns(wgs_row, WGS_COLUMNS, schema, wgs_metrics_file))

    return pd.DataFrame([record], columns=ALN_COLUMNS + DUP_COLUMNS + WGS_COLUMNS)