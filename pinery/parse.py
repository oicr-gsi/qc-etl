import logging
from typing import Dict, Any, List, Union, Tuple

import numpy
import pandas
import pandas.io.json
from pandas import DataFrame

from pinery.column import HeredityColumn, HeredityIndex, SamplesColumn


def parse_record(rec: List[Dict[str, Any]]) -> DataFrame:
    """
    Takes all MISO sample records and converts it to a DataFrame.

    The `status` key is a dictionary with two keys. The values of the two keys
    differ in a few samples, so the `status` key is split into the `status` and
    `state` columns.

    The `preparation_kit` key is a dictionary with two keys: `description` and
    `name`. They are split into `preparation_kit_name` and
    `preparation_kit_description` fields.

    Args:
        rec: The record from Pinery

    Returns:

    """
    df = pandas.io.json.json_normalize(rec)

    att = df.pop("attributes")

    # Attributes are a list of name/value dictionaries
    att_decon = []
    for a in att:
        att_decon.append({x["name"]: x["value"] for x in a})
    att_df = pandas.DataFrame(att_decon)

    df = pandas.concat(
        [df, att_df], axis="columns", verify_integrity=True, sort=False
    )

    df = df.rename(
        errors="raise",
        columns={
            "status.name": SamplesColumn.Status,
            "status.state": SamplesColumn.State,
            "preparation_kit.description": SamplesColumn.PreparationKitDescription,
            "preparation_kit.name": SamplesColumn.PreparationKitName,
        },
    )

    return df


def heredity_to_dataframe(df: DataFrame, heredity_type: str) -> DataFrame:
    """
    Covert the nested children or parents column into an indexed DataFrame

    Args:
        df: The Pinery all samples DataFrame
        heredity_type: Extracting children or parents relationships

    Returns: A DataFrame with the index being `id` (reference sample) and
        `type` (children or parents). The single value column is `heredity
        id` (the sample that is a child or parent).

    """
    # Remove rows that do not have parents/children
    child_df = df.dropna(subset=[heredity_type])

    # Two lists. One for the starting id, one for the parent/child id
    child_result = {HeredityIndex.ID: [], HeredityColumn.HeredityID: []}

    for c in child_df.itertuples():
        i = [x["id"] for x in getattr(c, heredity_type)]
        child_result[HeredityColumn.HeredityID].extend(i)
        child_result[HeredityIndex.ID].extend([getattr(c, "id")] * len(i))

    result = pandas.DataFrame(child_result)
    result[HeredityIndex.Type] = heredity_type
    result = result.set_index([HeredityIndex.ID, HeredityIndex.Type])

    return result


def get_samples_data_frame(
    raw_records: List[Dict[str, Any]],
) -> Tuple[DataFrame, DataFrame]:
    """
    Coverts Pinery JSON records into two DataFrame.

    The first DataFrame includes all information except the heredity (children,
    parents). Due to the `attributes` field, records have different columns. If
    a record does not have a value in a column, it will be marked as NaN.

    The second DataFrame contains the heredity information

    Args:
        raw_records: The raw List parsed from the Pinery JSON record.

    Returns:

    """
    samples = parse_record(raw_records)
    children = heredity_to_dataframe(samples, "children")
    parents = heredity_to_dataframe(samples, "parents")
    heredity = pandas.concat([children, parents], sort=False).sort_index()

    # children and parents columns are removed from the samples DataFrame
    samples = samples.drop(columns=["children", "parents"])
    return samples, heredity


logger = logging.getLogger(__name__)


def extract_pool_attributes(pools: DataFrame) -> DataFrame:
    """
    Concatenating the pool DataFrames leaves the attribute field improperly
    parsed. It cannot be automatically parsed due to there being lots of NaN
    values and the format List[Dict(name, value)].

    Args:
        pools: The concatenated pool DataFrame of all the runs

    Returns: The returned DataFrame has the name key as the column and the
        value keys as row values. The order of the rows is identical for the
        input DataFrame

    """
    # Holds all name values, which will be the column names
    att_keys = set()
    # The dictionary which will be converted to the DataFrame
    # The key is the column name and the value is a list of row values
    dict_to_df = {}

    # Find all the name values
    for att in pools["attributes"]:
        if not pandas.isnull(att):
            keys = [x["name"] for x in att]
            att_keys.update(keys)

    # Add the future columns, with all values being NaN
    for key in att_keys:
        dict_to_df[key] = [numpy.nan] * len(pools["attributes"])

    # For each attribute row, add the value to the correct column
    for i in range(len(pools["attributes"])):
        att = pools["attributes"].iloc[i]
        if not pandas.isnull(att):
            for d in att:
                dict_to_df[d["name"]][i] = d["value"]

    return pandas.DataFrame(dict_to_df)


def get_run_data_frame(
    master_json: List[Dict[Any, Any]], parse_pool: bool
) -> Tuple[DataFrame, Union[None, DataFrame]]:
    """
    Creates two DataFrames. The first is the run information. The second
    is the optional pool information

    Args:
        master_json: The JSON list.
        parse_pool: Should the pool (positions column) be parsed

    Returns: Run info DataFrame

    """
    df = pandas.json_normalize(master_json)

    # Transform to look like it did before Pinery multi-container support.
    # * Removes any runs with 0 or >1 container
    # * Move the positions col back to top level and remove containers col
    df = df.dropna(subset=["containers"])
    df = df[df["containers"].apply(len) == 1]
    df["positions"] = df["containers"].apply(lambda x: x[0].get("positions"))
    df = df.drop(columns="containers")

    def add_name_to_pool(run):
        y = run["positions"]
        return [{**{"run_alias": run["name"]}, **x} for x in y]

    if parse_pool:
        # This adds the name of the run to each position
        pos = df.dropna(subset=["positions"]).apply(
            lambda x: add_name_to_pool(x), axis=1
        )

        # The positions are a list (lane) of lists (samples). Flatten them
        # https://stackoverflow.com/questions/952914/
        # how-to-make-a-flat-list-out-of-list-of-lists
        all_flat = [item for sublist in pos for item in sublist]
        # Remove any lane that lacks samples
        flat = [x for x in all_flat if "samples" in x]

        bad_lanes = len(all_flat) - len(flat)
        if bad_lanes:
            logger.warning(
                "{} lanes lacked pool information and were excluded from"
                "pool parsing".format(bad_lanes)
            )

        # Each element (pool) in samples gets its own row
        pools = pandas.json_normalize(
            flat,
            "samples",
            [
                "run_alias",
                "position",
                "poolId",
                "pool_name",
                "pool_created_by_id",
                "pool_created_date",
                "pool_modified_by_id",
                "pool_modified_date",
                "analysis_skipped",
            ],
        )
        # The pool attributes rows match those of the input DataFrame
        # They can be concatenated
        pool_attributes = extract_pool_attributes(pools)
        pools_combined = pandas.concat(
            [pools, pool_attributes], axis="columns", sort=False
        )
        pools_combined.drop(columns=["attributes"], inplace=True)
    else:
        pools_combined = None

    df = df.drop(columns="positions")

    return df, pools_combined
