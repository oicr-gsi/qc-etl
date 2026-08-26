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
                    Column.Metric: "s",
                    Column.Value: "f",
                    Column.Barcode: "s",
                    Column.Index: "s",
                    Column.Detail: "s",
                    Column.Library: "s",
                    Column.PineryLimsID: "s",
                }
            }
        }
        self.columns = {1: {"ultimamethylcontrol": Column}}
        self.input_format = {
            "path": "p",
            "barcode": "s",
            "run": "s",
            "pinery_lims_id": "s",
        }
        self.primary_key = {
            1: {"ultimamethylcontrol": [Column.PineryLimsID, Column.Detail]}
        }
        self.input_key = {1: ("pinery_lims_id", Column.PineryLimsID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {"ultimamethylcontrol": parse_record(single_input["path"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ultimamethylcontrol": {
                Column.Run: single_input["run"],
                Column.Barcode: single_input["barcode"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
            }
        }
