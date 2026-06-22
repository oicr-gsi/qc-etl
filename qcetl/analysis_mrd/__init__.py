import qcetl.common
from qcetl.column import AnalysisMrdColumn as MrdColumn
from qcetl.analysis_mrd.parse import parse_record


class AnalysisMrdCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_mrd"
        self.schema_versions = {
            2: {
                "analysis_mrd": {
                    MrdColumn.SampleName: "s",
                    MrdColumn.SampleCoverage: "f",
                    MrdColumn.MedianVAF: "f",
                    MrdColumn.SampleSNPs: "f",
                    MrdColumn.SitesDetected: "f",
                    MrdColumn.MeanNoise: "f",
                    MrdColumn.DetectionRate: "f",
                    MrdColumn.TumourFractionEstimate: "f",
                    MrdColumn.TumourFractionAdjusted: "f",
                    MrdColumn.ZScore: "f",
                    MrdColumn.PValue: "f",
                    MrdColumn.DatasetDetectionCutoff: "f",
                    MrdColumn.FalsePositiveRate: "f",
                    MrdColumn.CancerDetected: "b",
                    MrdColumn.Donor: "s",
                    MrdColumn.GroupID: "s",
                    MrdColumn.LibraryDesign: "s",
                    MrdColumn.MergedPineryLimsID: "as",
                    MrdColumn.Reference: "s",
                    MrdColumn.TissueOrigin: "s",
                    MrdColumn.TissueType: "s",
                    MrdColumn.WorkflowRunSWID: "s",
                }
            }
        }
        self.columns = {
            2: {
                "analysis_mrd": MrdColumn,
            }
        }
        self.input_format = {
            "mrd_txt_file": "p",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "reference": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {
            2: {
                "analysis_mrd": [
                    MrdColumn.WorkflowRunSWID,
                ],
            }
        }
        self.input_key = {2: ("swid", MrdColumn.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        analysis_mrd_df = parse_record(
            single_input["mrd_txt_file"],
        )
        return {
            2: {
                "analysis_mrd": analysis_mrd_df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_mrd": {
                MrdColumn.Donor: single_input["donor"],
                MrdColumn.GroupID: single_input["group_id"],
                MrdColumn.LibraryDesign: single_input["library_design"],
                MrdColumn.MergedPineryLimsID: single_input["pinery_lims_ids"],
                MrdColumn.Reference: single_input.get("reference", "Unknown"),
                MrdColumn.TissueOrigin: single_input["tissue_origin"],
                MrdColumn.TissueType: single_input["tissue_type"],
                MrdColumn.WorkflowRunSWID: single_input["swid"],
            }
        }
