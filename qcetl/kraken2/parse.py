import logging
import numpy
import pandas
from pandas import DataFrame

from qcetl.column import Kraken2Column as Column

logger = logging.getLogger(__name__)


def parse_record(path: str) -> DataFrame:
    """
    Parse kraken2 output, adding the parents and children column. One column is removed
    as its meaning is unknown

    Args:
        path: path to kraken2 output
    Returns:
        DataFrame
    """
    df = pandas.read_csv(
        path,
        sep="\t",
        header=None,
        names=[
            Column.PercentAtClade,
            Column.CountAtClade,
            Column.Count,
            Column.Rank,
            Column.TaxonomicID,
            Column.Name,
        ],
    )

    # The phylogeny is represented by 2 space indent and order of listing
    # Multiple roots are possible, so NaN acts are the real singular root
    stack = [(numpy.nan, -1)]
    parents = []

    for line in df[Column.Name]:
        name = line.strip()
        line = line.rstrip()
        depth = len(line) - len(name)
        current_depth = stack[-1][1]

        while depth <= current_depth:
            stack.pop()
            current_depth = stack[-1][1]

        parents.append(stack[-1][0])
        stack.append((name, depth))

    # Remove indents that used to indicate hierarchy
    df[Column.Name] = df[Column.Name].str.strip()
    df[Column.Parent] = parents

    return df
