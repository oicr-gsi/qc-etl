import pandas
from typing import Union

from qcetl.column import CrosscheckFingerprintsColumn as Column


def generate_matrix(cache: pandas.DataFrame) -> pandas.DataFrame:
    """
    The stored cache is in long format. This function converts it into a wide format
    that allows easy pairwise comparisons. The library name is the IUS, with
    underscore separators (run_lane_barcode)

    Args:
        cache: Whole or subset of cache DataFame

    Returns: Pairwise comparison DataFrame

    """
    left = (
        cache[Column.RunLeft]
        + "_"
        + cache[Column.LaneLeft].astype(str)
        + "_"
        + cache[Column.BarcodeLeft]
    )
    right = (
        cache[Column.RunRight]
        + "_"
        + cache[Column.LaneRight].astype(str)
        + "_"
        + cache[Column.BarcodeRight]
    )
    long = pandas.DataFrame(
        {"left": left, "right": right, Column.LODScore: cache[Column.LODScore]}
    )
    # `pivot` requires left and right column combination to be unique
    # Each comparison with library A, will have an A/A (left/right) comparison
    # Remove those duplicates, as they are all exactly the same (including LOD score)
    long = long.drop_duplicates(
        ["left", "right", Column.LODScore], keep="first"
    )
    return long.pivot("left", "right", Column.LODScore).reset_index()


def calculate_results(
    cache: pandas.DataFrame,
    lod_cutoff: Union[float, int],
    ambiguous_zone: Union[float, int, None] = None,
) -> pandas.Series:
    """
    Returns correct values for the RESULT column. The patient identities are derived
    from the library names. If the LOD score is equal or greater than the cutoff,
    the patient identities are expected to match. If the LOD score is below the cutoff,
    the patients identities are expected to the different. LOD scores close to 0 can be
    marked as AMBIGUOUS.


    Args:
        cache: Whole or subset of cache DataFame
        lod_cutoff: At what LOD score are patient identities expected to be the same
        ambiguous_zone: Range below and above an LOD score of zero at which results
            should be marked as ambiguous

    Returns: A series that can replace the RESULT column in the input cache.

    """
    # MISO Identity from the Library Alias
    id_regex = r"(^[a-zA-Z0-9]+_[a-zA-Z0-9]+)_"
    left_identity = cache[Column.LibraryLeft].str.extract(
        id_regex, expand=False
    )
    right_identity = cache[Column.LibraryRight].str.extract(
        id_regex, expand=False
    )
    df = pandas.DataFrame(
        {
            "left": left_identity,
            "right": right_identity,
            Column.LODScore: cache[Column.LODScore],
        }
    )

    def call(row):
        lod = row[Column.LODScore]
        if ambiguous_zone is not None:
            if abs(lod) <= abs(ambiguous_zone):
                return "AMBIGUOUS"

        if row["left"] == row["right"]:
            if lod >= lod_cutoff:
                return "EXPECTED_MATCH"
            else:
                return "UNEXPECTED_MATCH"
        else:
            if lod >= lod_cutoff:
                return "UNEXPECTED_MISMATCH"
            else:
                return "EXPECTED_MISMATCH"

    return df.apply(call, axis=1)
