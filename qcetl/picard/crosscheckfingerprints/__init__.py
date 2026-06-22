import qcetl.common
from qcetl.column import (
    CrosscheckFingerprintsCallSwapColumn as SwapCol,
)
from qcetl.picard.crosscheckfingerprints.parse import (
    parse_record,
    filter_swaps,
)


class CrosscheckFingerprintsCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "crosscheckfingerprints"
        self.schema_versions = {
            4: {
                "filterswaps": {
                    SwapCol.FileSWID: "s",
                    SwapCol.QueryLibrary: "s",
                    SwapCol.QueryBarcode: "s",
                    SwapCol.QueryLane: "i",
                    SwapCol.QueryRun: "s",
                    SwapCol.MatchLibrary: "s",
                    SwapCol.MatchBarcode: "s",
                    SwapCol.MatchLane: "i",
                    SwapCol.MatchRun: "s",
                    SwapCol.LODScore: "f",
                    SwapCol.ClosestLibrariesCount: "i",
                    SwapCol.SameIdentity: "b",
                },
            }
        }
        self.columns = {4: {"filterswaps": SwapCol}}
        self.input_format = {"file": "p", "swid": "s", "version": "s"}
        self.primary_key = {
            4: {
                "filterswaps": [
                    SwapCol.FileSWID,
                    SwapCol.QueryLibrary,
                    SwapCol.QueryBarcode,
                    SwapCol.QueryLane,
                    SwapCol.QueryRun,
                    SwapCol.MatchLibrary,
                    SwapCol.MatchBarcode,
                    SwapCol.MatchLane,
                    SwapCol.MatchRun,
                ],
            }
        }
        self.input_key = {4: ("swid", SwapCol.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        cache = parse_record(single_input["file"], single_input["version"])
        swaps = filter_swaps(cache)
        if schema_version == 4:
            return {"filterswaps": swaps}
        else:
            raise ValueError("Unknown version")

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "filterswaps": {SwapCol.FileSWID: single_input["swid"]},
        }
