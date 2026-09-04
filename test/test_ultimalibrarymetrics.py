import json
import test.cachechecker
from qcetl.ultimalibrarymetrics import UltimaLibraryMetricsCache


class CannedUltimaLibraryMetrics(UltimaLibraryMetricsCache):
    """
    The actual class gets data from the Nexus API using `fetch`. For testing
    purposes, this class is over-written to load from local disk
    """

    def fetch(self, run_id):
        with open(self.host, "r") as f:
            return json.load(f)


def tests_ultimalibrarymetrics():
    test.cachechecker.check(
        CannedUltimaLibraryMetrics(
            host="test/files/ultimalibrarymetrics/sample_response.json"
        ),
        [
            {
                "run": "RUN0001",
                "ultima_library_id": "TEST_SAMPLE_1",
                "pinery_lims_id": "ID1",
            },
            {
                "run": "RUN0001",
                "ultima_library_id": "TEST_SAMPLE_2",
                "pinery_lims_id": "ID2",
            },
            {
                "run": "RUN0001",
                "ultima_library_id": "TEST_SAMPLE_3",
                "pinery_lims_id": "ID3",
            },
        ],
        {"ultimalibrarymetrics": "test/files/ultimalibrarymetrics/RUN0001.csv"},
    )
