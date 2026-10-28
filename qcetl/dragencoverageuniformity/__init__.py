import qcetl.common
from qcetl.column import DragenCoverageUniformityCoverageColumn as CovColumn
from qcetl.column import DragenCoverageUniformityCnvColumn as CnvColumn
from qcetl.dragencoverageuniformity.parse import parse_coverage, parse_cnv


class DragenCoverageUniformityCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "dragencoverageuniformity"
        self.schema_versions = {
            1: {
                "coverage_metrics": {
                    CovColumn.AlignedBases: "qi",
                    CovColumn.AlignedBasesInGenome: "qi",
                    CovColumn.AlignedBasesInGenomePct: "qf",
                    CovColumn.AverageAlignmentCoverage: "qf",
                    CovColumn.UniformityPct02Mean: "f",
                    CovColumn.UniformityPct04Mean: "f",
                    CovColumn.PctCoverage1500xInf: "qf",
                    CovColumn.PctCoverage1000xInf: "qf",
                    CovColumn.PctCoverage500xInf: "qf",
                    CovColumn.PctCoverage100xInf: "qf",
                    CovColumn.PctCoverage50xInf: "qf",
                    CovColumn.PctCoverage20xInf: "qf",
                    CovColumn.PctCoverage15xInf: "qf",
                    CovColumn.PctCoverage10xInf: "qf",
                    CovColumn.PctCoverage3xInf: "qf",
                    CovColumn.PctCoverage1xInf: "qf",
                    CovColumn.PctCoverage0xInf: "qf",
                    CovColumn.PctCoverage1000x1500x: "qf",
                    CovColumn.PctCoverage500x1000x: "qf",
                    CovColumn.PctCoverage100x500x: "qf",
                    CovColumn.PctCoverage50x100x: "qf",
                    CovColumn.PctCoverage20x50x: "qf",
                    CovColumn.PctCoverage15x20x: "qf",
                    CovColumn.PctCoverage10x15x: "qf",
                    CovColumn.PctCoverage3x10x: "qf",
                    CovColumn.PctCoverage1x3x: "qf",
                    CovColumn.PctCoverage0x1x: "qf",
                    CovColumn.MedianChrXCoverage: "qf",
                    CovColumn.MedianChrYCoverage: "qf",
                    CovColumn.AverageMitochondrialCoverage: "qf",
                    CovColumn.AverageAutosomalCoverage: "f",
                    CovColumn.MedianAutosomalCoverage: "f",
                    CovColumn.MeanMedianAutosomalCoverageRatio: "qf",
                    CovColumn.AlignedReads: "i",
                    CovColumn.AlignedReadsInGenome: "qi",
                    CovColumn.AlignedReadsInGenomePct: "qf",
                    CovColumn.Donor: "s",
                    CovColumn.FileSWID: "s",
                    CovColumn.GroupID: "s",
                    CovColumn.LibraryDesign: "s",
                    CovColumn.MergedPineryLimsID: "as",
                    CovColumn.TissueOrigin: "s",
                    CovColumn.TissueType: "s",
                },
                "cnv_metrics": {
                    CnvColumn.SexGenotyperSample: "qs",
                    CnvColumn.SexGenotyperKaryotype: "qs",
                    CnvColumn.SexGenotyperConfidence: "qf",
                    CnvColumn.BasesInReferenceGenome: "qi",
                    CnvColumn.AverageAlignmentCoverage: "qf",
                    CnvColumn.NumberOfAlignmentRecords: "qi",
                    CnvColumn.FilteredRecordsTotal: "qi",
                    CnvColumn.FilteredRecordsTotalPct: "qf",
                    CnvColumn.FilteredRecordsDuplicates: "qi",
                    CnvColumn.FilteredRecordsDuplicatesPct: "qf",
                    CnvColumn.FilteredRecordsMAPQ: "qi",
                    CnvColumn.FilteredRecordsMAPQPct: "qf",
                    CnvColumn.FilteredRecordsUnmapped: "qi",
                    CnvColumn.FilteredRecordsUnmappedPct: "qf",
                    CnvColumn.PMAD: "f",
                    CnvColumn.CoverageUniformity: "f",
                    CnvColumn.NumberOfTargetIntervals: "qi",
                    CnvColumn.NumberOfSegments: "qi",
                    CnvColumn.NumberOfAmplifications: "i",
                    CnvColumn.NumberOfDeletions: "i",
                    CnvColumn.NumberOfPassingAmplifications: "qi",
                    CnvColumn.NumberOfPassingAmplificationsPct: "qf",
                    CnvColumn.NumberOfPassingDeletions: "qi",
                    CnvColumn.NumberOfPassingDeletionsPct: "qf",
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
