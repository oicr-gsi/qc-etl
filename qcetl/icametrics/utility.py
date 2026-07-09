import os
import re
import glob
import numpy as np
import pandas as pd

__all__ = [
    "calculate_mean_cov", "calculate_dup_del_ratio",
]


def calculate_dup_del_ratio(data: dict) -> None:
    """
    Calculate the amplification-to-deletion ratio and store it in-place.

    This function removes the values associated with
    'Number of amplifications' and 'Number of deletions' from the
    input dictionary, calculates their ratio, and stores the result
    as a string in the dictionary.

    If no amplification count is present, the ratio defaults to '0'.

    Args:
        data: Dictionary containing copy number variation metrics

    Returns:
        None. The input dictionary is modified in-place.
    """
    try:
        amps = float(data.pop('Number of amplifications', None))
        dels = float(data.pop('Number of deletions', None))
        dupdelratio = str(round(amps/dels, 2))
    except Exception:
        dupdelratio = '0'
    data['dupdelratio'] = dupdelratio


def calculate_mean_cov(root_dir: str, p_num: str, name: str, val_type="sub", fail=False):
    """
    Calculate the average coverage depth or failing interval percentage
    from a metrics file for a given sample.

    The function searches for the appropriate metrics file under the
    provided root directory using the patient/sample identifier and
    metric name.

    Args:
        root_dir: Root directory containing metrics subdirectories.
        p_num: P# used to locate the metrics file.
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
    file_locs = glob.glob(os.path.join(root_dir, "*{}*".format(p_num), "metrics_*", "*{}*.{}".format(name, "failing_intervals" if fail else "per_base")))
    file_loc = [loc for loc in file_locs if ("NM_filtered" in loc) == (val_type == "full")][0]

    if fail:
        lines = open(file_loc, 'r').readlines()
        avg_val = float(re.sub('Failing intervals represent (.*)%.*', r'\1', lines[-1].rstrip()))
    else:
        df = pd.read_csv(os.path.join(file_loc), delimiter='\t')
        avg_val = np.mean(df['Depth'])
    return round(avg_val, 2)
