import qcetl.common
from qcetl.column import AnalysisDellyColumn as DellyColumn

from qcetl.analysis_delly.parse import parse_record


class AnalysisDellyCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_delly"
        self.schema_versions = {
            1: {
                "analysis_delly": {
                    DellyColumn.Donor: "s",
                    DellyColumn.GroupID: "s",
                    DellyColumn.LibraryDesign: "s",
                    DellyColumn.Reference: "s",
                    DellyColumn.TissueOrigin: "s",
                    DellyColumn.TissueType: "s",
                    DellyColumn.MergedPineryLimsID: "as",
                    DellyColumn.WorkflowRunSWID: "s",
                    DellyColumn.NumCalls: "i",
                    DellyColumn.NumPASS: "i",
                    DellyColumn.NumBND: "i",
                    DellyColumn.NumDEL: "i",
                    DellyColumn.NumDUP: "i",
                    DellyColumn.NumINS: "i",
                    DellyColumn.NumINV: "i",
                }
            }
        }
        self.columns = {
            1: {
                "analysis_delly": DellyColumn,
            }
        }
        self.input_format = {
            "donor": "s",
            "file": "p",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "reference": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {
            1: {
                "analysis_delly": [
                    DellyColumn.WorkflowRunSWID,
                ]
            }
        }
        self.input_key = {1: ("swid", DellyColumn.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(
            single_input["file"],
        )
        return {
            1: {
                "analysis_delly": df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_delly": {
                DellyColumn.Donor: single_input["donor"],
                DellyColumn.GroupID: single_input["group_id"],
                DellyColumn.LibraryDesign: single_input["library_design"],
                DellyColumn.MergedPineryLimsID: single_input["pinery_lims_ids"],
                DellyColumn.TissueOrigin: single_input["tissue_origin"],
                DellyColumn.TissueType: single_input["tissue_type"],
                DellyColumn.WorkflowRunSWID: single_input["swid"],
                DellyColumn.Reference: single_input.get("reference", "Unknown"),
            }
        }
