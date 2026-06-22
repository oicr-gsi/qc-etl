import json
import numpy
import os
import pandas
from pandas import DataFrame
import pandas.io.json
import pathlib
import time
from typing import Any, Dict, Union, Container, Callable, List, Iterable
import urllib.request
import urllib.error

from qcetl.common.exceptions import InvalidRecordError


def load_json_from_url(url: str) -> Any:
    """
    Load JSON from a url

    Args:
        url: The URL.

    Returns:

    Raises:
        InvalidRecordError: If URL cannot be accessed
    """
    try:
        with urllib.request.urlopen(url) as j:
            if j.getcode() == 404:
                return None
            else:
                string = j.read().decode()
    except urllib.error.URLError as e:
        raise InvalidRecordError(
            "Cannot access URL from {}: {}".format(url, e)
        ) from e

    try:
        return json.loads(string)
    except json.decoder.JSONDecodeError as e:
        raise InvalidRecordError(
            "Cannot decode string from JSON from {}. {}: {}".format(
                url, e, string
            )
        ) from e


def hdf_cache_to_csv(cache_path: str, save_dir: str = None):
    """
    Takes a cache file in hdf5 format and saves it as a csv file.

    If the hdf5 file contains more than one DataFrame, multiple csv files are
    created. In those cases, the group name specifying the DataFrame in the
    hdf5 file will be appended to the csv filename.

    Args:
        cache_path: Path to the cache file
        save_dir: Directory to save the csv files in. By default, same as hdf

    """
    cache_dir, cache_file = os.path.split(cache_path)

    if save_dir is None:
        save_dir = cache_dir

    # Remove hdf5 extension
    file_without_ext = pathlib.Path(cache_file).with_suffix("")

    # How many DataFrames in one hdf5 file
    with pandas.HDFStore(cache_path) as hdf:
        group_names = hdf.keys()
        has_one_group = len(group_names) == 1

    for g in group_names:
        if has_one_group:
            save_path = os.path.join(
                save_dir, file_without_ext.with_suffix(".csv")
            )
        else:
            # Group names are path like, so heave a leading /
            # Needs to be removed before appending to file name
            new_name = str(file_without_ext) + "_" + g[1:]
            new_name = pathlib.Path(new_name)

            save_path = os.path.join(save_dir, new_name.with_suffix(".csv"))

        df: pandas.DataFrame = pandas.read_hdf(cache_path, g)
        df.to_csv(save_path)


def hdf_dir_to_csv(cache_dir: str, save_dir: str = None):
    """
    Converts all hdf5 files in the given directory to csv files.

    Same considerations as `hdf_cache_to_csv`.

    Args:
        cache_dir: Path to directory containing files with the hd5 extension.
            By default, the same as the default cache save directory
        save_dir: Directory to save the csv files in. By default, same as hdf
            directory

    """
    for f in os.listdir(cache_dir):
        if f.endswith(".hd5"):
            path = os.path.join(cache_dir, f)
            hdf_cache_to_csv(path, save_dir)


def multiindex_get_levels(
    mi: pandas.MultiIndex, levels: Container[str]
) -> Union[pandas.MultiIndex, pandas.Index]:
    """
    Get the specified levels from a MultiIndex

    Currently, there is no clean was to extract specific levels from a
    MultiIndex. The workaround is to drop unwanted levels, but that requires
    additional steps and sanity checks. This function wraps all these steps.

    Args:
        mi: The MultiIndex to select levels from
        levels: The levels to get

    Returns: The only one level is being returned, the return type is Index,
        otherwise MultiIndex

    Raises:
        KeyError: If any one level is not found in the MultiIndex

    """
    multiindex_levels = set(mi.names)
    levels = set(levels)

    if not levels.issubset(multiindex_levels):
        raise KeyError(
            "At least one requested level in {} is not found in the "
            "MultiIndex levels {}".format(multiindex_levels, levels)
        )

    to_drop = multiindex_levels.difference(levels)

    return mi.droplevel(list(to_drop))


def add_custom_column(df: DataFrame, name: str, values: Any):
    """
    Parsed DataFrames keep the column names of their source whenever
    possible. A common occurrence is the addition of extra columns. For
    example, LIMS IUS SWID is added to allow linking to File Provenance.

    The addition is done in place and name collisions raise an error.

    Args:
        df: Column will be added to this DataFrame
        name: The new column names
        values: The new values. Must match the length of input DataFrame

    Raises:
        InvalidRecordError: If column exists

    """
    if name in df.columns:
        raise InvalidRecordError(
            "New column name '{}' already present in DataFrame".format(name)
        )

    df[name] = values


def get_column_names(col_class: Callable) -> set:
    """
    Column names for the cached DataFrames are kept as a class variables. There
    is no clean way to iterate over the names. This returns the class variables.

    Stolen from https://stackoverflow.com/questions/1398022/
    looping-over-all-member-variables-of-a-class-in-python

    Args:
        col_class: The class from which to extract class variables

    Returns:

    """
    return {
        getattr(col_class, attr)
        for attr in dir(col_class())
        if not callable(getattr(col_class, attr)) and not attr.startswith("__")
    }


def get_schema(df: DataFrame) -> dict:
    """
    Returns a dictionary describing column names and their types, index of the
    DataFrame and its type, and the version of Pandas used to create the cached
    DataFrame

    Args:
        df: DataFrame for which schema is requested

    Returns: Dictionary is described at https://pandas.pydata.org/pandas-docs
    /stable/reference/api/
    pandas.io.json.build_table_schema.html#pandas.io.json.build_table_schema

    """
    result = pandas.io.json.build_table_schema(df)

    # There is a bug where the pandas version is always set to 0.20.0
    result["pandas_version"] = pandas.__version__

    return result


