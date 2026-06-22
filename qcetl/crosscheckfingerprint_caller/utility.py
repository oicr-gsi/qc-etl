from pandas import DataFrame
from qcetl.column import CrosscheckFingerprintCallerCallsColumn as Clmn


def consistent_lims_id_calls(
    calls: DataFrame, unique_lims_id: bool
) -> DataFrame:
    """
    Ensure that a swap call is consistent across multi-row lims ids.

    Swap calls may happen multiple times for the same lims id, as it is in multiple groupings
    (project, case, donor, batch). This means that a swap may be called in one set of groupings and not another.
    This utility function sets all swap calls for a lims id to true if there is a swap in at least one grouping.

    Args:
        calls: The loaded calls DataFrame
        unique_lims_id: Use this if you care to have one row per lims id. An arbitrary grouping will be kept.

    Returns: A calls DataFrame where swap calls are consistent across all groupings

    """
    grp = calls.groupby(Clmn.PineryLimsID)[Clmn.SwapCall].any()
    grp = grp.to_frame("swap_call_grouped")
    grp = calls.merge(grp, left_on=Clmn.PineryLimsID, right_index=True)
    grp = grp.drop(columns=Clmn.SwapCall)
    grp = grp.rename(columns={"swap_call_grouped": Clmn.SwapCall})

    if unique_lims_id:
        grp = grp.drop_duplicates(Clmn.PineryLimsID)

    return grp
