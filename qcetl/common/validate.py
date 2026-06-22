from logging import Logger
from pandas import DataFrame
from typing import Any


def remove_bool(df: DataFrame, which_col: str, log: Logger = None) -> DataFrame:
    """
    Removes rows based on boolean Validation columns. True means the row has
    failed validation and will be removed.

    Args:
        df: The DataFrame for which to remove records
        which_col: Which Validate column to use to remove records
        log: Log which records were removed

    Returns: A copy of the input DataFrame

    """
    to_remove = df[which_col]

    if sum(to_remove) > 0 and log is not None:
        log.warning(
            "Records that failed validation on column {} were removed. "
            "Number of records removed: {}".format(which_col, sum(to_remove))
        )

    result = df[~to_remove].copy()

    return result


def replace_bool(
    df: DataFrame,
    bool_col: str,
    replace_col: str,
    new_value: Any,
    log: Logger = None,
) -> DataFrame:
    """
    For any row where bool_col is True, replace that cell in the replace_col
    with the supplied value

    Args:
        df: The input DataFrame
        bool_col: Indicates if a value in this row needs to be replaced
        replace_col: The column where the cell will be replaced
        new_value: What value to replace with
        log: Optional warning logger

    Returns: A copy of the input DataFrame

    """
    df = df.copy()

    df.loc[df[bool_col], replace_col] = new_value

    if sum(df[bool_col]) > 0 and log:
        log.warning(
            "Values in column {} were replaced with {} if row value in column "
            "was set to {}".format(replace_col, new_value, bool_col)
        )

    return df
