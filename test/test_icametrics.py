import json

import qcetl.icametrics
import test.cachechecker


def tests_ica_metrics():
    with open("test/files/icametrics/input.json", "r") as f:
        data = json.load(f)
    test.cachechecker.check(
        qcetl.icametrics.ICAMetricsCache(),
        data,
        {"icametrics": "test/files/icametrics/test_result.csv"},
    )
