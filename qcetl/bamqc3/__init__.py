import qcetl.common
from qcetl.column import (
    BaseBamQc3Column,
    BamQc3Column,
    BamQc3MergedColumn,
    BamQc3IntHistColumn,
    BamQc3MergedIntHistColumn,
)
from qcetl.bamqc3.parse import (
    parse_record,
    calculate_downsampling_normalization,
)


class BaseBamQc3Cache(qcetl.common.Cache):
    def __init__(
        self,
        name,
        column,
        hist_column,
        identifiers,
        extra_columns,
        input_data,
        primary_key,
        input_key,
    ):
        self.name = name
        self.schema_versions = {
            #  1: Parses BamQC JSON from Niassa workflow version 3+
            2: {
                name: {
                    **identifiers,
                    **extra_columns,
                    BaseBamQc3Column.AlignedReference: "p",
                    BaseBamQc3Column.AverageReadLength: "f",
                    BaseBamQc3Column.BasesMapped: "i",
                    BaseBamQc3Column.Coverage: "f",
                    BaseBamQc3Column.CoverageDeduplicated: "f",
                    BaseBamQc3Column.DeletedBases: "i",
                    BaseBamQc3Column.HardClipBases: "i",
                    BaseBamQc3Column.InsertMax: "i",
                    BaseBamQc3Column.InsertMean: "f",
                    BaseBamQc3Column.InsertMedian: "f",
                    BaseBamQc3Column.InsertSD: "f",
                    BaseBamQc3Column.InsertCount: "i",
                    BaseBamQc3Column.Insert10Percentile: "qi",
                    BaseBamQc3Column.Insert90Percentile: "qi",
                    BaseBamQc3Column.MappedReads: "i",
                    BaseBamQc3Column.MarkDuplicates_ESTIMATED_LIBRARY_SIZE: "qi",
                    BaseBamQc3Column.MarkDuplicates_LIBRARY: "qs",
                    BaseBamQc3Column.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    BaseBamQc3Column.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    BaseBamQc3Column.MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES: "qi",
                    BaseBamQc3Column.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    BaseBamQc3Column.MarkDuplicates_UNMAPPED_READS: "qi",
                    BaseBamQc3Column.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    BaseBamQc3Column.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    BaseBamQc3Column.MismatchBases: "i",
                    BaseBamQc3Column.NonPrimaryReads: "i",
                    BaseBamQc3Column.NumberOfTargets: "i",
                    BaseBamQc3Column.PackageVersion: "s",
                    BaseBamQc3Column.PairedEnd: "b",
                    BaseBamQc3Column.PairedReads: "i",
                    BaseBamQc3Column.PairsMappedAbnormallyFar: "i",
                    BaseBamQc3Column.PairsMappedToDifferentChr: "i",
                    BaseBamQc3Column.ProperlyPairedReads: "i",
                    BaseBamQc3Column.QualityCutoff: "qf",
                    BaseBamQc3Column.QualityFailedReads: "i",
                    BaseBamQc3Column.Read1AverageLength: "f",
                    BaseBamQc3Column.Read2AverageLength: "f",
                    BaseBamQc3Column.ReadsMappedAndPaired: "i",
                    BaseBamQc3Column.ReadsOnTarget: "i",
                    BaseBamQc3Column.ReadsPerStartPoint: "f",
                    BaseBamQc3Column.ReadsMissingMDTags: "i",
                    BaseBamQc3Column.Sample: "qs",
                    BaseBamQc3Column.SampleLevel: "i",
                    BaseBamQc3Column.SampleTotal: "qi",
                    BaseBamQc3Column.SoftClipBases: "i",
                    BaseBamQc3Column.TargetFile: "p",
                    BaseBamQc3Column.TotalBasesOnTarget: "i",
                    BaseBamQc3Column.TotalReads: "i",
                    BaseBamQc3Column.TotalClusters: "i",
                    BaseBamQc3Column.TotalTargetSize: "i",
                    BaseBamQc3Column.UnmappedReads: "i",
                    BaseBamQc3Column.WorkflowVersion: "qs",
                },
                "histogram": {
                    **identifiers,
                    BamQc3IntHistColumn.Count: "i",
                    BamQc3IntHistColumn.Name: "s",
                    BamQc3IntHistColumn.Value: "i",
                },
            }
        }
        self.columns = {2: {name: column, "histogram": hist_column}}
        self.input_format = {**input_data, "path": "p", "swid": "s"}
        self.primary_key = primary_key
        self.input_key = input_key

    def parse_single_record(self, single_input, schema_version):
        merged = self.name == "bamqc3merged"
        df, hist = parse_record(single_input["path"], merged)
        return {2: {self.name: df, "histogram": hist}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        raise NotImplementedError

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            if name == "histogram":
                return df

            log = log_creator(__name__)

            if cleaning_rules.fix_picard_duplicate_percentage:
                df[BaseBamQc3Column.MarkDuplicates_PERCENT_DUPLICATION] = (
                    100
                    * df[BaseBamQc3Column.MarkDuplicates_PERCENT_DUPLICATION]
                )

                if log:
                    log.warning(
                        "Multiplied Picard PERCENT_DUPLICATION by 100 as the "
                        "Picard output is actually a fraction"
                    )

            if cleaning_rules.normalize_downsampling:
                # Normalization factor due to down sampling
                norm = calculate_downsampling_normalization(df)
                df[BaseBamQc3Column.ReadsOnTarget] = (
                    df[BaseBamQc3Column.ReadsOnTarget] * norm
                ).round()
                df[BaseBamQc3Column.TotalBasesOnTarget] = (
                    df[BaseBamQc3Column.TotalBasesOnTarget] * norm
                ).round()
                df = df.astype(
                    {
                        BaseBamQc3Column.ReadsOnTarget: int,
                        BaseBamQc3Column.TotalBasesOnTarget: int,
                    }
                )

                if log:
                    log.warning(
                        "Downsampled Bedtools metrics have been normalized "
                        "to reflect original input BAM"
                    )

            return df

        return filter_function


class BamQc3Cache(BaseBamQc3Cache):
    def __init__(self):
        super().__init__(
            "bamqc3",
            BamQc3Column,
            BamQc3IntHistColumn,
            {
                BamQc3Column.Barcodes: "s",
                BaseBamQc3Column.FileSWID: "s",
                BamQc3Column.Lane: "i",
                BamQc3Column.Run: "s",
                BaseBamQc3Column.Reference: "s",
            },
            {BaseBamQc3Column.Instrument: "s", BaseBamQc3Column.Library: "qs"},
            {},
            {
                2: {
                    "bamqc3": [BaseBamQc3Column.FileSWID],
                    "histogram": [
                        BaseBamQc3Column.FileSWID,
                        BamQc3IntHistColumn.Value,
                        BamQc3IntHistColumn.Name,
                    ],
                }
            },
            {2: ("swid", BaseBamQc3Column.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        # metadata is contained in one DataFrame and will be used to populate others
        return {
            self.name: {BamQc3Column.FileSWID: single_input["swid"]},
            "histogram": {
                BamQc3Column.FileSWID: single_input["swid"],
            },
        }


class BamQc3MergedCache(BaseBamQc3Cache):
    def __init__(self):
        super().__init__(
            "bamqc3merged",
            BamQc3MergedColumn,
            BamQc3MergedIntHistColumn,
            {
                BamQc3MergedColumn.Donor: "s",
                BaseBamQc3Column.FileSWID: "s",
                BamQc3MergedColumn.GroupID: "s",
                BamQc3MergedColumn.LibraryDesign: "s",
                BamQc3MergedColumn.Project: "s",
                BamQc3MergedColumn.TissueOrigin: "s",
                BamQc3MergedColumn.TissueType: "s",
                BaseBamQc3Column.Reference: "s",
            },
            {BaseBamQc3Column.Instrument: "as", BaseBamQc3Column.Library: "as"},
            {"project": "s"},
            {
                2: {
                    "bamqc3merged": [BaseBamQc3Column.FileSWID],
                    "histogram": [
                        BaseBamQc3Column.FileSWID,
                        BamQc3MergedIntHistColumn.Value,
                        BamQc3MergedIntHistColumn.Name,
                    ],
                }
            },
            {2: ("swid", BaseBamQc3Column.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                BamQc3MergedColumn.Project: single_input["project"],
                BamQc3MergedColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                BamQc3MergedColumn.FileSWID: single_input["swid"],
            },
            "histogram": {
                BamQc3MergedIntHistColumn.Project: single_input["project"],
                BamQc3MergedIntHistColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                BamQc3MergedIntHistColumn.FileSWID: single_input["swid"],
            },
        }
