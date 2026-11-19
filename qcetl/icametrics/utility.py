import os
import re
import glob
import numpy as np
import pandas as pd

from qcetl.icametrics.constants import sex_to_karyotype

__all__ = [
    "calculate_mean_cov",
    "calculate_dup_del_ratio",
    "check_sex_match",
    "to_float",
]


def calculate_dup_del_ratio(data: dict) -> None:
    """
    Calculate the amplification-to-deletion ratio and store it in-place.

    This function removes the values associated with
    'Number of amplifications' and 'Number of deletions' from the
    input dictionary, calculates their ratio, and stores the result
    in the dictionary.

    If there are no deletions, or either count is missing or not numeric
    (e.g. no CNV output), the ratio is undefined and set to NaN.

    Args:
        data: Dictionary containing copy number variation metrics

    Returns:
        None. The input dictionary is modified in-place.
    """
    amps = data.pop("Number of amplifications", None)
    dels = data.pop("Number of deletions", None)
    try:
        dupdelratio = round(float(amps) / float(dels), 2)
    except (TypeError, ValueError, ZeroDivisionError):
        dupdelratio = np.nan
    data["dupdelratio"] = dupdelratio


def calculate_mean_cov(pp_dir: str, name: str, val_type="sub", fail=False):
    """
    Calculate the average coverage depth or failing interval percentage
    from a metrics file for a given sample.

    The function searches for the appropriate metrics file under the
    provided root directory using the patient/sample identifier and
    metric name.

    Args:
        pp_dir: Pipeline directory containing metrics subdirectories.
        name: Name pattern used to identify the target metrics file.
        val_type : Type of metrics file to use:
            - "sub" (default): use non-NM_filtered files
            - "full": use NM_filtered files
        fail : If True, extract the failing interval percentage from a
            `.failing_intervals` file. Otherwise, calculate the mean
            coverage depth from a `.per_base` TSV file.

    Returns
        float. Rounded average value to 2 decimal places:
            - mean depth coverage when `fail=False`
            - failing interval percentage when `fail=True`
    """
    file_locs = glob.glob(
        os.path.join(
            pp_dir,
            "metrics_*",
            "*{}*.{}".format(name, "failing_intervals" if fail else "per_base"),
        )
    )
    try:
        file_loc = [
            loc
            for loc in file_locs
            if ("NM_filtered" in loc) == (val_type == "full")
        ][0]
    except Exception:
        return np.nan

    if fail:
        lines = open(file_loc, "r").readlines()
        avg_val = float(
            re.sub(
                "Failing intervals represent (.*)%.*", r"\1", lines[-1].rstrip()
            )
        )
    else:
        df = pd.read_csv(os.path.join(file_loc), delimiter="\t")
        avg_val = np.mean(df["Depth"])
    return round(avg_val, 2)


def to_float(value) -> float:
    """
    Convert a metric value to float, returning NaN if it is missing or not
    numeric.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan


def check_sex_match(expected_sex: str, observed_sex: str) -> float:
    """
    Compare the donor sex from MISO against the sex karyotype called by the
    DRAGEN Ploidy Estimator.

    MISO donor sex (DonorSex enum) is MALE, FEMALE, OTHER, UNSPECIFIED or
    UNKNOWN. MALE expects XY and FEMALE expects XX; the others have no
    expected karyotype, so no check is done.

    Any karyotype DRAGEN calls other than the expected one is a
    mismatch, including sex chromosome aneuploidies (e.g. XXY, X0).
    If DRAGEN did not call a karyotype, the value is empty or NA and 
    there is nothing to compare.

    The result is a float (qf) so that an undetermined comparison can be NaN 
    (a boolean column cannot hold missing values).

    Args:
        expected_sex: Donor sex from MISO (e.g. Male, Female, Unknown)
        observed_sex: DRAGEN `Ploidy estimation` value (e.g. XX, XY, XXY)

    Returns:
        1.0 if they match, 0.0 if they do not, NaN if the MISO donor sex
        has no expected karyotype or DRAGEN called no karyotype
    """
    expected = sex_to_karyotype.get(str(expected_sex).strip().lower())
    if expected is None or pd.isna(observed_sex):
        return np.nan
    observed = str(observed_sex).strip().upper()
    if observed in ("", "NA"):
        return np.nan
    return 1.0 if observed == expected else 0.0
