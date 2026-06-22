"""
Sequenza parsing module

"""

import re
import zipfile

import pandas
from pandas import DataFrame


from qcetl.column import SequenzaColumn


def parse_record(path: str) -> DataFrame:
    """
    Generate a DataFrame for a Sequenza record:
    - Parse alternative_solutions.txt files from the zip file
    - Ignore alternative_solutions.txt files in sol folders
    - Add the gamma folder name to the parsed data

    Args:
        path: path to the zip file
    Returns:
        DataFrame
    """

    with zipfile.ZipFile(path) as sequenza_zip:
        results = []
        zipcontents = sequenza_zip.namelist()
        r = re.compile(r"^gammas/(\d+)/.*alternative_solutions\.txt")
        for z in zipcontents:
            s = re.search(
                r, z
            )  # s[0] is the full string and s[1] is the gamma value
            if s is not None and "/sol" not in s[0]:
                with sequenza_zip.open(s[0]) as f:
                    df = pandas.read_csv(f, delimiter="\t")
                    df["gamma"] = s[1]
                    results.append(df)

        if len(results) == 0:
            return pandas.DataFrame(
                columns=[
                    SequenzaColumn.Gamma,
                    SequenzaColumn.Cellularity,
                    SequenzaColumn.Ploidy,
                    SequenzaColumn.SLPP,
                ]
            )
        else:
            return pandas.concat(results)
