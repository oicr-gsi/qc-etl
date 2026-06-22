import qcetl.common
from qcetl.column import (
    BaseRnaSeqQc2Column,
    RnaSeqQc2Column,
    RnaSeqQc2MergedColumn,
)
from qcetl.rnaseqqc2.parse import parse_record


class BaseRnaSeqQc2Cache(qcetl.common.Cache):
    def __init__(
        self, name, column, identifiers, input_data, primary_key, input_key
    ):
        self.name = name
        self.schema_versions = {
            3: {
                name: {
                    **identifiers,
                    BaseRnaSeqQc2Column.AlignedReference: "qp",
                    BaseRnaSeqQc2Column.AverageReadLength: "f",
                    BaseRnaSeqQc2Column.BasesMapped: "i",
                    BaseRnaSeqQc2Column.DeletedBases: "i",
                    BaseRnaSeqQc2Column.FileSWID: "s",
                    BaseRnaSeqQc2Column.InsertCount: "i",
                    BaseRnaSeqQc2Column.InsertMax: "i",
                    BaseRnaSeqQc2Column.InsertMean: "f",
                    BaseRnaSeqQc2Column.InsertMedian: "f",
                    BaseRnaSeqQc2Column.InsertMedian10Percentile: "f",
                    BaseRnaSeqQc2Column.InsertMedian90Percentile: "f",
                    BaseRnaSeqQc2Column.InsertSD: "f",
                    BaseRnaSeqQc2Column.MappedReads: "i",
                    BaseRnaSeqQc2Column.MetricsIntronicBases: "i",
                    BaseRnaSeqQc2Column.MetricsCorrectStrandReads: "qi",
                    BaseRnaSeqQc2Column.MetricsIgnoredReads: "i",
                    BaseRnaSeqQc2Column.MetricsIncorrectStrandReads: "qi",
                    BaseRnaSeqQc2Column.MetricsIntergenicBases: "i",
                    BaseRnaSeqQc2Column.MetricsMedian5PrimeTo3PrimeBias: "f",
                    BaseRnaSeqQc2Column.MetricsMedian3PrimeBias: "f",
                    BaseRnaSeqQc2Column.MetricsMedian5PrimeBias: "f",
                    BaseRnaSeqQc2Column.MetricsMedianCVCoverage: "f",
                    BaseRnaSeqQc2Column.MetricsNumRead1TranscriptStrandReads: "qi",
                    BaseRnaSeqQc2Column.MetricsNumRead2TranscriptStrandReads: "qi",
                    BaseRnaSeqQc2Column.MetricsNumUnexplainedReads: "qi",
                    BaseRnaSeqQc2Column.MetricsPassedFilterAlignedBases: "i",
                    BaseRnaSeqQc2Column.MetricsPassedFilterBases: "i",
                    BaseRnaSeqQc2Column.MetricsPercentCodingBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentCorrectStrandReads: "f",
                    BaseRnaSeqQc2Column.MetricsPercentIntergenicBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentIntronicBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentMRnaBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentRead1TranscriptStrandReads: "f",
                    BaseRnaSeqQc2Column.MetricsPercentRead2TranscriptStrandReads: "f",
                    BaseRnaSeqQc2Column.MetricsPercentRibosomalBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentUTRBases: "f",
                    BaseRnaSeqQc2Column.MetricsPercentUsableBases: "f",
                    BaseRnaSeqQc2Column.MetricsRibosomalBases: "i",
                    BaseRnaSeqQc2Column.MetricsUTRBases: "i",
                    BaseRnaSeqQc2Column.MismatchBases: "i",
                    BaseRnaSeqQc2Column.NonPrimaryReads: "i",
                    BaseRnaSeqQc2Column.PackageVersion: "s",
                    BaseRnaSeqQc2Column.PairedEnd: "b",
                    BaseRnaSeqQc2Column.PairedReads: "i",
                    BaseRnaSeqQc2Column.PairsMappedAbnormallyFar: "i",
                    BaseRnaSeqQc2Column.PairsMappedToDifferentChr: "i",
                    BaseRnaSeqQc2Column.ProperlyPairedReads: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationDuplicates: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationInTotal: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationMapped: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationPairedInSequencing: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationProperlyPaired: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationRead1: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationRead2: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationSecondary: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationSingletons: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationSupplementary: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationWithMateMappedToDifferentChr: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationWithMateMappedToDifferentChrAndGoodMapQ: "i",
                    BaseRnaSeqQc2Column.RRnaContaminationWithSelfAndMateMapped: "i",
                    BaseRnaSeqQc2Column.Read1AverageLength: "f",
                    BaseRnaSeqQc2Column.Read2AverageLength: "f",
                    BaseRnaSeqQc2Column.ReadsMappedAndPaired: "i",
                    BaseRnaSeqQc2Column.TotalClusters: "i",
                    BaseRnaSeqQc2Column.TotalReads: "i",
                    BaseRnaSeqQc2Column.UniqueReads: "i",
                    BaseRnaSeqQc2Column.UnmappedReads: "i",
                }
            },
        }
        self.columns = column
        self.input_format = {**input_data, "path": "p", "swid": "s"}
        self.primary_key = primary_key
        self.input_key = input_key

    def parse_single_record(self, single_input, schema_version):
        if schema_version == 3:
            df = parse_record(single_input["path"])
            return {self.name: df}
        else:
            raise KeyError("Unknown schema version")

    def add_shesmu_metadata(self, single_input, schema_version):
        raise NotImplementedError


