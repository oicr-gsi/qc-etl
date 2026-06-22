import pandas as pd

# index of the columns for VCF files, see
# VCF specs for column order
FILTER = 6
ID = 2


def parse_record(file):
    """
    (str) -> pandas dataframe

    Selects statistics for delly process from file

    Parameters
    ----------
    - file (str): path to file to be parsed

    """
    structural_variant_types = ["BND", "DEL", "DUP", "INS", "INV"]

    results = {
        "num_calls": 0,
        "num_PASS": 0,
        # the following stats are for PASS calls only
        "num_BND": 0,
        "num_DEL": 0,
        "num_DUP": 0,
        "num_INS": 0,
        "num_INV": 0,
    }

    chunksize = 5 * 10**4

    # it is possible the csv only contains the header
    try:
        data = pd.read_csv(
            file,
            sep="\t",
            comment="#",
            header=None,  # No headers, instead use VCF column indices
            chunksize=chunksize,
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame(results, index=[0])

    for sub_df in data:
        # num_calls = the number of vcf records, including PASS and
        # non-PASS calls
        results["num_calls"] = results["num_calls"] + len(sub_df)

        # num_PASS = the number of vcf records where the FILTER field is
        # marked as PASS
        results["num_PASS"] = results["num_PASS"] + len(
            sub_df[sub_df[FILTER] == "PASS"]
        )

        # count the number of PASS calls for each structural variant type in
        # structural_variant_types
        for type in structural_variant_types:
            results[f"num_{type}"] = results[f"num_{type}"] + len(
                sub_df[
                    (sub_df[FILTER] == "PASS") & sub_df[ID].str.startswith(type)
                ]
            )

    df = pd.DataFrame(results, index=[0])
    return df
