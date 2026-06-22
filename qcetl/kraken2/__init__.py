import qcetl.common
from qcetl.column import Kraken2Column as Column
from qcetl.kraken2.parse import parse_record


class Kraken2Cache(qcetl.common.Cache):
    def __init__(self):
        self.name = "kraken2"
        self.schema_versions = {
            1: {
                self.name: {
                    Column.Barcodes: "s",
                    Column.Count: "i",
                    Column.CountAtClade: "i",
                    Column.FileSWID: "s",
                    Column.Lane: "i",
                    Column.Name: "s",
                    Column.Parent: "s",
                    Column.PercentAtClade: "f",
                    Column.PineryLimsID: "s",
                    Column.Rank: "s",
                    Column.Reference: "s",
                    Column.Run: "s",
                    Column.TaxonomicID: "i",
                }
            }
        }
        self.columns = {1: {self.name: Column}}
        self.input_format = {
            "file": "p",
            "swid": "s",
            "barcodes": "s",
            "lane": "i",
            "pinery_lims_id": "s",
            "reference": "s",
            "run": "s",
        }
        self.primary_key = {
            1: {self.name: [Column.FileSWID, Column.TaxonomicID]}
        }
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
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.Reference: single_input["reference"],
                Column.FileSWID: single_input["swid"],
            }
        }
