import qcetl.common
from qcetl.column import SequenzaColumn as Column
from qcetl.sequenza.parse import parse_record


class SequenzaCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "sequenza"
        self.schema_versions = {
            2: {
                self.name: {
                    Column.Cellularity: "f",
                    Column.Gamma: "i",
                    Column.Ploidy: "f",
                    Column.SLPP: "f",
                    Column.FileSWID: "s",
                    Column.Donor: "s",
                    Column.GroupID: "s",
                    Column.LibraryDesign: "s",
                    Column.MergedPineryLimsID: "as",
                    Column.TissueOrigin: "s",
                    Column.TissueType: "s",
                }
            }
        }
        self.columns = {2: {self.name: Column}}
        self.input_format = {
            "input": "p",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {
            2: {
                self.name: [
                    Column.FileSWID,
                    Column.Ploidy,
                    Column.Gamma,
                ]
            }
        }
        self.input_key = {2: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {2: {self.name: parse_record(single_input["input"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.LibraryDesign: single_input["library_design"],
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.FileSWID: single_input["swid"],
            }
        }
