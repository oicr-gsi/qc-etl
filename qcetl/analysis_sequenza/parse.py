import json
import pandas as pd
import zipfile
import re


def add_gamma_col(gamma, data):
    """
    (int, dict) -> pandas dataframe

    Assigns each row in the data a 'gamma' attribute with value = gamma

    Parameters
    ----------
    - gamma (int): gamma value to give corresponding data
    - data (dict): data to be altered (a dictionary of columns)

    """
    df = pd.DataFrame(data)
    df["gamma"] = gamma
    df["index"] = df.index
    return df


def parse_alt_soln(file):
    """
    (str) -> pandas dataframe

    Parses alternative_solutions.json for sequenza

    Parameters
    ----------
    - file (str): path to alternative_solutions.json file to be parsed

    """
    data = {}
    with open(file) as f:
        data = json.load(f)
    dfs = [add_gamma_col(k, v) for k, v in data.items()]
    df = pd.concat(dfs)
    return df


def get_target_gamma_fga(file, genome_size, fga_gamma, fga_threshold):
    """
    (str, int) -> pandas dataframe

    Calculates fga from file at target_gamma level

    Parameters
    ----------
    - file (str): path to zip file to be parsed
    - target_gamma (int): gamma level for fga

    """
    with zipfile.ZipFile(file) as sequenza_zip:
        # extract target file name from zip file
        zipcontents = sequenza_zip.namelist()
        r = re.compile(rf"^gammas/{fga_gamma}/.*Total_CN\.seg")
        target_file = list(filter(r.match, zipcontents))[0]

        # open the file into pandas df
        with sequenza_zip.open(target_file) as f:
            df = pd.read_csv(f, index_col=0, delimiter="\t")
            df["len"] = df["loc.end"] - df["loc.start"]

            # fraction genome altered for gamma = FGA_GAMMA, where
            # seg.mean is greater than FGA_THRESHOLD
            fga = (
                df.loc[df["seg.mean"] > fga_threshold, "len"].sum()
                / genome_size
            )

            fga_df = pd.DataFrame.from_dict({"fga": [fga]})
            return fga_df


def parse_record(alt_soln, zip_file, genome_size, fga_gamma, fga_threshold):
    return (
        parse_alt_soln(alt_soln),
        get_target_gamma_fga(zip_file, genome_size, fga_gamma, fga_threshold),
    )
