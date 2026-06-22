import qcetl.common
from qcetl.column import (
    AnalysisSequenzaAlternativeSolutionsColumn as AltSolnCol,
    AnalysisSequenzaGamma500FGAColumn as FGACol,
)

from qcetl.analysis_sequenza.parse import parse_record


class AnalysisSequenzaCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "analysis_sequenza"
        self.schema_versions = {
            1: {
                "analysis_sequenza_alternative_solutions": {
                    AltSolnCol.Donor: "s",
                    AltSolnCol.GroupID: "s",
                    AltSolnCol.LibraryDesign: "s",
                    AltSolnCol.Reference: "s",
                    AltSolnCol.TissueOrigin: "s",
                    AltSolnCol.TissueType: "s",
                    AltSolnCol.MergedPineryLimsID: "as",
                    AltSolnCol.WorkflowRunSWID: "s",
                    AltSolnCol.Index: "i",
                    AltSolnCol.Cellularity: "f",
                    AltSolnCol.Ploidy: "f",
                    AltSolnCol.SLPP: "f",
                    AltSolnCol.Gamma: "i",
                },
                "analysis_sequenza_gamma_500_fga": {
                    FGACol.Donor: "s",
                    FGACol.GroupID: "s",
                    FGACol.LibraryDesign: "s",
                    FGACol.Reference: "s",
                    FGACol.TissueOrigin: "s",
                    FGACol.TissueType: "s",
                    FGACol.MergedPineryLimsID: "as",
                    FGACol.WorkflowRunSWID: "s",
                    FGACol.FGA: "f",
                },
            }
        }
        self.columns = {
            1: {
                "analysis_sequenza_alternative_solutions": AltSolnCol,
                "analysis_sequenza_gamma_500_fga": FGACol,
            }
        }
        self.input_format = {
            "donor": "s",
            "alt_soln_file": "p",
            "zip_file": "p",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "reference": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
            "genome_size": "i",
            "fga_gamma": "i",  # gamma level fga is calculated for
            "fga_threshold": "f",  # we want seg.mean greater than threshold
        }
        self.primary_key = {
            1: {
                "analysis_sequenza_alternative_solutions": [
                    AltSolnCol.WorkflowRunSWID,
                    AltSolnCol.Gamma,
                    AltSolnCol.Index,
                ],
                "analysis_sequenza_gamma_500_fga": [
                    FGACol.WorkflowRunSWID,
                ],
            }
        }
        self.input_key = {1: ("swid", AltSolnCol.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        alt_soln, gamma_500_fga = parse_record(
            single_input["alt_soln_file"],
            single_input["zip_file"],
            single_input["genome_size"],
            single_input["fga_gamma"],
            single_input["fga_threshold"],
        )
        return {
            1: {
                "analysis_sequenza_alternative_solutions": alt_soln,
                "analysis_sequenza_gamma_500_fga": gamma_500_fga,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "analysis_sequenza_alternative_solutions": {
                AltSolnCol.Donor: single_input["donor"],
                AltSolnCol.GroupID: single_input["group_id"],
                AltSolnCol.LibraryDesign: single_input["library_design"],
                AltSolnCol.MergedPineryLimsID: single_input["pinery_lims_ids"],
                AltSolnCol.TissueOrigin: single_input["tissue_origin"],
                AltSolnCol.TissueType: single_input["tissue_type"],
                AltSolnCol.WorkflowRunSWID: single_input["swid"],
                AltSolnCol.Reference: single_input.get("reference", "Unknown"),
            },
            "analysis_sequenza_gamma_500_fga": {
                FGACol.Donor: single_input["donor"],
                FGACol.GroupID: single_input["group_id"],
                FGACol.LibraryDesign: single_input["library_design"],
                FGACol.MergedPineryLimsID: single_input["pinery_lims_ids"],
                FGACol.TissueOrigin: single_input["tissue_origin"],
                FGACol.TissueType: single_input["tissue_type"],
                FGACol.WorkflowRunSWID: single_input["swid"],
                FGACol.Reference: single_input.get("reference", "Unknown"),
            },
        }
