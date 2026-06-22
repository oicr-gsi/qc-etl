from logging import Logger
import pandas
from pandas import DataFrame, Series

from qcetl.column import (
    RunScannerFlowcellColumn as FlowcellColumn,
    RunScannerValidationColumn as Validate,
)


def mark_flow_cell_invalid(
    flow_cell: DataFrame, log: Logger = None
) -> DataFrame:
    """
    Adds columns specifying which values are invalid

    Args:
        flow_cell: DataFrame containing all parsed flow cell data
        log: If logger is given, logs warnings for rows that are invalid

    Returns: Copy of original DataFrame with validity columns added

    """
    df = flow_cell.copy()

    # Cluster data can be below zero, which makes no sense
    invalid_cluster = flow_cell[FlowcellColumn.Clusters] < 0
    invalid_cluster_pf = flow_cell[FlowcellColumn.ClustersPF] < 0

    invalid_healthstatus = is_invalid_heathtype(df)

    # Cannot directly assign Series to DataFrame, as index might not match
    # Use of the `values` method is essential (error is silent without it)
    df = df.assign(
        **{
            Validate.ETLValidateClusters: invalid_cluster.values,
            Validate.ETLValidateClustersPF: invalid_cluster_pf.values,
            Validate.ETLValidateHeathStatus: invalid_healthstatus.values,
        }
    )

    if log is not None:
        if sum(invalid_cluster) > 0:
            log.warning(
                "{} runs had invalid Cluster flow cell "
                "values and are marked in column {}".format(
                    sum(invalid_cluster), Validate.ETLValidateClusters
                )
            )

        if sum(invalid_cluster_pf) > 0:
            log.warning(
                "{} runs had invalid ClusterPF flow cell "
                "values and are marked in column {}".format(
                    sum(invalid_cluster), Validate.ETLValidateClusters
                )
            )

        if sum(invalid_healthstatus) > 0:
            log.warning(
                "{} runs had invalid flow cell Health Status and are marked "
                "in column {}".format(
                    sum(invalid_healthstatus),
                    Validate.ETLValidateHeathStatus,
                )
            )

    return df


def is_invalid_heathtype(flowcell: DataFrame) -> Series:
    """
    In certain circumstances, an Illumina run in stuck on the Running health
    status. If the following conditions are met, the health status of a
    machine is invalid.

    * The Run does not have a start date
    * The Run has a completion date, but is marked as running
    * The Run has started more than 30 days ago

    Args:
        flowcell: The DataFrame containing the flow cell data

    Returns: True if the health status is invalid

    """
    running = flowcell[flowcell[FlowcellColumn.HealthType] == "RUNNING"]

    # A run that never started
    never_started = running[running[FlowcellColumn.StartDate].isna()]
    running = running.drop(never_started.index)

    # A run that completed, but is still running
    strange_completion = running[running[FlowcellColumn.CompletionDate].notna()]
    running = running.drop(strange_completion.index)

    # Run that has not completed, but has been running for more than 30 days
    now = pandas.Timestamp.now()
    since_started = now - running[FlowcellColumn.StartDate]
    days_running = since_started.dt.days
    running_too_long = running[days_running > 30]

    runs_to_fail = pandas.concat(
        [never_started, strange_completion, running_too_long]
    )

    # The order of the result will be the same as input DataFrame
    result = Series(False, index=flowcell.index)
    result[runs_to_fail.index] = True

    return result
