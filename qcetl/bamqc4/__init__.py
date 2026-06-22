import qcetl.common
from qcetl.column import BaseBamQc4Column, BamQc4Column, BamQc4MergedColumn
from qcetl.bamqc4.parse import (
    parse_record,
    calculate_downsampling_normalization,
)


class BaseBamQc4Cache(qcetl.common.Cache):
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
            5: {
                name: {
                    **identifiers,
                    **extra_columns,
                    BaseBamQc4Column.AlignedReference: "p",
                    BaseBamQc4Column.AverageReadLength: "f",
                    BaseBamQc4Column.BasesMapped: "i",
                    BaseBamQc4Column.Coverage: "f",
                    BaseBamQc4Column.CoverageDeduplicated: "f",
                    BaseBamQc4Column.CoverageMedian: "qf",
                    BaseBamQc4Column.CoverageMedian10Percentile: "qi",
                    BaseBamQc4Column.CoverageMedian90Percentile: "qi",
                    BaseBamQc4Column.DeletedBases: "i",
                    BaseBamQc4Column.DownsampledTotal: "qi",
                    BaseBamQc4Column.HardClipBases: "i",
                    BaseBamQc4Column.InsertMax: "i",
                    BaseBamQc4Column.InsertMean: "f",
                    BaseBamQc4Column.InsertMedian: "f",
                    BaseBamQc4Column.InsertSD: "f",
                    BaseBamQc4Column.InsertCount: "i",
                    BaseBamQc4Column.Insert10Percentile: "qi",
                    BaseBamQc4Column.Insert90Percentile: "qi",
                    BaseBamQc4Column.LowQualityReadsMeta: "i",
                    BaseBamQc4Column.MappedReads: "i",
                    BaseBamQc4Column.MarkDuplicates_ESTIMATED_LIBRARY_SIZE: "qi",
                    BaseBamQc4Column.MarkDuplicates_LIBRARY: "qs",
                    BaseBamQc4Column.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    BaseBamQc4Column.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    BaseBamQc4Column.MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES: "qi",
                    BaseBamQc4Column.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    BaseBamQc4Column.MarkDuplicates_UNMAPPED_READS: "qi",
                    BaseBamQc4Column.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    BaseBamQc4Column.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    BaseBamQc4Column.MismatchBases: "i",
                    BaseBamQc4Column.NonPrimaryReads: "i",
                    BaseBamQc4Column.NonPrimaryReadsMeta: "i",
                    BaseBamQc4Column.NumberOfTargets: "i",
                    BaseBamQc4Column.PackageVersion: "s",
                    BaseBamQc4Column.PairedEnd: "b",
                    BaseBamQc4Column.PairedReads: "i",
                    BaseBamQc4Column.PairsMappedAbnormallyFar: "i",
                    BaseBamQc4Column.PairsMappedToDifferentChr: "i",
                    BaseBamQc4Column.ProperlyPairedReads: "i",
                    BaseBamQc4Column.QualityCutoff: "qf",
                    BaseBamQc4Column.QualityFailedReads: "i",
                    BaseBamQc4Column.Read1AverageLength: "f",
                    BaseBamQc4Column.Read2AverageLength: "f",
                    BaseBamQc4Column.ReadsMappedAndPaired: "i",
                    BaseBamQc4Column.ReadsOnTarget: "i",
                    BaseBamQc4Column.ReadsPerStartPoint: "f",
                    BaseBamQc4Column.ReadsMissingMDTags: "i",
                    BaseBamQc4Column.Sample: "qs",
                    BaseBamQc4Column.SampleLevel: "qi",
                    BaseBamQc4Column.SoftClipBases: "i",
                    BaseBamQc4Column.TargetFile: "p",
                    BaseBamQc4Column.TotalBasesOnTarget: "i",
                    BaseBamQc4Column.TotalInputReadsMeta: "i",
                    BaseBamQc4Column.TotalClusters: "i",
                    BaseBamQc4Column.TotalReads: "i",
                    BaseBamQc4Column.TotalTargetSize: "i",
                    BaseBamQc4Column.UnmappedReads: "i",
                    BaseBamQc4Column.UnmappedReadsMeta: "i",
                    BaseBamQc4Column.WorkflowVersion: "qs",
                }
            }
        }
        self.columns = {5: {name: column}}
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
                df[BaseBamQc4Column.MarkDuplicates_PERCENT_DUPLICATION] = (
                    100
                    * df[BaseBamQc4Column.MarkDuplicates_PERCENT_DUPLICATION]
                )

                if log:
                    log.warning(
                        "Multiplied Picard PERCENT_DUPLICATION by 100 as the "
                        "Picard output is actually a fraction"
                    )

            if cleaning_rules.normalize_downsampling:
                # Normalization factor due to down sampling
                norm = calculate_downsampling_normalization(df)
                df[BaseBamQc4Column.ReadsOnTarget] = (
                    df[BaseBamQc4Column.ReadsOnTarget] * norm
                ).round()
                df[BaseBamQc4Column.TotalBasesOnTarget] = (
                    df[BaseBamQc4Column.TotalBasesOnTarget] * norm
                ).round()
                df = df.astype(
                    {
                        BaseBamQc4Column.ReadsOnTarget: int,
                        BaseBamQc4Column.TotalBasesOnTarget: int,
                    }
                )

                if log:
                    log.warning(
                        "Downsampled Bedtools metrics have been normalized "
                        "to reflect original input BAM"
                    )

            return df

        return filter_function

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(
            single_input["path"], single_input["workflow_version"]
        )
        return {5: {self.name: df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        raise NotImplementedError


class BamQc4Cache(BaseBamQc4Cache):
    def __init__(self):
        super().__init__(
            "bamqc4",
            BamQc4Column,
            {
                BamQc4Column.Barcodes: "s",
                BaseBamQc4Column.FileSWID: "s",
                BamQc4Column.Lane: "i",
                BamQc4Column.PineryLimsID: "s",
                BamQc4Column.Run: "s",
                BaseBamQc4Column.Reference: "s",
            },
            {BaseBamQc4Column.Instrument: "s", BaseBamQc4Column.Library: "qs"},
            {"pinery_lims_id": "s", "run": "s", "lane": "i", "barcode": "s"},
            {5: {"bamqc4": [BaseBamQc4Column.FileSWID]}},
            {5: ("swid", BaseBamQc4Column.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                BamQc4Column.FileSWID: single_input["swid"],
                BamQc4Column.PineryLimsID: single_input["pinery_lims_id"],
                BamQc4Column.Run: single_input["run"],
                BamQc4Column.Lane: single_input["lane"],
                BamQc4Column.Barcodes: single_input["barcode"],
                BamQc4Column.Reference: single_input.get(
                    "reference", "Unknown"
                ),
            }
        }


class BamQc4MergedCache(BaseBamQc4Cache):
    def __init__(self):
        super().__init__(
            "bamqc4merged",
            BamQc4MergedColumn,
            {
                BamQc4MergedColumn.Donor: "s",
                BaseBamQc4Column.FileSWID: "s",
                BamQc4MergedColumn.GroupID: "s",
                BamQc4MergedColumn.LibraryDesign: "s",
                BamQc4MergedColumn.MergedPineryLimsID: "as",
                BamQc4MergedColumn.Project: "s",
                BamQc4MergedColumn.TissueOrigin: "s",
                BamQc4MergedColumn.TissueType: "s",
                BaseBamQc4Column.Reference: "s",
            },
            {BaseBamQc4Column.Instrument: "as", BaseBamQc4Column.Library: "as"},
            {
                "project": "s",
                "pinery_lims_ids": "as",
                "donor": "s",
                "group_id": "s",
                "library_design": "s",
                "tissue_origin": "s",
                "tissue_type": "s",
            },
            {5: {"bamqc4merged": [BaseBamQc4Column.FileSWID]}},
            {5: ("swid", BaseBamQc4Column.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                BamQc4MergedColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                BamQc4MergedColumn.Project: single_input["project"],
                BamQc4MergedColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                BamQc4MergedColumn.FileSWID: single_input["swid"],
                BamQc4MergedColumn.Donor: single_input["donor"],
                BamQc4MergedColumn.GroupID: single_input["group_id"],
                BamQc4MergedColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                BamQc4MergedColumn.TissueOrigin: single_input["tissue_origin"],
                BamQc4MergedColumn.TissueType: single_input["tissue_type"],
            }
        }
