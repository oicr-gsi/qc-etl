"""
hmftools PURPLE purity parsing module.

Parses the single-row PURPLE purity file (``*.purple.purity.tsv``) for a
merged/call-ready tumour. ``Purity`` is the inferred tumour purity; the min/max
purity and ploidy fields support review of alternate PURPLE solutions.
"""

import logging

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import HmfPurpleColumn as Column

logger = logging.getLogger(__name__)

# Map the raw purity.tsv header to the declared DataFrame column name.
PURITY_COLUMN_MAP = {
    "purity": Column.Purity,
    "ploidy": Column.Ploidy,
    "normFactor": Column.NormFactor,
    "score": Column.Score,
    "diploidProportion": Column.DiploidProportion,
    "polyclonalProportion": Column.PolyclonalProportion,
    "minPurity": Column.MinPurity,
    "maxPurity": Column.MaxPurity,
    "minPloidy": Column.MinPloidy,
    "maxPloidy": Column.MaxPloidy,
    "minDiploidProportion": Column.MinDiploidProportion,
    "maxDiploidProportion": Column.MaxDiploidProportion,
    "somaticPenalty": Column.SomaticPenalty,
}


def parse_record(path: str) -> DataFrame:
    """
    Parse the single-row PURPLE purity table.

    Args:
        path: Path to ``*.purple.purity.tsv``

    Returns: A one-row DataFrame with declared column names
    """
    df = pandas.read_csv(path, sep="\t")
    df = df.rename(columns=PURITY_COLUMN_MAP)
    # Keep only known columns so a new upstream column does not break the schema
    df = df[list(PURITY_COLUMN_MAP.values())]
    with pandas.option_context("future.no_silent_downcasting", True):
        df = df.fillna(value=numpy.nan)
    return df
