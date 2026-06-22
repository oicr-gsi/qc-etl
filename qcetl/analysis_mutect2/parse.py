import pandas as pd
import numpy as np
from qcetl.column import AnalysisMutect2Column as Mutect2Column

NUM_DP = 2  # number of decimal points to round ti, tv ratios

# index of the columns for VCF files, see
# VCF specs for column order
FILTER = 6
REF = 3
ALT = 4


def parse_vcf_record(vcf):
    """
    (str) -> pandas dataframe

    Selects statistics for mutect2 process from vcf

    Parameters
    ----------
    - file (str): path to file to be parsed

    """

    results = {
        Mutect2Column.NumCalls: 0,
        Mutect2Column.NumPASS: 0,
        Mutect2Column.PASSNumSNPs: 0,
        Mutect2Column.PASSNumMultiSNPs: 0,
        Mutect2Column.PASSNumIndels: 0,
        Mutect2Column.TITVRatio: np.nan,
        Mutect2Column.PASSNumMNPs: 0,
        Mutect2Column.PctTI: 0,
        Mutect2Column.PctTV: 0,
    }

    total_ti = 0
    total_tv = 0

    chunksize = 5 * 10**4

    # it is possible the csv only contains the header
    try:
        df = pd.read_csv(
            vcf,
            sep="\t",
            comment="#",
            header=None,  # No headers, instead use VCF column indices
            chunksize=chunksize,
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame(results, index=[0])

    for sub_df in df:
        # num_calls = the number of vcf records, including PASS and
        # non-PASS calls
        results[Mutect2Column.NumCalls] = results[Mutect2Column.NumCalls] + len(
            sub_df
        )

        # num_PASS = the number of vcf records where the FILTER field is
        # marked as PASS
        results[Mutect2Column.NumPASS] = results[Mutect2Column.NumPASS] + len(
            sub_df[sub_df[FILTER] == "PASS"]
        )

        if 0 != results[Mutect2Column.NumPASS]:

            # SNPs are when REF and ALT each have a single base
            results[Mutect2Column.PASSNumSNPs] = results[
                Mutect2Column.PASSNumSNPs
            ] + len(
                sub_df[
                    (sub_df[FILTER] == "PASS")
                    & (sub_df[REF].str.len() == 1)
                    & (sub_df[ALT].str.len() == 1)
                ]
            )

            # multiallelic SNPS are where there are multiple ALT indicated as
            # a comma separated list. These may represent SNPs or Indels
            results[Mutect2Column.PASSNumMultiSNPs] = results[
                Mutect2Column.PASSNumMultiSNPs
            ] + len(
                sub_df[
                    (sub_df[FILTER] == "PASS")
                    & (sub_df[REF].str.len() == 1)
                    & (sub_df[ALT].str.contains(","))
                ]
            )

            # MNPs have that REF and ALT are the same length, but
            # greater than 1 base in length
            results[Mutect2Column.PASSNumMNPs] = results[
                Mutect2Column.PASSNumMNPs
            ] + len(
                sub_df[
                    (sub_df[FILTER] == "PASS")
                    & (sub_df[REF].str.len() > 1)
                    & (sub_df[REF].str.len() == sub_df[ALT].str.len())
                ]
            )

            # transitions are single base substitutions purine to
            # purine (A<->G) or pyrimidine to pyrimidine (C<>T)
            total_ti = total_ti + len(
                sub_df[
                    (sub_df[FILTER] == "PASS")
                    & (sub_df[REF].str.len() == 1)
                    & (sub_df[ALT].str.len() == 1)
                    & (sub_df[REF] + sub_df[ALT]).isin(["AG", "GA", "CT", "TC"])
                ]
            )
            # transversions are single base substitutions purine <-> pyrmidine
            # (A<->C, A<->T, C<->G, G<->T)
            total_tv = total_tv + len(
                sub_df[
                    (sub_df[FILTER] == "PASS")
                    & (sub_df[REF].str.len() == 1)
                    & (sub_df[ALT].str.len() == 1)
                    & (sub_df[REF] + sub_df[ALT]).isin(
                        ["AC", "AT", "CA", "CG", "GT", "GC", "TA", "TG"]
                    )
                ]
            )

        # indels are everything else
        results[Mutect2Column.PASSNumIndels] = (
            results[Mutect2Column.NumPASS]
            - results[Mutect2Column.PASSNumSNPs]
            - results[Mutect2Column.PASSNumMultiSNPs]
            - results[Mutect2Column.PASSNumMNPs]
        )

        # percent transitions and transversions of all PASS calls
        if 0 != results[Mutect2Column.NumPASS]:
            results[Mutect2Column.PctTI] = round(
                total_ti / results[Mutect2Column.NumPASS], NUM_DP
            )
            results[Mutect2Column.PctTV] = round(
                total_tv / results[Mutect2Column.NumPASS], NUM_DP
            )

        # ratio of transitions : transversions
        results[Mutect2Column.TITVRatio] = (
            np.nan if total_tv == 0 else round(total_ti / total_tv, NUM_DP)
        )

    return pd.DataFrame(results, index=[0])


def parse_tsv_record(tsv):
    """
    (str) -> pandas dataframe

    Reads precomputed mutect2 statistics from a TSV file

    Parameters
    ----------
    - tsv (str): path to tsv file to be parsed

    """

    col = [
        Mutect2Column.NumCalls,
        Mutect2Column.NumPASS,
        Mutect2Column.PASSNumSNPs,
        Mutect2Column.PASSNumMultiSNPs,
        Mutect2Column.PASSNumIndels,
        Mutect2Column.TITVRatio,
        Mutect2Column.PASSNumMNPs,
        Mutect2Column.PctTI,
        Mutect2Column.PctTV,
    ]

    try:
        df = pd.read_csv(tsv, sep="\t")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(index=[0])

    missing = set(col) - set(df.columns)
    if missing:
        raise ValueError(f"TSV file is missing required columns: {missing}")

    return df[col]
