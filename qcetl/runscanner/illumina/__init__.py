import json
import logging
import os
from typing import List, Dict, Any

import numpy
import pandas
from pandas import DataFrame

import qcetl.common
import qcetl.runscanner
from qcetl.column import (
    RunScannerFlowcellColumn as FlowcellColumn,
    RunScannerLaneColumn as LaneColumn,
    RunScannerValidationColumn as ValidationColumn,
)
from qcetl.common.utility import rename_columns
from qcetl.runscanner.illumina.constants import LEVEL, FLOW_CELL_TYPES
from qcetl.runscanner.illumina.parse import (
    get_all_data_frames,
    get_data_frame,
    LongIndex,
    LongColumn,
)
import qcetl.runscanner.illumina.validate
import qcetl.common.validate

logger = logging.getLogger(__name__)


class RunScannerIlluminaCache(qcetl.common.Cache):
    def __init__(self, url=None):
        """

        Args:
            url: URL to JSON file containing all the runs. Can be set to a
                default by QC_ETL_RUNSCANNER_MASTER_URL environmental
                variable
        """

        self.name = "runscannerillumina"
        self.schema_versions = {
            1: {
                "flowcell": {
                    FlowcellColumn.PercentAboveQ30: "f",
                    FlowcellColumn.BaseMask: "s",
                    FlowcellColumn.BclCount: "i",
                    FlowcellColumn.CallCycle: "i",
                    FlowcellColumn.Chemistry: "s",
                    FlowcellColumn.Clusters: "qi",  # May be invalid and be set to NA
                    FlowcellColumn.ClustersPF: "qi",  # May be invalid and be set to NA
                    FlowcellColumn.CompletionDate: "d",
                    FlowcellColumn.ContainerModel: "s",
                    FlowcellColumn.ContainerSerialNumber: "s",
                    FlowcellColumn.Cycles: "s",
                    FlowcellColumn.Ends: "s",
                    FlowcellColumn.HealthType: "s",
                    FlowcellColumn.ImgCycle: "i",
                    FlowcellColumn.IndexLengths: "s",
                    FlowcellColumn.IndexSequencing: "qs",
                    FlowcellColumn.LaneCount: "i",
                    FlowcellColumn.NumberCycles: "i",
                    FlowcellColumn.NumberReads: "i",
                    FlowcellColumn.MISOHealthType: "s",
                    FlowcellColumn.PairedEndRun: "b",
                    FlowcellColumn.Platform: "s",
                    FlowcellColumn.ProjectedYieldIndex1: "f",
                    FlowcellColumn.ProjectedYieldIndex2: "f",
                    FlowcellColumn.ProjectedYieldRead1: "f",
                    FlowcellColumn.ProjectedYieldRead2: "f",
                    FlowcellColumn.Read1Length: "i",
                    FlowcellColumn.Read2Length: "qi",
                    FlowcellColumn.Run: "s",
                    FlowcellColumn.RunBaseMask: "s",
                    FlowcellColumn.ScoreCycle: "i",
                    FlowcellColumn.SequencerFolderPath: "p",
                    FlowcellColumn.SequencerName: "s",
                    FlowcellColumn.SequencerPosition: "s",
                    FlowcellColumn.SequencingKit: "qs",
                    FlowcellColumn.Software: "s",
                    FlowcellColumn.StartDate: "d",
                    FlowcellColumn.WorkflowType: "s",
                    FlowcellColumn.YieldIndex1: "f",
                    FlowcellColumn.YieldIndex2: "f",
                    FlowcellColumn.YieldRead1: "f",
                    FlowcellColumn.YieldRead2: "f",
                },
                "lane": {
                    LaneColumn.AlignedRead1: "f",
                    LaneColumn.AlignedRead1StandardDeviation: "f",
                    LaneColumn.AlignedRead2: "f",
                    LaneColumn.AlignedRead2StandardDeviation: "f",
                    LaneColumn.ClusterDensity: "f",
                    LaneColumn.ClusterDensityStandardDeviation: "f",
                    LaneColumn.Clusters: "qi",
                    LaneColumn.ClustersPF: "qi",
                    LaneColumn.DensityPercentage: "f",
                    LaneColumn.DensityPF: "f",
                    LaneColumn.DensityPFStandardDeviation: "f",
                    LaneColumn.LaneNumber: "i",
                    LaneColumn.PercentAboveQ30Index1: "qi",
                    LaneColumn.PercentAboveQ30Index2: "qi",
                    LaneColumn.PercentAboveQ30Read1: "qi",
                    LaneColumn.PercentAboveQ30Read2: "qi",
                    LaneColumn.Pool: "s",
                    LaneColumn.Q30: "qi",
                    LaneColumn.Run: "s",
                },
            }
        }
        self.columns = {1: {"flowcell": FlowcellColumn, "lane": LaneColumn}}
        self.input_format = {"run": "s", "status": "s"}
        self.url = url
        self.fetch_cache = None
        self.primary_key = {
            1: {
                "flowcell": [FlowcellColumn.Run],
                "lane": [LaneColumn.Run, LaneColumn.LaneNumber],
            }
        }
        self.input_key = {1: ("run", FlowcellColumn.Run)}

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Loads JSON from URL.

        Returns:

        """
        if self.url is None:
            self.url = os.getenv("QC_ETL_RUNSCANNER_MASTER_URL")

        if self.url is None:
            raise TypeError(
                "Run Scanner URL never specified. Do it during "
                "initialization or via QC_ETL_RUNSCANNER_MASTER_URL "
                "environmental variable "
            )

        return qcetl.common.utility.load_json_from_url(self.url)

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            if name == "flowcell":
                if (
                    not cleaning_rules.mark_invalid_cluster_nan
                    and not cleaning_rules.mark_invalid_cluster_pf_nan
                    and not cleaning_rules.mark_invalid_healthstatus_failed
                    and cleaning_rules.remove_validate_columns
                ):
                    return df

                log = log_creator(__name__)
                df = qcetl.runscanner.illumina.validate.mark_flow_cell_invalid(
                    df, log
                )
                df = qcetl.common.validate.replace_bool(
                    df,
                    ValidationColumn.ETLValidateClusters,
                    FlowcellColumn.Clusters,
                    numpy.nan,
                    log,
                )
                df = qcetl.common.validate.replace_bool(
                    df,
                    ValidationColumn.ETLValidateClustersPF,
                    FlowcellColumn.ClustersPF,
                    numpy.nan,
                    log,
                )
                df = qcetl.common.validate.replace_bool(
                    df,
                    ValidationColumn.ETLValidateHeathStatus,
                    FlowcellColumn.HealthType,
                    "FAILED",
                    log,
                )

                if cleaning_rules.remove_validate_columns:
                    df = df.drop(
                        columns=[
                            ValidationColumn.ETLValidateClusters,
                            ValidationColumn.ETLValidateClustersPF,
                            ValidationColumn.ETLValidateHeathStatus,
                        ]
                    )

            return df

        return filter_function

    def parse_single_record(self, single_input, schema_version):
        if self.fetch_cache is None:
            self.fetch_cache = self.fetch()

        run = single_input["run"]
        status = single_input["status"]

        to_parse = [x for x in self.fetch_cache if x["runAlias"] == run]
        if len(to_parse) != 1:
            raise qcetl.common.InvalidRecordError(
                "Run does not exist uniquely in RunScanner: {}".format(run)
            )
        to_parse = to_parse[0]
        # Inject the MISO status so it gets parsed in flow cell parser
        to_parse[FlowcellColumn.MISOHealthType] = status
        df = get_data_frame(to_parse)

        parsed_df = {}
        # Missing runAlias indicates a run that has deep problems
        if "runAlias" not in df.index.get_level_values("key"):
            logger.warning(
                "Cannot parse record as runAlias is missing: {}".format(
                    single_input
                )
            )
            return parsed_df

        wide_flow_cell_df = get_wide_flow_cell(df)
        for col in self.get_dtypes()["flowcell"]:
            if col not in wide_flow_cell_df:
                wide_flow_cell_df[col] = numpy.nan

        wide_flow_cell_df = wide_flow_cell_df.astype(
            self.get_dtypes()["flowcell"]
        )
        if any(wide_flow_cell_df[FlowcellColumn.CompletionDate].isnull()):
            logger.warning(
                "Run has no completion date. Won't be stored: {}".format(
                    single_input
                )
            )
        else:
            parsed_df["flowcell"] = wide_flow_cell_df.astype(
                self.get_dtypes()["flowcell"]
            )

        if LEVEL.LANE not in df.index.get_level_values(LongIndex.Level):
            logger.warning(
                "Cannot parse lanes as lane information is missing: {}".format(
                    single_input
                )
            )
        else:
            wide_lane_df = get_wide_lane(df)
            for col in self.get_dtypes()["lane"]:
                if col not in wide_lane_df:
                    wide_lane_df[col] = numpy.nan

            parsed_df["lane"] = wide_lane_df.astype(self.get_dtypes()["lane"])

        return {1: parsed_df}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {"flowcell": {}, "lane": {}}


def get_wide_flow_cell(long_master_df: DataFrame) -> DataFrame:
    """
    Extract flow cell metrics as a wide DataFrame from the master DataFrame
    that is in long format. The read and index metrics and included

    Args:
        long_master_df: The master DataFrame, which is in long format

    Returns:

    """
    long_flow_cell = long_master_df.xs(
        key=LEVEL.FLOWCELL, level=LongIndex.Level
    )
    wide_flow_cell = long_flow_cell[LongColumn.Value].unstack(
        LongIndex.Key, fill_value=numpy.nan
    )

    # Strange HiSeq runs without run alias info  (see 210427_D00355_0381_BHKW5KBCX3)
    # As the `runAlias` column is missing, the below merges cannot be done
    missing_alias = wide_flow_cell["runAlias"].isna()
    if sum(missing_alias) > 0:
        logger.warning(
            "{} flow cell(s) excluded as they don't have a run alias".format(
                sum(missing_alias)
            )
        )
        wide_flow_cell = wide_flow_cell[~missing_alias]

    if LEVEL.INDEX in long_master_df.index.get_level_values(LongIndex.Level):
        read = get_wide_read(long_master_df)
        # Unstack makes multi-index column, which are then mapped into one index
        read = read.unstack("level_name")
        read.columns = read.columns.map(
            lambda c: "{} (Read {})".format(c[0], c[1])
        )
        wide_flow_cell = wide_flow_cell.merge(
            read,
            "left",
            left_on="runAlias",
            right_index=True,
            validate="one_to_one",
        )

        index = get_wide_index(long_master_df)
        # Unstack makes multi-index column, which are then mapped into one index
        index = index.unstack("level_name")
        index.columns = index.columns.map(
            lambda c: "{} (Index {})".format(c[0], c[1])
        )
        wide_flow_cell = wide_flow_cell.merge(
            index,
            "left",
            left_on="runAlias",
            right_index=True,
            validate="one_to_one",
        )

    # Strip away unnecessary index as they are already columns
    wide_flow_cell = wide_flow_cell.reset_index(drop=True)

    # `unstack` does not correctly infer numeric types (bug?)
    wide_flow_cell = wide_flow_cell.apply(pandas.to_numeric, errors="ignore")
    wide_flow_cell = wide_flow_cell.astype(FLOW_CELL_TYPES)

    # The date type from Shesmu doesn't have a timezone, so strip if from here
    wide_flow_cell[FlowcellColumn.CompletionDate] = wide_flow_cell[
        FlowcellColumn.CompletionDate
    ].dt.tz_localize(None)
    wide_flow_cell[FlowcellColumn.StartDate] = wide_flow_cell[
        FlowcellColumn.StartDate
    ].dt.tz_localize(None)

    rename_columns(wide_flow_cell, {"runAlias": LaneColumn.Run})
    return wide_flow_cell


def get_wide_index(long_master_df: DataFrame) -> DataFrame:
    """
    Extract index metrics as a wide DataFrame from the master DataFrame
    that is in long format

    Args:
        long_master_df: The master DataFrame, which is in long format

    Returns:

    """
    long_index = long_master_df.xs(key=LEVEL.INDEX, level=LongIndex.Level)
    wide_index = long_index[LongColumn.Value].unstack(
        LongIndex.Key, fill_value=numpy.nan
    )

    # `unstack` does not correctly infer numeric types (bug?)
    wide_index = wide_index.apply(pandas.to_numeric, errors="ignore")

    return wide_index


def get_wide_lane(long_master_df: DataFrame) -> DataFrame:
    """
    Extract lane metrics as a wide DataFrame from the master DataFrame
    that is in long format

    Args:
        long_master_df: The master DataFrame, which is in long format

    Returns:

    """
    long_lane = long_master_df.xs(key=LEVEL.LANE, level=LongIndex.Level)
    wide_lane = long_lane[LongColumn.Value].unstack(
        LongIndex.Key, fill_value=numpy.nan
    )

    # Add the uncertainty columns (which is its own column in the long format)
    # Any metrics without uncertainty measures will be excluded
    uncertainty = long_lane.dropna(subset=[LongColumn.Uncertainty])
    uncertainty = uncertainty[LongColumn.Uncertainty].unstack(
        LongIndex.Key, fill_value=numpy.nan
    )
    uncertainty = uncertainty.add_suffix(" Standard Deviation")

    wide_lane = wide_lane.merge(
        uncertainty,
        "left",
        left_index=True,
        right_index=True,
        validate="one_to_one",
    )

    # The index contains the run_alias and lane number metadata
    wide_lane = wide_lane.reset_index()
    wide_lane = wide_lane.rename(
        columns={LongIndex.LevelName: LaneColumn.LaneNumber}
    )

    # `unstack` does not correctly infer numeric types (bug?)
    wide_lane = wide_lane.apply(pandas.to_numeric, errors="ignore")
    rename_columns(wide_lane, {"run_alias": LaneColumn.Run})
    return wide_lane


def get_wide_read(long_master_df: DataFrame) -> DataFrame:
    """
    Extract read metrics as a wide DataFrame from the master DataFrame
    that is in long format

    Args:
        long_master_df: The master DataFrame, which is in long format

    Returns:

    """
    long_read = long_master_df.xs(key=LEVEL.READ, level=LongIndex.Level)
    wide_read = long_read[LongColumn.Value].unstack(
        LongIndex.Key, fill_value=numpy.nan
    )
    # `unstack` does not correctly infer numeric types (bug?)
    wide_read = wide_read.apply(pandas.to_numeric, errors="ignore")

    return wide_read
