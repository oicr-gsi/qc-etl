import qcetl.common
from qcetl.column import AnalysisStarFusionColumn as Column

from qcetl.analysis_starfusion.parse import parse_record


class AnalysisStarFusionCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_starfusion"
        self.schema_versions = {
            1: {
                "analysis_starfusion": {
                    Column.Donor: "s",
                    Column.GroupID: "s",
                    Column.LibraryDesign: "s",
                    Column.Reference: "s",
                    Column.TissueOrigin: "s",
                    Column.TissueType: "s",
                    Column.MergedPineryLimsID: "as",
                    Column.WorkflowRunSWID: "s",
                    Column.NumRecords: "i",
                }
            }
        }
        self.columns = {
            1: {
                "analysis_starfusion": Column,
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
                "analysis_starfusion": [
                    Column.WorkflowRunSWID,
                ]
            }
        }
        self.input_key = {1: ("swid", Column.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(
            single_input["file"],
        )
        return {
            1: {
                "analysis_starfusion": df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_starfusion": {
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.LibraryDesign: single_input["library_design"],
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.WorkflowRunSWID: single_input["swid"],
                Column.Reference: single_input.get("reference", "Unknown"),
            }
        }
