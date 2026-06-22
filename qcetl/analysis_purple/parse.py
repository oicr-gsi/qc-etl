import csv
import pandas as pd
import numpy as np
from pandas import DataFrame
from qcetl.column import AnalysisPurpleColumn as PurpleColumn
from qcetl.common import InvalidRecordError


def parse_purity_file(purity_tsv_file: str) -> DataFrame:
    """
    (str) -> pandas dataframe

    Selects metrics for purple from purple_purity.tsv input file

    Parameters
    ----------
    - file (str): path to file to be parsed

    Returns
    -------
    - pandas dataframe with purple metrics
    - raises InvalidRecordError if the file is empty or only contains headers
    - raises InvalidRecordError if a required column is missing
    """
    # Read purple purity input tsv and making a dataframe
    with open(purity_tsv_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        purple_input_data = [row for row in reader]
        if not purple_input_data:
            raise InvalidRecordError("File is empty or only contains headers")

    columns = [
        PurpleColumn.Score,
        PurpleColumn.Purity,
        PurpleColumn.MinPurity,
        PurpleColumn.MaxPurity,
        PurpleColumn.Ploidy,
        PurpleColumn.MinPloidy,
        PurpleColumn.MaxPloidy,
        PurpleColumn.DiploidProportion,
        PurpleColumn.MinDiploidProportion,
        PurpleColumn.MaxDiploidProportion,
        PurpleColumn.PolyclonalProportion,
        PurpleColumn.Status,
        PurpleColumn.WholeGenomeDuplication,
        PurpleColumn.msStatus,
        PurpleColumn.Tml,
        PurpleColumn.TmlStatus,
        PurpleColumn.TmbPerMb,
        PurpleColumn.TmbStatus,
    ]
    result = {column: [] for column in columns}

    for row in purple_input_data:
        for column in result.keys():
            try:
                result[column].append(row[column])
            except KeyError:
                raise InvalidRecordError(
                    f"Column {column} not found in the input file."
                )

    purple_df = pd.DataFrame(result)
    purple_df.columns = columns

    return purple_df


def get_pga(purity_tsv_file: str, cnv_somatic_file: str) -> DataFrame:
    """
    (str, str) -> pandas dataframe

    Calculates the Percentage of Genome Altered (PGA) from purple_purity.tsv and purple_cnv_somatic.tsv files and adds the metric to the purple dataframe.

    Parameters
    ----------
    - cnv_somatic_file (str): path to file to be parsed
    - purity_tsv_file (str): path to file to be parsed

    Returns
    -------
    - pandas dataframe with the Percentage of Genome Altered (PGA) metric added
    """
    purple_df = parse_purity_file(purity_tsv_file)
    numeric_col = [
        PurpleColumn.Purity,
        PurpleColumn.Ploidy,
    ]
    for col in numeric_col:
        purple_df[col] = pd.to_numeric(purple_df[col], errors="coerce")

    purity = purple_df[PurpleColumn.Purity].values[0]
    ploidy = purple_df[PurpleColumn.Ploidy].values[0]

    MINIMUM_MAGNITUDE_SEG_MEAN = 0.2
    GENOME_SIZE = 3095978931  # comes from https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38.p12. Non-N bases.

    with open(cnv_somatic_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        cnv_rows = [row for row in reader]
        if not cnv_rows:
            raise InvalidRecordError("File is empty or only contains headers")

    cnv_data = pd.DataFrame(cnv_rows)

    # Convert columns to appropriate types
    cnv_data["chromosome"] = cnv_data["chromosome"].astype(str)
    cnv_data["start"] = cnv_data["start"].astype(int)
    cnv_data["end"] = cnv_data["end"].astype(int)
    cnv_data["copyNumber"] = cnv_data["copyNumber"].astype(float)
    cnv_data["bafCount"] = cnv_data["bafCount"].astype(int)

    cnv_data["seg_mean"] = np.log2(
        1 + (purity * (cnv_data["copyNumber"] - ploidy) / ploidy)
    )
    cnv_data = cnv_data[
        cnv_data["seg_mean"].abs() >= MINIMUM_MAGNITUDE_SEG_MEAN
    ].copy()

    # Calculate length of altered segments
    cnv_data["seg_length"] = cnv_data["end"] - cnv_data["start"]

    # Compute FGA
    total_alt_bases = cnv_data["seg_length"].sum()
    fga = total_alt_bases / GENOME_SIZE

    # Compute PGA
    purple_df[PurpleColumn.Pga] = int(round(fga * 100, 0))

    return purple_df


def get_qc_metrics(purity_tsv_file, cnv_somatic_file, qc_file):
    purple_df = get_pga(purity_tsv_file, cnv_somatic_file)

    qc_val = {}
    with open(qc_file, "r") as f:
        for line in f:
            if line.strip() == "":
                continue
            key, value = line.strip().split("\t")
            qc_val[key] = value

    try:
        purple_df[PurpleColumn.QCStatus] = qc_val.get("QCStatus", None)
        purple_df[PurpleColumn.CopyNumberSegments] = int(
            qc_val.get("CopyNumberSegments", 0)
        )
        purple_df[PurpleColumn.Contamination] = float(
            qc_val.get("Contamination", np.nan)
        )
    except ValueError as e:
        raise InvalidRecordError(f"Error parsing QC file values: {e}")

    return purple_df


def parse_record(purity_tsv_file, cnv_somatic_file, qc_file):
    return get_qc_metrics(purity_tsv_file, cnv_somatic_file, qc_file)
