import pandas

from qcetl.column import (
    CrosscheckFingerprintsColumn as Column,
    CrosscheckFingerprintsCallSwapColumn as CallSwapColumn,
)


def get_ius(rg_id):
    """
    IUS information is embedded in the output and is derived from the BAM @RG:ID field.
    STAR (ID:{ius[0]}_{ius[1]}_{ius[2]}) and bwa mem (ID:{ius[0]}-{ius[2]}_{ius[1]})
    differ in how the IUS is stored.

    Args:
        rg_id: The string in the LEFT_GROUP_VALUE or RIGHT_GROUP_VALUE cell

    Returns: Values associated to their correct IUS fields

    """
    # bwa mem
    if rg_id[-1].isdigit():
        run, rest = rg_id.split("-", 1)
        barcode, lane = rest.split("_")
    # STAR
    else:
        run, lane, barcode = rg_id.rsplit("_", 2)

    return {"run": run, "lane": lane, "barcode": barcode}


def get_ius_library(rg_id):
    """
    For input from crosscheckfingerprintCollector, the library + ius are in the readgroup field

    Unfortunately, the underscore character is used within library and run name as well as the
    separator of the whole string (MYR_0127_01_LB02-01_230113_A00469_0414_AHYH5MDSX3_3_TCCGCGAA-CTTCGCCT).
    The library can be in V1 or V2 style. The assumption will be that the run name in Illumina (has
    3 underscores). If this breaks in the future, I hope that all library aliases are V2.


    Args:
        rg_id: The string in the LEFT_GROUP_VALUE or RIGHT_GROUP_VALUE cell

    Returns: A dictionary of the seperated fields

    """
    rest, lane, barcode = rg_id.rsplit("_", 2)
    library, *run_list = rest.rsplit("_", 4)

    return {
        "library": library,
        "run": "_".join(run_list),
        "lane": lane,
        "barcode": barcode,
    }


def parse_record(path: str, version: str) -> pandas.DataFrame:
    """
    Parse crosscheckFingerprints into a DataFrame

    Args:
        path: Path to Picard output file
        version: Which workflow version is the input file coming from

    Returns:

    """
    df = pandas.read_csv(path, sep="\t", comment="#")

    if version == "1.0":
        left = pandas.DataFrame(list(df[Column.GroupValueLeft].apply(get_ius)))
        df[Column.RunLeft] = left["run"]
        df[Column.LaneLeft] = left["lane"]
        df[Column.BarcodeLeft] = left["barcode"]

        right = pandas.DataFrame(
            list(df[Column.GroupValueRight].apply(get_ius))
        )
        df[Column.RunRight] = right["run"]
        df[Column.LaneRight] = right["lane"]
        df[Column.BarcodeRight] = right["barcode"]
    else:
        left = pandas.DataFrame(
            list(df[Column.GroupValueLeft].apply(get_ius_library))
        )
        df[Column.RunLeft] = left["run"]
        df[Column.LaneLeft] = left["lane"]
        df[Column.BarcodeLeft] = left["barcode"]
        df[Column.LibraryLeft] = left["library"]

        right = pandas.DataFrame(
            list(df[Column.GroupValueRight].apply(get_ius_library))
        )
        df[Column.RunRight] = right["run"]
        df[Column.LaneRight] = right["lane"]
        df[Column.BarcodeRight] = right["barcode"]
        df[Column.LibraryRight] = right["library"]

    return df


def filter_swaps(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    Find swaps in the parsed CrosscheckFingerprints output.

    Args:
        df: The parsed DataFrame from the input file

    Returns:

    """
    rename = {
        Column.LibraryLeft: CallSwapColumn.QueryLibrary,
        Column.BarcodeLeft: CallSwapColumn.QueryBarcode,
        Column.LaneLeft: CallSwapColumn.QueryLane,
        Column.RunLeft: CallSwapColumn.QueryRun,
        Column.LibraryRight: CallSwapColumn.MatchLibrary,
        Column.BarcodeRight: CallSwapColumn.MatchBarcode,
        Column.LaneRight: CallSwapColumn.MatchLane,
        Column.RunRight: CallSwapColumn.MatchRun,
        Column.LODScore: CallSwapColumn.LODScore,
    }
    swap = df[list(rename)].copy()
    swap = swap.rename(columns=rename)
    swap = swap.sort_values(
        [CallSwapColumn.QueryLibrary, CallSwapColumn.LODScore], ascending=False
    )
    # This nasty regex gets the MISO Identity from the MISO Alias
    identity_regex = r"(^[A-Z0-9]+_\d+)_.*$"
    swap[CallSwapColumn.SameIdentity] = swap[
        CallSwapColumn.MatchLibrary
    ].str.extract(identity_regex) == swap[
        CallSwapColumn.QueryLibrary
    ].str.extract(
        identity_regex
    )
    swap = swap[
        swap[CallSwapColumn.QueryLibrary] != swap[CallSwapColumn.MatchLibrary]
    ]
    # Empty dictionary with the renamed columns _ those added by `closest_lib`
    empty = pandas.DataFrame(
        columns=list(rename.values())
        + [CallSwapColumn.ClosestLibrariesCount, CallSwapColumn.SameIdentity]
    )
    result = []
    for _, d in swap.groupby(CallSwapColumn.QueryLibrary):
        c = closest_lib(d)
        if c is None:
            c = empty
        result.append(c)
    if len(result) == 0:
        return empty
    else:
        return pandas.concat(result)


def closest_lib(input_df: pandas.DataFrame):
    """
    The `input_df` must be sored by LOD_SCORE (descending).

    For each library, traverses until it finds an expected match (same MISO Identity).
    If there was no swap, only one library should have been traversed. If there is
    only one library with that MISO Identity, return the closest library.

    Args:
        input_df: The parsed DataFrame from the input file

    Returns:
    """
    # There must be at least two libraries for swap comparison
    if len(input_df) < 2:
        return None
    # Index will be used with `iloc` call, so has to go from 0 to number of rows
    lib_df = input_df.reset_index(drop=True)
    # Libraries that came from the same patient
    same_ident_df = lib_df[lib_df[CallSwapColumn.SameIdentity]]
    # Patient has only one library sequenced
    # Take the first hit (should not match, as it is from different patient)
    if same_ident_df.empty:
        # The closest library
        return_df = lib_df.head(1).copy()
        # As there are no expected close libraries, this is always 0
        return_df[CallSwapColumn.ClosestLibrariesCount] = 0
    else:
        # Get libraries up to and including the first that came from the same patient
        return_df = lib_df.iloc[: same_ident_df.index[0] + 1].copy()
        return_df[CallSwapColumn.ClosestLibrariesCount] = len(return_df)

    return return_df
