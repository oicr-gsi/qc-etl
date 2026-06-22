import csv
import pandas as pd
import numpy as np
from pandas import DataFrame
from qcetl.column import BiomodalQcColumn
from qcetl.common import InvalidRecordError


def parse_record(biomodalqc_csv: str) -> DataFrame:
    try:
        with open(biomodalqc_csv, "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            # Assuming there's only one row of data
            data_row = next(reader)
            if not data_row:
                raise InvalidRecordError(
                    "File is empty or only contains headers"
                )

    except InvalidRecordError as e:
        print(f"Invalid Record Error: {e}")
        raise

    metrics_columns = [
        "pmkd_genome_percent_duplication",
        "dqs_lambda_modc_perc",
        "dqs_puc19_modc_perc",
        "dqs_ss_sq2hmc_mc_perc",
        "dqs_ss_sq2hmc_hmc_perc",
        "fastqc_raw_total_sequences",
    ]

    metrics_row = {
        key: (
            float(data_row[key])
            if key in data_row and data_row[key] not in ("", None)
            else np.nan
        )
        for key in metrics_columns
    }

    biomodalqc_df = pd.DataFrame(
        {
            BiomodalQcColumn.DuplicationRate: metrics_row[
                "pmkd_genome_percent_duplication"
            ],
            BiomodalQcColumn.LambdaMethylationModC: metrics_row[
                "dqs_lambda_modc_perc"
            ],
            BiomodalQcColumn.PUC19MethylationModC: metrics_row[
                "dqs_puc19_modc_perc"
            ],
            BiomodalQcColumn.Sq2hmcMethylation5mC: metrics_row[
                "dqs_ss_sq2hmc_mc_perc"
            ],
            BiomodalQcColumn.Sq2hmcMethylation5hmC: metrics_row[
                "dqs_ss_sq2hmc_hmc_perc"
            ],
            BiomodalQcColumn.TotalClusters: metrics_row[
                "fastqc_raw_total_sequences"
            ],
        },
        index=[0],
    )

    return biomodalqc_df
