"""Transform Runscanner JSON into DataFrame format.

The JSON file consists of a metrics field and everything else. The metrics
field is another complex JSON string containing sequencing stats.
Everything else is a simple JSON key/value structure containing sequencer
metadata.

Four fields will be used to convert from complex metrics JSON to structured
table:

level: What part of the machine/process does the metric refer to (Flow
Cell, Read, Lane)

level_name: If multiple different levels of the same type exist exist,
this name separates them. Currently, has real world meaning. (For Read: 1 or
2; for Lane: 1-8)

key: Name of metric

value: Value of metric

uncertainty: If the numeric value has an plus/minus uncertainty attached to
it, it is split of and stored in this column
"""

import json
import logging
import numpy
import pandas
from pandas import DataFrame, Series
from typing import List, Union, Dict, Any

from qcetl.runscanner.illumina.constants import LEVEL, KEY_NUMBERS, METRIC
from qcetl.column import RunScannerFlowcellColumn as FlowColumn

from qcetl.common import InvalidRecordError
import qcetl.common.utility


# TODO: Refactor away long RunScanner DataFrame and remove these columns
class IndexColumn:
    ProjectedYield = "Projected Yield"
    Yield = "Yield"


class LongColumn:
    Value = "value"
    Uncertainty = "uncertainty"


class LongIndex:
    RunAlias = "run_alias"
    Level = "level"
    LevelName = "level_name"
    Key = "key"


class ReadColumn:
    ProjectedYield = "Projected Yield"
    Yield = "Yield"


class RemovedColumn:
    ReadLength = "readLength"
    ReadLengths = "readLengths"


logger = logging.getLogger(__name__)


def fix_numbers(numb: Union[int, float, str]) -> Union[int, float, str]:
    """
    Removes comma, percentage, and leading/following whitespaces

    Args:
        numb: The number to format

    Returns: If string is given, removes non-numeric characters. Anything
        else is returned as is

    """
    try:
        result = numb.replace(",", "")
        result = result.replace("%", "")

        return result.strip()
    except AttributeError:
        return numb


def fix_flowcell_metadata(flowcell: DataFrame) -> DataFrame:
    """
    The `readLength` attribute is deprecated as it only assumes symmetrically
    paired reads. It will be removed. The `readLengths` attribute is a list of
    the individual read lengths. It will be split into readLength1 and
    readLength2.

    This needs to be called before any additional data is added to the
    DataFrame, so this function should be called early.

    Args:
        flowcell: The parsed flow cell DataFrame

    Returns: A copy of the input DataFrame with the fixed data

    Raises:
        InvalidRecordError: If ReadLengths column is not unique
        InvalidRecordError: If no or more than 2 reads are found

    """
    df = flowcell.copy()
    read_lengths = df.loc[
        df[LongIndex.Key] == RemovedColumn.ReadLengths, LongColumn.Value
    ]

    if len(read_lengths) != 1:
        raise InvalidRecordError(
            "{} appears multiple times in flow cell metadata: {}".format(
                RemovedColumn.ReadLengths, df.to_json()
            )
        )

    read_lengths = read_lengths.iloc[0]

    if len(read_lengths) == 1:
        read1 = read_lengths[0]
        read2 = numpy.nan
    elif len(read_lengths) == 2:
        read1 = read_lengths[0]
        read2 = read_lengths[1]
    else:
        raise InvalidRecordError(
            "Expected 1 or 2 reads for Illumina run from {}".format(
                read_lengths
            )
        )

    df = pandas.concat(
        [
            df,
            pandas.DataFrame(
                [
                    [FlowColumn.Read1Length, read1],
                    [FlowColumn.Read2Length, read2],
                ],
                columns=[LongIndex.Key, LongColumn.Value],
            ),
        ],
        ignore_index=True,
    )

    df = df[
        ~df[LongIndex.Key].isin(
            [RemovedColumn.ReadLength, RemovedColumn.ReadLengths]
        )
    ]

    return df


