import csv
import pandas as pd
import numpy as np
from pandas import DataFrame
from qcetl.column import AnalysisMrdColumn as MrdColumn
from qcetl.common import InvalidRecordError


def parse_record(mrd_txt_file: str) -> DataFrame:
    """
    (str) -> pandas dataframe

    Selects metrics for mrdetect from .mrdetect.txt input file

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
    with open(mrd_txt_file, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        mrd_input_data = [row for row in reader]
        if not mrd_input_data:
            raise InvalidRecordError("File is empty or only contains headers")

    columns = [
        MrdColumn.SampleName,
        MrdColumn.SampleCoverage,
        MrdColumn.MedianVAF,
        MrdColumn.SampleSNPs,
        MrdColumn.SitesDetected,
        MrdColumn.MeanNoise,
        MrdColumn.DetectionRate,
        MrdColumn.TumourFractionEstimate,
        MrdColumn.TumourFractionAdjusted,
        MrdColumn.ZScore,
        MrdColumn.PValue,
        MrdColumn.DatasetDetectionCutoff,
        MrdColumn.FalsePositiveRate,
        MrdColumn.CancerDetected,
    ]
    result = {column: [] for column in columns}

    for row in mrd_input_data:
        for column in result.keys():
            try:
                result[column].append(row[column])
            except KeyError:
                raise InvalidRecordError(
                    f"Column {column} not found in the input file."
                )

    mrd_df = pd.DataFrame(result)
    mrd_df.columns = columns
    mrd_df["cancer_detected"] = (
        mrd_df["cancer_detected"]
        .str.strip()
        .str.upper()
        .map(
            {
                "TRUE": True,
                "FALSE": False,
            }
        )
        .astype(bool)
    )

    return mrd_df
