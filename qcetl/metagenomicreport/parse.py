import pandas


def parse_record(path: str) -> pandas.DataFrame:
    """
    It's a simple TSV file

    Args:
        path: path to report file
    Returns:
        DataFrame
    """
    return pandas.read_csv(path, sep="\t")
