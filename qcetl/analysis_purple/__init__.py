import qcetl.common
from qcetl.column import AnalysisPurpleColumn as PurpleColumn
from qcetl.analysis_purple.parse import parse_record


class AnalysisPurpleCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_purple"
        self.schema_versions = {
            3: {
                "analysis_purple": {
                    PurpleColumn.Score: "f",
                    PurpleColumn.Purity: "f",
                    PurpleColumn.MinPurity: "f",
                    PurpleColumn.MaxPurity: "f",
                    PurpleColumn.Ploidy: "f",
                    PurpleColumn.MinPloidy: "f",
                    PurpleColumn.MaxPloidy: "f",
                    PurpleColumn.DiploidProportion: "f",
                    PurpleColumn.MinDiploidProportion: "f",
                    PurpleColumn.MaxDiploidProportion: "f",
                    PurpleColumn.PolyclonalProportion: "f",
                    PurpleColumn.Status: "s",
                    PurpleColumn.WholeGenomeDuplication: "b",
                    PurpleColumn.msStatus: "s",
                    PurpleColumn.Tml: "f",
                    PurpleColumn.TmlStatus: "s",
                    PurpleColumn.TmbStatus: "s",
                    PurpleColumn.TmbPerMb: "f",
                    PurpleColumn.WorkflowRunSWID: "s",
                    PurpleColumn.Donor: "s",
                    PurpleColumn.GroupID: "s",
                    PurpleColumn.LibraryDesign: "s",
                    PurpleColumn.MergedPineryLimsID: "as",
                    PurpleColumn.Reference: "s",
                    PurpleColumn.TissueOrigin: "s",
                    PurpleColumn.TissueType: "s",
                    PurpleColumn.Pga: "i",
                    PurpleColumn.QCStatus: "s",
                    PurpleColumn.CopyNumberSegments: "i",
                    PurpleColumn.Contamination: "f",
                }
            }
        }
        self.columns = {
            3: {
                "analysis_purple": PurpleColumn,
            }
        }
        self.input_format = {
            "purity_tsv_file": "p",
            "cnv_somatic_file": "p",
            "qc_file": "p",
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
            3: {
                "analysis_purple": [
                    PurpleColumn.WorkflowRunSWID,
                ],
            }
        }
        self.input_key = {3: ("swid", PurpleColumn.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        analysis_purple_df = parse_record(
            single_input["purity_tsv_file"],
            single_input["cnv_somatic_file"],
            single_input["qc_file"],
        )
        return {
            3: {
                "analysis_purple": analysis_purple_df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_purple": {
                PurpleColumn.Donor: single_input["donor"],
                PurpleColumn.GroupID: single_input["group_id"],
                PurpleColumn.LibraryDesign: single_input["library_design"],
                PurpleColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                PurpleColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                PurpleColumn.TissueOrigin: single_input["tissue_origin"],
                PurpleColumn.TissueType: single_input["tissue_type"],
                PurpleColumn.WorkflowRunSWID: single_input["swid"],
            }
        }
