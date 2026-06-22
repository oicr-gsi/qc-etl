import qcetl.common
from qcetl.column import AnalysisMutect2Column as Mutect2Column

from qcetl.analysis_mutect2.parse import parse_vcf_record
from qcetl.analysis_mutect2.parse import parse_tsv_record


class AnalysisMutect2Cache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_mutect2"
        self.schema_versions = {
            1: {
                "analysis_mutect2": {
                    Mutect2Column.Donor: "s",
                    Mutect2Column.GroupID: "s",
                    Mutect2Column.LibraryDesign: "s",
                    Mutect2Column.Reference: "s",
                    Mutect2Column.TissueOrigin: "s",
                    Mutect2Column.TissueType: "s",
                    Mutect2Column.MergedPineryLimsID: "as",
                    Mutect2Column.WorkflowRunSWID: "s",
                    Mutect2Column.NumCalls: "i",
                    Mutect2Column.NumPASS: "i",
                    Mutect2Column.PASSNumSNPs: "i",
                    Mutect2Column.PASSNumMultiSNPs: "i",
                    Mutect2Column.PASSNumIndels: "i",
                    Mutect2Column.TITVRatio: "f",
                    Mutect2Column.PASSNumMNPs: "i",
                    Mutect2Column.PctTI: "f",
                    Mutect2Column.PctTV: "f",
                }
            }
        }
        self.columns = {
            1: {
                "analysis_mutect2": Mutect2Column,
            }
        }
        self.input_format = {
            "donor": "s",
            "vcf": "qp",
            "tsv": "qp",
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
                "analysis_mutect2": [
                    Mutect2Column.WorkflowRunSWID,
                ]
            }
        }
        self.input_key = {1: ("swid", Mutect2Column.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        if single_input["tsv"] is not None:
            df = parse_tsv_record(
                single_input["tsv"],
            )
        elif single_input["vcf"] is not None:
            df = parse_vcf_record(
                single_input["vcf"],
            )
        else:
            raise ValueError("Expected either 'tsv' or 'vcf' in single_input")
        return {
            1: {
                "analysis_mutect2": df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_mutect2": {
                Mutect2Column.Donor: single_input["donor"],
                Mutect2Column.GroupID: single_input["group_id"],
                Mutect2Column.LibraryDesign: single_input["library_design"],
                Mutect2Column.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                Mutect2Column.TissueOrigin: single_input["tissue_origin"],
                Mutect2Column.TissueType: single_input["tissue_type"],
                Mutect2Column.WorkflowRunSWID: single_input["swid"],
                Mutect2Column.Reference: single_input.get(
                    "reference", "Unknown"
                ),
            }
        }
