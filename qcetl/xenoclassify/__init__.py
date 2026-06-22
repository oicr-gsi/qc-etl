import qcetl.common
from qcetl.column import XenoclassifyColumn as Column
from qcetl.xenoclassify.parse import parse_record


class XenoclassifyCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "xenoclassify"
        self.schema_versions = {
            1: {
                self.name: {
                    Column.FileSWID: "s",
                    Column.Run: "s",
                    Column.Lane: "i",
                    Column.Barcodes: "s",
                    Column.GraftReads: "i",
                    Column.HostReads: "i",
                    Column.BothReads: "i",
                    Column.NeitherReads: "i",
                }
            }
        }
        self.columns = {1: {self.name: Column}}
        self.input_format = {
            "file": "p",
            "swid": "s",
            "barcodes": "s",
            "lane": "i",
            "run": "s",
        }
        self.primary_key = {1: {self.name: [Column.FileSWID]}}
        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {self.name: parse_record(single_input["file"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                Column.Barcodes: single_input["barcodes"],
                Column.Lane: single_input["lane"],
                Column.Run: single_input["run"],
                Column.FileSWID: single_input["swid"],
            }
        }
