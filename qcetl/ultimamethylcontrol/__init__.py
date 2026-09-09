import qcetl.common
from qcetl.column import UltimaMethylControlColumn as Column
from qcetl.ultimamethylcontrol.parse import parse_record


class UltimaMethylControlCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "ultimamethylcontrol"
        self.schema_versions = {
            1: {
                "ultimamethylcontrol": {
                    Column.Run: "s",
                    Column.PercentMethylationMeanLambda: "qf",
                    Column.PercentMethylationMeanPuc19: "qf",
                    Column.PercentMethylationMeanHg: "qf",
                    Column.CoverageMeanLambda: "qf",
                    Column.CoverageMeanPuc19: "qf",
                    Column.CoverageMeanHg: "qf",
                    Column.BarcodeSequence: "s",
                    Column.BarcodeName: "qs",
                    Column.PineryLimsID: "s",
                }
            }
        }
        self.columns = {1: {"ultimamethylcontrol": Column}}
        self.input_format = {
            "path": "p",
            "barcode": "s",
            "barcode_name": "qs",
            "run": "s",
            "pinery_lims_id": "s",
        }
        self.primary_key = {1: {"ultimamethylcontrol": [Column.PineryLimsID]}}
        self.input_key = {1: ("pinery_lims_id", Column.PineryLimsID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {"ultimamethylcontrol": parse_record(single_input["path"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ultimamethylcontrol": {
                Column.Run: single_input["run"],
                Column.BarcodeSequence: single_input["barcode"],
                Column.BarcodeName: single_input.get("barcode_name"),
                Column.PineryLimsID: single_input["pinery_lims_id"],
            }
        }
