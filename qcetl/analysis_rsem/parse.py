import pandas as pd


def parse_record(file):
    """
    (str) -> pandas dataframe

    Parses statistics for RSEM process from file

    Parameters
    ----------
    - file (str): path file to be parsed

    """
    data = pd.read_csv(file, sep="\t")
    quantiles = [0, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1]

    results = {
        "total": 0,
        "pct_non_zero": 0,
    }

    # total number of transcripts reported
    results["total"] = len(data["TPM"])

    # percentage of transcripts with non-zero value
    results["pct_non_zero"] = len(data[data["TPM"] > 0]) / results["total"]

    # get quantiles for transcripts with non-zero value
    non_zero_tpm_entries = data[data["TPM"] > 0]
    for qt in quantiles:
        results["Q" + str(qt)] = non_zero_tpm_entries["TPM"].quantile(qt)

    df = pd.DataFrame(results, index=[0])
    return df