def extract_flowcell_metadata(run_series: Series) -> DataFrame:
    """
    Extracts the flow cell level metadata and adds the appropriate
    additional columns. Converts the data field to consistent format.

    Args:
        run_series: The Series generated from the JSON input

    Returns: DataFrame of flow cell level metadata

    """
    # Otherwise run_series would be modified in place
    series: Series = run_series.copy()

    # By default, the column name would be '0'
    df = series.to_frame(LongColumn.Value)

    # Extract the key column, which is the index after conversion to DataFrame
    df.index.names = [LongIndex.Key]
    df = df.reset_index(level=0)

    # The metrics JSON is parsed separately and is removed
    df = df[df[LongIndex.Key] != "metrics"]

    # This needs to be called before the extra columns are added
    df = fix_flowcell_metadata(df)

    df[LongIndex.Level] = LEVEL.FLOWCELL

    # The level name specifies which machine side was used (A or B)
    side = series[FlowColumn.SequencerPosition]
    df[LongIndex.LevelName] = side

    return df


def get_metric(all_metrics: List, metric_type: METRIC) -> Dict:
    """
    Extract specified metric from the list of all metrics

    Args:
        all_metrics: A list of all metrics provided by RunScanner
        metric_type: The type of the metric to retrieve

    Returns: The specified metric

    Warns: If any metric does not have mandatory type field

    Raises:
        InvalidRecordError: If metric does not exist

    """
    for metric in all_metrics:
        try:
            if metric["type"] == metric_type.value:
                return metric
        except KeyError:
            logger.warning(
                "Metric does not have expected `type` key: {}".format(metric)
            )

    raise InvalidRecordError(
        "Expected metric {} not found in {}".format(
            metric_type.value, all_metrics
        )
    )


def parse_chart(metrics: List, flow_side: str) -> DataFrame:
    """
    Converts the chart metrics into a DataFrame.

    ```
    {
        type: "chart",
        values: [{name: KEY, value: VALUE}]
    }
    ```

    Args:
        metrics: The RunScanner metrics as a list of dicts
        flow_side: The level_name column to add to the DataFrame.

    Returns: DataFrame with consistent column names across all metric fields

    Raises:
        InvalidRecordError: If expected metric is not found or cannot be read

    """
    chart = get_metric(metrics, METRIC.CHART)

    p_chart = pandas.json_normalize(chart, "values")
    p_chart.rename(columns={"name": LongIndex.Key}, inplace=True)

    p_chart[LongIndex.Level] = LEVEL.FLOWCELL
    p_chart[LongIndex.LevelName] = flow_side

    return p_chart


def parse_read_yield(metrics: List) -> DataFrame:
    """
    Converts the read yield metrics into a DataFrame.

    ```
    {
        type: "illumina-yield-by-read",
        categories: [LEVEl/LEVEL NAME],
        series: [{data: [VALUE], name: KEY}]
    }
    ```

    Args:
        metrics: The RunScanner metrics as a list of dicts

    Returns: DataFrame with consistent column names across all metric fields

    Raises:
        InvalidRecordError: If field contains no data

    """
    reads = get_metric(metrics, METRIC.YIELD_BY_READ)

    p_yield = pandas.json_normalize(reads["series"], "data", "name")

    if p_yield.empty:
        raise InvalidRecordError(
            "Yield-by-read field exists, but has no data: {}".format(reads)
        )

    p_yield.rename(
        columns={0: LongColumn.Value, "name": LongIndex.Key}, inplace=True
    )

    levels = reads["categories"]
    level = [x.strip().split(" ")[0] for x in levels]
    level_name = [x.strip().split(" ")[1] for x in levels]

    # Depends if it is single or paired reads
    read_num = len(reads["series"])
    p_yield[LongIndex.Level] = level * read_num
    p_yield[LongIndex.LevelName] = level_name * read_num
    return p_yield


