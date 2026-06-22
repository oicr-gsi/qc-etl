import qcetl.common
from qcetl.column import AnalysisRSEMColumn as RSEMColumn

from qcetl.analysis_rsem.parse import parse_record


class AnalysisRSEMCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_rsem"
        self.schema_versions = {
            1: {
                "analysis_rsem": {
                    RSEMColumn.Donor: "s",
                    RSEMColumn.GroupID: "s",
                    RSEMColumn.LibraryDesign: "s",
                    RSEMColumn.Reference: "s",
                    RSEMColumn.TissueOrigin: "s",
                    RSEMColumn.TissueType: "s",
                    RSEMColumn.MergedPineryLimsID: "as",
                    RSEMColumn.WorkflowRunSWID: "s",
                    RSEMColumn.TotalNumTranscripts: "i",
                    RSEMColumn.PctNonZeroTranscripts: "f",
                    RSEMColumn.Q0: "f",
                    RSEMColumn.Q0_05: "f",
                    RSEMColumn.Q0_1: "f",
                    RSEMColumn.Q0_25: "f",
                    RSEMColumn.Q0_5: "f",
                    RSEMColumn.Q0_75: "f",
                    RSEMColumn.Q0_9: "f",
                    RSEMColumn.Q0_95: "f",
                    RSEMColumn.Q1: "f",
                }
            }
        }
        self.columns = {
            1: {
                "analysis_rsem": RSEMColumn,
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
                "analysis_rsem": [
                    RSEMColumn.WorkflowRunSWID,
                ]
            }
        }
        self.input_key = {1: ("swid", RSEMColumn.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(
            single_input["file"],
        )
        return {
            1: {
                "analysis_rsem": df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_rsem": {
                RSEMColumn.Donor: single_input["donor"],
                RSEMColumn.GroupID: single_input["group_id"],
                RSEMColumn.LibraryDesign: single_input["library_design"],
                RSEMColumn.MergedPineryLimsID: single_input["pinery_lims_ids"],
                RSEMColumn.TissueOrigin: single_input["tissue_origin"],
                RSEMColumn.TissueType: single_input["tissue_type"],
                RSEMColumn.WorkflowRunSWID: single_input["swid"],
                RSEMColumn.Reference: single_input.get("reference", "Unknown"),
            }
        }
