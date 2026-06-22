import json
import test.cachechecker
from qcetl.runscanner.illumina import RunScannerIlluminaCache


class CannedRunScannerIllumina(RunScannerIlluminaCache):
    """
    The actual class gets data from Run Scanner URL using `fetch`. For testing
    purposes, this class is over-written to load from local disk
    """

    def fetch(self):
        with open(self.url, "r") as f:
            return json.load(f)


def tests_181109_A00469_0016_AHGC37DMXX_runscanner():
    test.cachechecker.check(
        CannedRunScannerIllumina(
            "test/files/runscanner/illumina/runscanner_181109_A00469_0016_AHGC37DMXX.json"
        ),
        [{"run": "181109_A00469_0016_AHGC37DMXX", "status": "Amazing"}],
        {
            "flowcell": "test/files/runscanner/illumina/runscanner_181109_A00469_0016_AHGC37DMXX_flowcell.csv",
            "lane": "test/files/runscanner/illumina/runscanner_181109_A00469_0016_AHGC37DMXX_lane.csv",
        },
    )
