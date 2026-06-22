import pandas as pd


def parse_record(file):
    """
    (str) -> pandas dataframe

    Selects statistics for starfusion process from file

    Parameters
    ----------
    - file (str): path to file to be parsed

    """

    data = pd.read_csv(file, sep="\t")
    results = {"num_records": len(data)}

    df = pd.DataFrame(results, index=[0])
    return df
