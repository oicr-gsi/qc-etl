import qcetl.common
from qcetl.column import (
    BaseBamQcLiteColumn,
    BamQcLiteColumn,
    BamQcLiteMergedColumn,
)
from qcetl.bamqclite.parse import (
    parse_record,
    calculate_downsampling_normalization,
)


class BaseBamQcLiteCache(qcetl.common.Cache):
    def __init__(
        self,
        name,
        column,
        identifiers,
        extra_columns,
        input_data,
        primary_key,
        input_key,
    ):
        self.name = name
        self.schema_versions = {
            1: {
                name: {
                    **identifiers,
                    **extra_columns,
                    BaseBamQcLiteColumn.AlignedReference: "p",
                    BaseBamQcLiteColumn.AverageReadLength: "f",
                    BaseBamQcLiteColumn.BasesMapped: "i",
                    BaseBamQcLiteColumn.Coverage: "f",
                    BaseBamQcLiteColumn.CoverageDeduplicated: "f",
                    BaseBamQcLiteColumn.CoverageMedian: "qf",
                    BaseBamQcLiteColumn.CoverageMedian10Percentile: "qi",
                    BaseBamQcLiteColumn.CoverageMedian90Percentile: "qi",
                    BaseBamQcLiteColumn.DeletedBases: "i",
                    BaseBamQcLiteColumn.DownsampledTotal: "qi",
                    BaseBamQcLiteColumn.HardClipBases: "i",
                    BaseBamQcLiteColumn.InsertMax: "i",
                    BaseBamQcLiteColumn.InsertMean: "f",
                    BaseBamQcLiteColumn.InsertMedian: "f",
                    BaseBamQcLiteColumn.InsertSD: "f",
                    BaseBamQcLiteColumn.InsertCount: "i",
                    BaseBamQcLiteColumn.Insert10Percentile: "qi",
                    BaseBamQcLiteColumn.Insert90Percentile: "qi",
                    BaseBamQcLiteColumn.MappedReads: "i",
                    BaseBamQcLiteColumn.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    BaseBamQcLiteColumn.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    BaseBamQcLiteColumn.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    BaseBamQcLiteColumn.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    BaseBamQcLiteColumn.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    BaseBamQcLiteColumn.MismatchBases: "i",
                    BaseBamQcLiteColumn.NonPrimaryReads: "i",
                    BaseBamQcLiteColumn.NumberOfTargets: "i",
                    BaseBamQcLiteColumn.PackageVersion: "s",
                    BaseBamQcLiteColumn.PairedEnd: "b",
                    BaseBamQcLiteColumn.PairedReads: "i",
                    BaseBamQcLiteColumn.PairsMappedAbnormallyFar: "i",
                    BaseBamQcLiteColumn.PairsMappedToDifferentChr: "i",
                    BaseBamQcLiteColumn.ProperlyPairedReads: "i",
                    BaseBamQcLiteColumn.Read1AverageLength: "f",
                    BaseBamQcLiteColumn.Read2AverageLength: "f",
                    BaseBamQcLiteColumn.ReadsMappedAndPaired: "i",
                    BaseBamQcLiteColumn.ReadsOnTarget: "i",
                    BaseBamQcLiteColumn.ReadsPerStartPoint: "f",
                    BaseBamQcLiteColumn.ReadsMissingMDTags: "i",
                    BaseBamQcLiteColumn.Sample: "qs",
                    BaseBamQcLiteColumn.SoftClipBases: "i",
                    BaseBamQcLiteColumn.TargetFile: "p",
                    BaseBamQcLiteColumn.TotalBasesOnTarget: "i",
                    BaseBamQcLiteColumn.TotalClusters: "i",
                    BaseBamQcLiteColumn.TotalReads: "i",
                    BaseBamQcLiteColumn.TotalTargetSize: "i",
                    BaseBamQcLiteColumn.UnmappedReads: "i",
                    BaseBamQcLiteColumn.WorkflowVersion: "qs",
                }
            }
        }
        self.columns = {1: {name: column}}
        self.input_format = {
            **input_data,
            "reference": "s",
            "path": "p",
            "swid": "s",
            "workflow_version": ["i", "i", "i"],
        }
        self.primary_key = primary_key
        self.input_key = input_key

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            if name == "histogram":
                return df

            log = log_creator(__name__)

            if cleaning_rules.fix_picard_duplicate_percentage:
                df[BaseBamQcLiteColumn.MarkDuplicates_PERCENT_DUPLICATION] = (
                    100
                    * df[BaseBamQcLiteColumn.MarkDuplicates_PERCENT_DUPLICATION]
                )

                if log:
                    log.warning(
                        "Multiplied Picard PERCENT_DUPLICATION by 100 as the "
                        "Picard output is actually a fraction"
                    )

            return df

        return filter_function

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(
            single_input["path"], single_input["workflow_version"]
        )
        return {1: {self.name: df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        raise NotImplementedError


class BamQcLiteCache(BaseBamQcLiteCache):
    def __init__(self):
        super().__init__(
            "bamqclite",
            BamQcLiteColumn,
            {
                BamQcLiteColumn.Barcodes: "s",
                BaseBamQcLiteColumn.FileSWID: "s",
                BamQcLiteColumn.Lane: "i",
                BamQcLiteColumn.PineryLimsID: "s",
                BamQcLiteColumn.Run: "s",
                BaseBamQcLiteColumn.Reference: "s",
            },
            {
                BaseBamQcLiteColumn.Instrument: "s",
                BaseBamQcLiteColumn.Library: "qs",
            },
            {"pinery_lims_id": "s", "run": "s", "lane": "i", "barcode": "s"},
            {1: {"bamqclite": [BaseBamQcLiteColumn.FileSWID]}},
            {1: ("swid", BaseBamQcLiteColumn.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                BamQcLiteColumn.FileSWID: single_input["swid"],
                BamQcLiteColumn.PineryLimsID: single_input["pinery_lims_id"],
                BamQcLiteColumn.Run: single_input["run"],
                BamQcLiteColumn.Lane: single_input["lane"],
                BamQcLiteColumn.Barcodes: single_input["barcode"],
                BamQcLiteColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
            }
        }


class BamQcLiteMergedCache(BaseBamQcLiteCache):
    def __init__(self):
        super().__init__(
            "bamqclitemerged",
            BamQcLiteMergedColumn,
            {
                BamQcLiteMergedColumn.Donor: "s",
                BaseBamQcLiteColumn.FileSWID: "s",
                BamQcLiteMergedColumn.GroupID: "s",
                BamQcLiteMergedColumn.LibraryDesign: "s",
                BamQcLiteMergedColumn.MergedPineryLimsID: "as",
                BamQcLiteMergedColumn.Project: "s",
                BamQcLiteMergedColumn.TissueOrigin: "s",
                BamQcLiteMergedColumn.TissueType: "s",
                BaseBamQcLiteColumn.Reference: "s",
            },
            {
                BaseBamQcLiteColumn.Instrument: "s",
                BaseBamQcLiteColumn.Library: "s",
            },
            {
                "project": "s",
                "pinery_lims_ids": "as",
                "donor": "s",
                "group_id": "s",
                "library_design": "s",
                "tissue_origin": "s",
                "tissue_type": "s",
            },
            {1: {"bamqclitemerged": [BaseBamQcLiteColumn.FileSWID]}},
            {1: ("swid", BaseBamQcLiteColumn.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                BamQcLiteMergedColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                BamQcLiteMergedColumn.Project: single_input["project"],
                BamQcLiteMergedColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                BamQcLiteMergedColumn.FileSWID: single_input["swid"],
                BamQcLiteMergedColumn.Donor: single_input["donor"],
                BamQcLiteMergedColumn.GroupID: single_input["group_id"],
                BamQcLiteMergedColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                BamQcLiteMergedColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                BamQcLiteMergedColumn.TissueType: single_input["tissue_type"],
            }
        }