def parse_table(metrics: List) -> DataFrame:
    """
    Converts the table metrics into a DataFrame. The table metrics are at
    the lane level.

    ```
    {
        type: "table",
        columns: [{name: VALUE, property: PROP}],
        rows: [{PROP: VALUE}]
    }
    ```

    Args:
        metrics: The RunScanner metrics as a list of dicts

    Returns: DataFrame with consistent column names across all metric fields

    Raises:
        InvalidRecordError: If expected metric is not found or cannot be read

    """
    table = get_metric(metrics, METRIC.TABLE)

    if len(table["rows"]) == 0:
        raise InvalidRecordError(
            "Expected at least one lane in table metric: {}".format(table)
        )

    # This creates a wide table with the keys as individual columns
    p_table = pandas.json_normalize(table, "rows")

    # Clearer names are in the column field of tables
    rename = {c["property"]: c["name"] for c in table["columns"]}
    p_table.rename(columns=rename, inplace=True)

    # Create long table based on lane
    p_table_melt = p_table.melt("Lane", var_name=LongIndex.Key)
    p_table_melt.rename(columns={"Lane": LongIndex.LevelName}, inplace=True)

    # The +- unicode is not read sometimes and replaced by questionmark
    p_table_melt["value"] = p_table_melt["value"].str.replace(
        "\ufffd", "\u00b1"
    )
    p_table_melt[LongIndex.Level] = LEVEL.LANE

    return p_table_melt


def parse_lane_clusters(metrics: List) -> DataFrame:
    """
    Converts the lane cluster metrics into a DataFrame.

    ```
    {
        type: "illumina-clusters-by-lane",
        series: [{data: [VALUES], name: KEY}]
    }
    ```

    Args:
        metrics: The RunScanner metrics as a list of dicts

    Returns: DataFrame with consistent column names across all metric fields

    Raises:
        InvalidRecordError: If expected metric is not found or cannot be read

    """
    lanes = get_metric(metrics, METRIC.CLUSTERS_BY_LANE)

    p_lane = pandas.json_normalize(lanes["series"], "data", "name")
    p_lane.rename(
        columns={0: LongColumn.Value, "name": LongIndex.Key}, inplace=True
    )

    # The data field length specifies how many lanes were used
    # Read the first element, as all data fields have the same length
    lane_name = list(range(1, len(lanes["series"][0]["data"]) + 1))
    lane_name = lane_name * len(lanes["series"])

    p_lane[LongIndex.Level] = LEVEL.LANE
    p_lane[LongIndex.LevelName] = lane_name

    return p_lane


def parse_run(run: Dict[str, Any]) -> DataFrame:
    """
    Parses run metadata and metrics into consistent DataFrame.

    Args:
        run: The run dictionary

    Returns:

    Raises:
        InvalidRecordError: If run alias contains to data

    Warns: If a metric does not exist or cannot be parsed

    """
    run_series = pandas.Series(run)
    metrics_json = json.loads(run_series["metrics"])
    side = run_series["sequencerPosition"]
    run_alias = run_series["runAlias"]

    metrics = []

    try:
        metrics.append(extract_flowcell_metadata(run_series))
    except InvalidRecordError as e:
        logger.warning(
            "Could not parse metadata for {}: {}".format(run_alias, e)
        )

    try:
        metrics.append(parse_chart(metrics_json, side))
    except InvalidRecordError as e:
        logger.warning("Could not parse chart for {}: {}".format(run_alias, e))

    try:
        metrics.append(parse_read_yield(metrics_json))
    except InvalidRecordError as e:
        logger.warning(
            "Could not parse read yields for {}: {}".format(run_alias, e)
        )

    try:
        metrics.append(parse_table(metrics_json))
    except InvalidRecordError as e:
        logger.warning("Could not parse table for {}: {}".format(run_alias, e))

    try:
        metrics.append(parse_lane_clusters(metrics_json))
    except InvalidRecordError as e:
        logger.warning(
            "Could not parse lane clusters for {}: {}".format(run_alias, e)
        )

    if len(metrics) == 0:
        raise InvalidRecordError(
            "Failed to parse any data for run alias {}".format(run_alias)
        )

    concat = pandas.concat(metrics, sort=False)
    concat[LongIndex.RunAlias] = run_alias

    return concat


