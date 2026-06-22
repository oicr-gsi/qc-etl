from typing import Union

from pandas import DataFrame

from qcetl.common import InvalidRecordError
from pinery.column import HeredityColumn, SamplesColumn, SampleCategory


def find_parent_with_sample_category(
    start_id: str,
    sample_category: SampleCategory,
    heredity_df: DataFrame,
    samples_df: DataFrame,
) -> Union[str, None]:
    """
    Find the parent with the specified Sample Category.

    Args:
        start_id: For which MISO ID is the parent being sought
        sample_category: Which Sample Category should the parent have
        heredity_df: The heredity DataFrame
        samples_df: The samples DataFrame

    Returns: The MISO ID of the parent. If a parent with the Sample Category
        cannot be found, None is returned.

    Raises:
        KeyError: If starting ID does not exit

    """
    if start_id not in samples_df.index:
        raise KeyError("MISO ID {} does not exist".format(start_id))

    while True:
        next_parent = find_parent(start_id, heredity_df)

        if next_parent is None:
            return None
        elif (
            samples_df.loc[next_parent, SamplesColumn.SampleCategory]
            == sample_category.value
        ):
            return next_parent
        else:
            start_id = next_parent


def find_parent(child_id: str, heredity_df: DataFrame) -> Union[str, None]:
    """
    Given the child's MISO ID, return the parent's ID.

    Args:
        child_id: MISO ID
        heredity_df: The heredity DataFrame from the parse module

    Returns: If no parents exist (because the ID is root or ID does not exist)
        None is returned, otherwise the parent ID is returned

    Raises:
        InvalidRecordError: If more than one parent is found. All MISO
            sample child:parent relationships are many:one.
    """
    try:
        result = heredity_df.loc[
            (child_id, "parents"), HeredityColumn.HeredityID
        ]
    except KeyError:
        return None

    if len(result) == 1:
        return result.iloc[0]
    else:
        raise InvalidRecordError(
            "Child ID {} has more than one parent: {}".format(child_id, result)
        )
