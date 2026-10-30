import qcetl.common
from qcetl.column import GermlineCoverageUniformityCoverageColumn as CovColumn
from qcetl.column import GermlineCoverageUniformityCnvColumn as CnvColumn
from qcetl.germlinecoverageuniformity.parse import parse_coverage, parse_cnv


class GermlineCoverageUniformityCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "germlinecoverageuniformity"
        self.schema_versions = {
            1: {
                "coverage_metrics": {
                    CovColumn.UniformityPct02Mean: "f",
                    CovColumn.UniformityPct04Mean: "f",
                    CovColumn.AverageAutosomalCoverage: "f",
                    CovColumn.MedianAutosomalCoverage: "f",
                    CovColumn.AlignedReads: "i",
                    CovColumn.Donor: "s",
                    CovColumn.FileSWID: "s",
                    CovColumn.GroupID: "s",
                    CovColumn.LibraryDesign: "s",
                    CovColumn.MergedPineryLimsID: "as",
                    CovColumn.TissueOrigin: "s",
                    CovColumn.TissueType: "s",
                },
                "cnv_metrics": {
                    CnvColumn.PMAD: "f",
                    CnvColumn.CoverageUniformity: "f",
                    CnvColumn.NumberOfAmplifications: "i",
                    CnvColumn.NumberOfDeletions: "i",
                    CnvColumn.AmplificationDeletionRatio: "qf",
                    CnvColumn.CnvFileSWID: "qs",
                    CnvColumn.Donor: "s",
                    CnvColumn.FileSWID: "s",
                    CnvColumn.GroupID: "s",
                    CnvColumn.LibraryDesign: "s",
                    CnvColumn.MergedPineryLimsID: "as",
                    CnvColumn.TissueOrigin: "s",
                    CnvColumn.TissueType: "s",
                },
            }
        }
        self.columns = {
            1: {
                "coverage_metrics": CovColumn,
                "cnv_metrics": CnvColumn,
            }
        }
        # The CNV file is an optional workflow output. Both tables are keyed by
        # the coverage file SWID, which holds the uniformity metrics.
        self.input_format = {
            "coverage_path": "p",
            "cnv_path": "qp",
            "swid": "s",
            "cnv_swid": "qs",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "tissue_origin": "s",
            "tissue_type": "s",
        }
        self.primary_key = {
            1: {
                "coverage_metrics": [CovColumn.FileSWID],
                "cnv_metrics": [CnvColumn.FileSWID],
            }
        }
        self.input_key = {1: ("swid", CovColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {
            1: {
                "coverage_metrics": parse_coverage(
                    single_input["coverage_path"]
                ),
                "cnv_metrics": parse_cnv(single_input.get("cnv_path")),
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "coverage_metrics": {
                CovColumn.Donor: single_input["donor"],
                CovColumn.FileSWID: single_input["swid"],
                CovColumn.GroupID: single_input["group_id"],
                CovColumn.LibraryDesign: single_input["library_design"],
                CovColumn.MergedPineryLimsID: single_input["pinery_lims_ids"],
                CovColumn.TissueOrigin: single_input["tissue_origin"],
                CovColumn.TissueType: single_input["tissue_type"],
            },
            "cnv_metrics": {
                CnvColumn.CnvFileSWID: single_input.get("cnv_swid"),
                CnvColumn.Donor: single_input["donor"],
                CnvColumn.FileSWID: single_input["swid"],
                CnvColumn.GroupID: single_input["group_id"],
                CnvColumn.LibraryDesign: single_input["library_design"],
                CnvColumn.MergedPineryLimsID: single_input["pinery_lims_ids"],
                CnvColumn.TissueOrigin: single_input["tissue_origin"],
                CnvColumn.TissueType: single_input["tissue_type"],
            },
        }