class RnaSeqQc2Cache(BaseRnaSeqQc2Cache):
    def __init__(self):
        super().__init__(
            "rnaseqqc2",
            {
                3: {"rnaseqqc2": RnaSeqQc2Column},
            },
            {
                RnaSeqQc2Column.Barcodes: "s",
                RnaSeqQc2Column.Lane: "i",
                RnaSeqQc2Column.PineryLimsID: "s",
                RnaSeqQc2Column.Reference: "s",
                RnaSeqQc2Column.Run: "s",
            },
            {
                "run": "s",
                "lane": "i",
                "barcode": "s",
                "pinery_lims_id": "s",
                "reference": "s",
            },
            {
                3: {"rnaseqqc2": [BaseRnaSeqQc2Column.FileSWID]},
            },
            {
                3: ("swid", BaseRnaSeqQc2Column.FileSWID),
            },
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                RnaSeqQc2Column.Run: single_input["run"],
                RnaSeqQc2Column.Lane: single_input["lane"],
                RnaSeqQc2Column.Barcodes: single_input["barcode"],
                RnaSeqQc2Column.PineryLimsID: single_input["pinery_lims_id"],
                RnaSeqQc2Column.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                RnaSeqQc2Column.FileSWID: single_input["swid"],
            }
        }


class RnaSeqQc2MergedCache(BaseRnaSeqQc2Cache):
    def __init__(self):
        super().__init__(
            "rnaseqqc2merged",
            {
                3: {"rnaseqqc2merged": RnaSeqQc2MergedColumn},
            },
            {
                RnaSeqQc2MergedColumn.Donor: "s",
                RnaSeqQc2MergedColumn.GroupID: "s",
                RnaSeqQc2MergedColumn.LibraryDesign: "s",
                RnaSeqQc2MergedColumn.MergedPineryLimsID: "as",
                RnaSeqQc2MergedColumn.Project: "s",
                RnaSeqQc2MergedColumn.Reference: "s",
                RnaSeqQc2MergedColumn.TissueOrigin: "s",
                RnaSeqQc2MergedColumn.TissueType: "s",
            },
            {
                "donor": "s",
                "group_id": "s",
                "library_design": "s",
                "project": "s",
                "pinery_lims_ids": "as",
                "reference": "s",
                "tissue_origin": "s",
                "tissue_type": "s",
            },
            {
                3: {"rnaseqqc2merged": [BaseRnaSeqQc2Column.FileSWID]},
            },
            {
                3: ("swid", BaseRnaSeqQc2Column.FileSWID),
            },
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                RnaSeqQc2MergedColumn.Donor: single_input["donor"],
                RnaSeqQc2MergedColumn.GroupID: single_input["group_id"],
                RnaSeqQc2MergedColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                # Will be used for merging and lists cannot be merged (not hashable)
                RnaSeqQc2MergedColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                RnaSeqQc2MergedColumn.Project: single_input["project"],
                RnaSeqQc2MergedColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                RnaSeqQc2MergedColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                RnaSeqQc2MergedColumn.TissueType: single_input["tissue_type"],
                RnaSeqQc2MergedColumn.FileSWID: single_input["swid"],
            }
        }