def rename_columns(df: DataFrame, rename_map=Dict[str, str], strict=True):
    """
    Rename columns in a DataFrame, with error handling.

    Used to impose consistent column names on run, lane, and barcode.

    Args:
        df: Dataframe with original column names (eg. from JSON input)
        rename_map: Mapping from old to new column names
        strict: Boolean. Default = True. If True, raise an InvalidRecordError
    when not all columns in rename_map are present in df

    Returns: None. The input DataFrame is modified in-place.

    Raises:
        InvalidRecordError: If "strict" is True and not all columns in rename_map are present in df
    """
    if strict:
        error_arg = "raise"
    else:
        error_arg = "ignore"
    try:
        df.rename(columns=rename_map, inplace=True, errors=error_arg)
    except KeyError as e:
        raise InvalidRecordError(
            "Unable to rename DataFrame columns {0}, strict mode = {1}".format(
                rename_map, strict
            )
        ) from e


def median_from_frequency_table(
    df: DataFrame, value_col: str = "value", count_col: str = "count"
) -> float:
    """
    Calculate median from a DataFrame that has counts of values (frequency table). This
    can be used to calculate medians from the histograms produced by BamQC.

    Args:
        df: Frequency DataTable
        value_col: The column name of the values
        count_col: The column name of the value counts

    Returns: The median

    """
    if len(df) == 0:
        return numpy.nan

    df = df.sort_values(value_col)

    # The cumulative sum series index matches that of the input DataFrame
    cumsum = df[count_col].cumsum()
    total = cumsum.iloc[-1]

    if total % 2 == 0:
        cutoff = total / 2
        m = (
            df[cumsum >= cutoff][value_col].iloc[0]
            + df[cumsum >= cutoff + 1][value_col].iloc[0]
        ) / 2
    else:
        cutoff = (total + 1) / 2
        m = df[cumsum >= cutoff][value_col].iloc[0]

    return m


def quantile_from_frequency_table(
    df: DataFrame, q: float, value_col: str = "value", count_col: str = "count"
) -> float:
    """
    Calculate an arbitrary quantile for a  DataFrame that has counts of values
    (frequency table). This emulates `pandas.Series.quantile` with the interpolation
    parameter being set to "lowest".

    Args:
        df: Frequency DataTable
        q: Quantile to find (0 <= q <= 1)
        value_col: The column name of the values
        count_col: The column name of the value counts

    Returns:

    """
    if len(df) == 0:
        return numpy.nan

    df = df.sort_values(value_col)

    # The cumulative sum series index matches that of the input DataFrame
    cumsum = df[count_col].cumsum()
    cutoff = cumsum.iloc[-1] * q
    return df[cumsum >= cutoff][value_col].iloc[0]


def concat_workflow_versions(dfs: List[DataFrame], ius_cols: List[str]):
    """
    Safely concat workflows across different versions. The following guarantees are
    provided:

    * Data will be deduplicated by the provided ius. The first occurrence is kept (order
        is determined from input DataFrames)
    * Data type of merged column will be the broadest type (int and float will be float,
        int and str (object) will be object
    * Columns not present in all DataFrames will be retained with NaN

    Args:
        dfs: The workflow DataFrames to combine. In case of IUS duplication, the record
            from the first DataFrame will be kept
        ius_cols: The columns on which to deduplicate

    Returns: Combined workflow DataFrame

    Raises:
        InvalidRecordError: If the types of the ius columns are not all the same.
            Deduplication would fail in these instances.

    """
    ius_df = [x[ius_cols] for x in dfs]
    dtypes = set(tuple(x.dtypes) for x in ius_df)

    if len(dtypes) > 1:
        raise InvalidRecordError(
            "IUS columns are of different types: {}".format(dtypes)
        )

    all_df = pandas.concat(dfs)
    return all_df.drop_duplicates(ius_cols, keep="first")


def none_to_nan_json_hook(d: dict) -> dict:
    """
    Used with `object_hook` of `json.load` so that `null` json values are `numpy.nan`
    instead of `None`

    Args:
        d: Will be run on each dictionary from the JSON

    Returns: The converted dictionary

    """

    def recurse_list_element(lst):
        result = []
        for i in lst:
            if isinstance(i, list):
                result.append(recurse_list_element(i))
            else:
                result.append(numpy.nan if i is None else i)

        return result

    for k, v in d.items():
        if v is None:
            d[k] = numpy.nan
        # Hook only runs on dicts, so lists need to be addressed
        elif isinstance(v, list):
            d[k] = recurse_list_element(v)

    return d


def safe_pandas_concat(
    obs: Iterable[DataFrame], columns=None, *args, **kwargs
) -> DataFrame:
    """
    The same as `pandas.concat`, but returns an empty DataFrame instead of raising
    ValueError if empty list is supplied.

    Args:
        obs: List of pandas objects to concatenate
        columns: The columns to add to the empty DataFrame
        args: Passed to `pandas.concat`
        kwargs: Passed to `pandas.concat`

    Returns: The empty DataFrame has 0 rows

    """
    if obs:
        return pandas.concat(obs, *args, **kwargs)
    else:
        if columns is None:
            columns = []
        return DataFrame(columns)


class TimeOut:
    def __init__(self, timeout: float):
        self.start = time.monotonic()
        self.tmt = timeout

    def timeout(self) -> bool:
        return (time.monotonic() - self.start) > self.tmt
