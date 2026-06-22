import qcetl.common
from qcetl.column import MetagenomicReportColumn as Column
from qcetl.metagenomicreport.parse import parse_record


class MetagenomicReportCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "metagenomicreport"
        self.schema_versions = {
            1: {
                self.name: {
                    Column.AddedReads: "i",
                    Column.AssignedReads: "i",
                    Column.Barcodes: "s",
                    Column.FileSWID: "s",
                    Column.Lane: "i",
                    Column.Name: "s",
                    Column.NewEstimatedReads: "i",
                    Column.Run: "s",
                    Column.TaxonomyId: "i",
                    Column.TaxonomyLevel: "s",
                    Column.FractionTotalReads: "f",
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
        self.primary_key = {
            1: {self.name: [Column.FileSWID, Column.TaxonomyId]}
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
                Column.Run: single_input["run"],
                Column.FileSWID: single_input["swid"],
            }
        }
