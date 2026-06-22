import qcetl.common
from qcetl.column import MutetctCallabilityColumn as Column
from qcetl.mutectcallability.parse import parse_record


class MutectCallabilityCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "mutectcallability"
        self.schema_versions = {
            1: {
                "mutectcallability": {
                    Column.Callability: "f",
                    Column.Donor: "s",
                    Column.Fail: "i",
                    Column.FileSWID: "s",
                    Column.GroupID: "s",
                    Column.LibraryDesign: "s",
                    Column.NormalMinCoverage: "f",
                    Column.Pass: "i",
                    Column.MergedPineryLimsID: "as",
                    Column.Project: "s",
                    Column.Reference: "s",
                    Column.TissueOrigin: "s",
                    Column.TissueType: "s",
                    Column.TumorMinCoverage: "f",
                }
            }
        }
        self.columns = {1: {"mutectcallability": Column}}
        self.input_format = {
            "donor": "s",
            "file": "p",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "project": "s",
            "reference": "s",
            "swid": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
        }
        self.primary_key = {1: {"mutectcallability": [Column.FileSWID]}}
        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {"mutectcallability": parse_record(single_input["file"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "mutectcallability": {
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.LibraryDesign: single_input["library_design"],
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.Project: single_input["project"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.FileSWID: single_input["swid"],
                Column.Reference: single_input.get("reference", "Unknown"),
            }
        }
