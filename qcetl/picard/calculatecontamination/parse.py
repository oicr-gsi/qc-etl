import pandas


def parse_record(path: str) -> pandas.DataFrame:
    return pandas.read_csv(path, sep="\t")
