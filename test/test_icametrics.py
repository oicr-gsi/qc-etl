import json

import gsiqcetl.icametrics
import test.cachechecker


def tests_ica_metrics():
    with open("test/files/icametrics/input.json", "r") as f:
        data = json.load(f)
    test.cachechecker.check(
        gsiqcetl.icametrics.ICAMetricsCache(),
        data,
        {"icametrics": "test/files/test_result.csv"},
    )
