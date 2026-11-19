from typing import Dict

import os
import numpy as np
import pandas as pd

from qcetl.common import InvalidRecordError
from qcetl.column import ICAMetricsColumn as Column
from qcetl.icametrics.constants import (
    row_in_csv,
    read_from_val,
    optional_files,
)
from qcetl.icametrics.utility import (
    calculate_mean_cov,
    calculate_dup_del_ratio,
    check_sex_match,
    to_float,
)


def parse_csv(filename: str) -> Dict:
    """
    Parse selected metric rows from a CSV file into a dictionary.

    The CSV is expected to contain up to five columns:
    summary_type, sample, key, val, and val_extra.

    The file type is determined by matching a key from `row_in_csv`
    against the input filename. For the matched file type, only rows
    whose `key` column matches entries in `row_in_csv[filetype]`
    are extracted.

    For `mapping_metrics` files:
    - rows with a non-empty `sample` column are skipped
    - values are read from the `val_extra` (percentage) column, except for
      the keys in `read_from_val`, which are read from the `val` column

    For all other file types:
    - values are read from the `val` column

    DRAGEN writes `NA` for metrics it could not calculate (e.g. sample
    contamination when contamination estimation is not enabled); these
    are returned as NaN.

    Args:
        filename: Path to the metrics CSV file

    Return:
        dictionary containing whose header values (from the third column) are listed in `row_in_csv`
    """
    columns = ["summary_type", "sample", "key", "val", "val_extra"]
    df = pd.read_csv(
        filename, header=None, names=columns, keep_default_na=False
    )
    for filetype in row_in_csv:
        if filetype in filename:
            break

    result_dict = {}
    read_val = "val_extra" if filetype == "mapping_metrics" else "val"
    row_keys = row_in_csv[filetype]
    for _, row in df.iterrows():
        for key in row_keys:
            if filetype == "mapping_metrics" and row["sample"] != "":
                continue
            if key in row["key"]:
                if key == "Mapped reads" and row["key"] != "Mapped reads":
                    continue
                value = row[read_val if key not in read_from_val else "val"]
                result_dict[row["key"]] = np.nan if value == "NA" else value
                break

    return result_dict


def load_sample_data(run: str, de_id: str, ica_dir: str) -> Dict:
    """
    Load and combine raw metrics data for a sample from CSV files.

    This function searches for CSV metric files matching each file type
    defined in `row_in_csv`, parses the relevant rows using `parse_csv`,
    and combines the extracted metrics into a single dictionary.

    The search includes:
    - DragenGermline output directories
    - Sample-specific directories under `ica_dir`

    Returns:
        Dictionary containing raw metric values extracted from all
    matching CSV files for the sample.

    Raises:
        InvalidRecordError: if a required metrics CSV file is missing except CNV metrics
    """
    result_dict = {
        Column.MeanCovFull: calculate_mean_cov(ica_dir, de_id, "full"),
        Column.MeanCovSub: calculate_mean_cov(ica_dir, de_id),
        Column.FailedRegionFull: calculate_mean_cov(
            ica_dir, de_id, "full", fail=True
        ),
        Column.FailedRegionSub: calculate_mean_cov(ica_dir, de_id, fail=True),
    }
    for filetype in row_in_csv:
        filename = "{}.{}.csv".format(de_id, filetype)
        filepath = os.path.join(ica_dir, filename)
        if not os.path.isfile(filepath):
            if filetype in optional_files:
                continue
            raise InvalidRecordError(
                "Missing {} file: {}".format(filetype, filepath)
            )
        result_dict |= parse_csv(filepath)
    return result_dict


def process_sample_data(data: Dict, de_id: str, sex: str) -> pd.DataFrame:
    """
    Process raw sample metrics into a structured summary dictionary.

    This function performs additional metric calculations and QC checks
    on the input sample data, then organizes selected values into a
    standardized report-ready structure grouped by metric category.

    Processing steps include:
    - calculating duplication/deletion ratio
    - validating observed ploidy against expected sex

    The resulting dictionary contains formatted metrics from:
    - WGS coverage metrics
    - Ploidy estimation metrics
    - Mapping metrics
    - GVCF metrics
    - CNV metrics

    Args:
        data: Dictionary containing raw extracted sample metrics

    Returns:
        Dictionary mapping the sample name to a structured summary
        of processed metrics and QC results.
    """
    calculate_dup_del_ratio(data)
    total_reads = to_float(data.get("Total input reads"))
    observed_sex = data.get("Ploidy estimation", "Unknown")
    result = {
        # Column.PineryLimsID: pinery_lims_id,
        # Column.Run: run,
        Column.DeID: de_id,
        Column.MeanCovGenome: data.get(
            "Average alignment coverage over genome", np.nan
        ),
        Column.MeanCovFull: data.get(Column.MeanCovFull, np.nan),
        Column.MeanCovSub: data.get(Column.MeanCovSub, np.nan),
        Column.FailedRegionFull: data.get(Column.FailedRegionFull, np.nan),
        Column.FailedRegionSub: data.get(Column.FailedRegionSub, np.nan),
        Column.PctGenome: data.get(
            "PCT of genome with coverage [  20x: inf)", np.nan
        ),
        Column.UniCov: data.get(
            "Uniformity of coverage (PCT > 0.2*mean) over genome", np.nan
        ),
        Column.ObsSex: observed_sex,
        Column.Sex: sex,
        Column.SexMatch: check_sex_match(
            sex, data.get("Ploidy estimation", np.nan)
        ),
        Column.TotalReads: total_reads,
        Column.TotalClusters: total_reads / 2, # paired-end
        Column.PctMapped: data.get("Mapped reads", np.nan),
        Column.PctUnique: data.get(
            "Number of unique reads (excl. duplicate marked reads)", np.nan
        ),
        Column.PctDuplicate: data.get(
            "Number of duplicate marked reads", np.nan
        ),
        Column.PctContamination: data.get(
            "Estimated sample contamination", np.nan
        ),
        Column.MeanInsertLength: data.get("Insert length: mean", np.nan),
        Column.MedInsertLength: data.get("Insert length: median", np.nan),
        Column.TiTvRatio: data.get("Ti/Tv ratio", np.nan),
        Column.PctAutosome: data.get("Percent Autosome Callability", np.nan),
        Column.CovUni: data.get("Coverage uniformity", np.nan),
        Column.DupDelRatio: data.get("dupdelratio", np.nan),
    }
    row = pd.DataFrame.from_records([result])
    return row


def parse_record(run: str, de_id: str, sex: str, ica_dir: str) -> pd.DataFrame:
    data = load_sample_data(run, de_id, ica_dir)
    return process_sample_data(data, de_id, sex)