def fix_value_column(master_df: DataFrame) -> DataFrame:
    """
    Minor fixes to ensure values have their proper types

    * Percent signs and commas are removed from numbers
    * All missing values identifiers are converted to numpy NaN

    Args:
        master_df: The DataFrame containing all data

    Returns: A new DataFrame with fixed values

    """
    # The passed DataFrame is not touched
    df: DataFrame = master_df.copy()

    # For easy MultiIndex accessing
    idx = pandas.IndexSlice

    # Remove non-numeric characters
    to_fix = df.loc[idx[:, :, :, KEY_NUMBERS], LongColumn.Value]
    df.loc[to_fix.index, LongColumn.Value] = to_fix.apply(fix_numbers)

    # None/nan string is used and needs to be replaced with NaN
    df[df[LongColumn.Value] == "None"] = numpy.nan
    df[df[LongColumn.Value] == "nan"] = numpy.nan
    df[df[LongColumn.Value] == "N/A"] = numpy.nan

    # None is used by JSON parsing. Replace with NaN
    df[df[LongColumn.Value].isna()] = numpy.nan

    return df


def split_off_uncertainty_column(master_df: DataFrame) -> DataFrame:
    """
    Some values have uncertainty information associated with them. This needs
    to be split off, so that the value can be properly interpreted.

    Args:
        master_df: The DataFrame containing all data

    Returns: A new DataFrame with a new uncertainty column

    """
    # The passed DataFrame is not touched
    df: DataFrame = master_df.copy()

    # Split any uncertainty values into their own columns
    # NaN is produced if the value is not a string. Converted to False
    uncrt_pos = df[LongColumn.Value].str.contains("\u00b1").fillna(False)
    # Create a DataFrame with Column 0 the value and Column 1 the uncertainty
    val_split = df.loc[uncrt_pos, LongColumn.Value].str.split(
        "\u00b1", expand=True
    )
    df[LongColumn.Uncertainty] = numpy.nan

    if not val_split.empty:
        df.loc[uncrt_pos, LongColumn.Value] = val_split[0]
        df.loc[uncrt_pos, LongColumn.Uncertainty] = val_split[1]

    return df


def get_data_frame(run_info: Dict[str, Any]) -> DataFrame:
    master_df = parse_run(run_info)

    master_df = master_df.set_index(
        [
            LongIndex.RunAlias,
            LongIndex.Level,
            LongIndex.LevelName,
            LongIndex.Key,
        ]
    )
    master_df = master_df.sort_index()

    master_df = split_off_uncertainty_column(master_df)
    master_df = fix_value_column(master_df)

    return master_df


def get_all_data_frames(run_info: List[Dict[str, Any]]) -> DataFrame:
    """
    Create the master DataFrame. The DataFrame is in the long format. The
    DataFrame is indexed on run_alias, level, level_name, and key for fast
    searching.

    Args:
        run_info: A list of loaded JSON Run Scanner files

    Returns: Run Scanner of all Illumina runs

    """
    results = []
    for run in run_info:
        try:
            results.append(parse_run(run))
        except InvalidRecordError as e:
            logger.error("Failed to add Run {}: {}".format(run, e))

    master_df = qcetl.common.utility.safe_pandas_concat(results)

    if not master_df.empty:
        master_df = master_df.set_index(
            [
                LongIndex.RunAlias,
                LongIndex.Level,
                LongIndex.LevelName,
                LongIndex.Key,
            ]
        )
        master_df = master_df.sort_index()

        master_df = split_off_uncertainty_column(master_df)
        master_df = fix_value_column(master_df)

    return master_df
