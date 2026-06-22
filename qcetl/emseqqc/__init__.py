import qcetl.common
from qcetl.column import (
    EmSeqBamQcColumn,
    SamtoolsStatsV112Column,
    EmSeqMethylationColumn,
)
import qcetl.bamqc4.parse
import qcetl.samtools.parse_stats
import qcetl.emseqqc.parse


class EmSeqQcCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "emseqqc"
        self.schema_versions = {
            2: {
                "bamqc": {
                    EmSeqBamQcColumn.Barcodes: "s",
                    EmSeqBamQcColumn.FileSWID: "s",
                    EmSeqBamQcColumn.Lane: "i",
                    EmSeqBamQcColumn.PineryLimsID: "s",
                    EmSeqBamQcColumn.Run: "s",
                    EmSeqBamQcColumn.AlignedReference: "p",
                    EmSeqBamQcColumn.AverageReadLength: "f",
                    EmSeqBamQcColumn.BasesMapped: "i",
                    EmSeqBamQcColumn.Coverage: "f",
                    EmSeqBamQcColumn.CoverageDeduplicated: "f",
                    EmSeqBamQcColumn.CoverageMedian: "qf",
                    EmSeqBamQcColumn.CoverageMedian10Percentile: "qi",
                    EmSeqBamQcColumn.CoverageMedian90Percentile: "qi",
                    EmSeqBamQcColumn.DeletedBases: "i",
                    EmSeqBamQcColumn.DownsampledTotal: "qi",
                    EmSeqBamQcColumn.HardClipBases: "i",
                    EmSeqBamQcColumn.InsertMax: "i",
                    EmSeqBamQcColumn.InsertMean: "f",
                    EmSeqBamQcColumn.InsertMedian: "f",
                    EmSeqBamQcColumn.InsertSD: "f",
                    EmSeqBamQcColumn.InsertCount: "i",
                    EmSeqBamQcColumn.Insert10Percentile: "qi",
                    EmSeqBamQcColumn.Insert90Percentile: "qi",
                    EmSeqBamQcColumn.Instrument: "s",
                    EmSeqBamQcColumn.Library: "qs",
                    EmSeqBamQcColumn.LowQualityReadsMeta: "i",
                    EmSeqBamQcColumn.MappedReads: "i",
                    EmSeqBamQcColumn.MarkDuplicates_ESTIMATED_LIBRARY_SIZE: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_LIBRARY: "qs",
                    EmSeqBamQcColumn.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    EmSeqBamQcColumn.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_UNMAPPED_READS: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    EmSeqBamQcColumn.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    EmSeqBamQcColumn.MismatchBases: "i",
                    EmSeqBamQcColumn.NonPrimaryReads: "i",
                    EmSeqBamQcColumn.NonPrimaryReadsMeta: "i",
                    EmSeqBamQcColumn.NumberOfTargets: "i",
                    EmSeqBamQcColumn.PackageVersion: "s",
                    EmSeqBamQcColumn.PairedEnd: "b",
                    EmSeqBamQcColumn.PairedReads: "i",
                    EmSeqBamQcColumn.PairsMappedAbnormallyFar: "i",
                    EmSeqBamQcColumn.PairsMappedToDifferentChr: "i",
                    EmSeqBamQcColumn.ProperlyPairedReads: "i",
                    EmSeqBamQcColumn.QualityCutoff: "qf",
                    EmSeqBamQcColumn.QualityFailedReads: "i",
                    EmSeqBamQcColumn.Read1AverageLength: "f",
                    EmSeqBamQcColumn.Read2AverageLength: "f",
                    EmSeqBamQcColumn.ReadsMappedAndPaired: "i",
                    EmSeqBamQcColumn.ReadsOnTarget: "i",
                    EmSeqBamQcColumn.ReadsPerStartPoint: "f",
                    EmSeqBamQcColumn.ReadsMissingMDTags: "i",
                    EmSeqBamQcColumn.Sample: "qs",
                    EmSeqBamQcColumn.SampleLevel: "qi",
                    EmSeqBamQcColumn.SoftClipBases: "i",
                    EmSeqBamQcColumn.TargetFile: "p",
                    EmSeqBamQcColumn.TotalBasesOnTarget: "i",
                    EmSeqBamQcColumn.TotalInputReadsMeta: "i",
                    EmSeqBamQcColumn.TotalClusters: "i",
                    EmSeqBamQcColumn.TotalReads: "i",
                    EmSeqBamQcColumn.TotalTargetSize: "i",
                    EmSeqBamQcColumn.UnmappedReads: "i",
                    EmSeqBamQcColumn.UnmappedReadsMeta: "i",
                    EmSeqBamQcColumn.WorkflowVersion: "qs",
                },
                "lambda_stats": {
                    SamtoolsStatsV112Column.RawTotalSequences: "i",
                    SamtoolsStatsV112Column.FilteredSequences: "i",
                    SamtoolsStatsV112Column.Sequences: "i",
                    SamtoolsStatsV112Column.IsSorted: "i",
                    SamtoolsStatsV112Column.FirstFragments: "i",
                    SamtoolsStatsV112Column.LastFragments: "i",
                    SamtoolsStatsV112Column.ReadsMapped: "i",
                    SamtoolsStatsV112Column.ReadsMappedAndPaired: "i",
                    SamtoolsStatsV112Column.ReadsUnmapped: "i",
                    SamtoolsStatsV112Column.ReadsProperlyPaired: "i",
                    SamtoolsStatsV112Column.ReadsPaired: "i",
                    SamtoolsStatsV112Column.ReadsDuplicated: "i",
                    SamtoolsStatsV112Column.ReadsmQ0: "i",
                    SamtoolsStatsV112Column.ReadsQCFailed: "i",
                    SamtoolsStatsV112Column.NonPrimaryAlignments: "i",
                    SamtoolsStatsV112Column.TotalLength: "i",
                    SamtoolsStatsV112Column.TotalFirstFragmentLength: "i",
                    SamtoolsStatsV112Column.TotalLastFragmentLength: "i",
                    SamtoolsStatsV112Column.BasesMapped: "i",
                    SamtoolsStatsV112Column.BasesMappedCigar: "i",
                    SamtoolsStatsV112Column.BasesTrimmed: "i",
                    SamtoolsStatsV112Column.BasesDuplicated: "i",
                    SamtoolsStatsV112Column.Mismatches: "i",
                    SamtoolsStatsV112Column.ErrorRate: "f",
                    SamtoolsStatsV112Column.AverageLength: "f",
                    SamtoolsStatsV112Column.AverageFirstFragmentLength: "f",
                    SamtoolsStatsV112Column.AverageLastFragmentLength: "f",
                    SamtoolsStatsV112Column.MaximumLength: "i",
                    SamtoolsStatsV112Column.MaximumFirstFragmentLength: "i",
                    SamtoolsStatsV112Column.MaximumLastFragmentLength: "i",
                    SamtoolsStatsV112Column.AverageQuality: "f",
                    SamtoolsStatsV112Column.InsertSizeAverage: "f",
                    SamtoolsStatsV112Column.InsertSizeStandardDeviation: "f",
                    SamtoolsStatsV112Column.InwardOrientedPairs: "i",
                    SamtoolsStatsV112Column.OutwardOrientedPairs: "i",
                    SamtoolsStatsV112Column.PairsWithOtherOrientation: "i",
                    SamtoolsStatsV112Column.PairsOnDifferentChromosomes: "i",
                    SamtoolsStatsV112Column.PercentageOfProperlyPairedReads: "f",
                    SamtoolsStatsV112Column.BasesInsideTheTarget: "i",
                    SamtoolsStatsV112Column.PercentageTargetsWithCoverage: "f",
                    SamtoolsStatsV112Column.SupplementaryAligments: "i",
                    SamtoolsStatsV112Column.FileSWID: "s",
                    SamtoolsStatsV112Column.Barcodes: "s",
                    SamtoolsStatsV112Column.Lane: "i",
                    SamtoolsStatsV112Column.PineryLimsID: "s",
                    SamtoolsStatsV112Column.Run: "s",
                },
                "puc19_stats": {
                    SamtoolsStatsV112Column.RawTotalSequences: "i",
                    SamtoolsStatsV112Column.FilteredSequences: "i",
                    SamtoolsStatsV112Column.Sequences: "i",
                    SamtoolsStatsV112Column.IsSorted: "i",
                    SamtoolsStatsV112Column.FirstFragments: "i",
                    SamtoolsStatsV112Column.LastFragments: "i",
                    SamtoolsStatsV112Column.ReadsMapped: "i",
                    SamtoolsStatsV112Column.ReadsMappedAndPaired: "i",
                    SamtoolsStatsV112Column.ReadsUnmapped: "i",
                    SamtoolsStatsV112Column.ReadsProperlyPaired: "i",
                    SamtoolsStatsV112Column.ReadsPaired: "i",
                    SamtoolsStatsV112Column.ReadsDuplicated: "i",
                    SamtoolsStatsV112Column.ReadsmQ0: "i",
                    SamtoolsStatsV112Column.ReadsQCFailed: "i",
                    SamtoolsStatsV112Column.NonPrimaryAlignments: "i",
                    SamtoolsStatsV112Column.TotalLength: "i",
                    SamtoolsStatsV112Column.TotalFirstFragmentLength: "i",
                    SamtoolsStatsV112Column.TotalLastFragmentLength: "i",
                    SamtoolsStatsV112Column.BasesMapped: "i",
                    SamtoolsStatsV112Column.BasesMappedCigar: "i",
                    SamtoolsStatsV112Column.BasesTrimmed: "i",
                    SamtoolsStatsV112Column.BasesDuplicated: "i",
                    SamtoolsStatsV112Column.Mismatches: "i",
                    SamtoolsStatsV112Column.ErrorRate: "f",
                    SamtoolsStatsV112Column.AverageLength: "f",
                    SamtoolsStatsV112Column.AverageFirstFragmentLength: "f",
                    SamtoolsStatsV112Column.AverageLastFragmentLength: "f",
                    SamtoolsStatsV112Column.MaximumLength: "i",
                    SamtoolsStatsV112Column.MaximumFirstFragmentLength: "i",
                    SamtoolsStatsV112Column.MaximumLastFragmentLength: "i",
                    SamtoolsStatsV112Column.AverageQuality: "f",
                    SamtoolsStatsV112Column.InsertSizeAverage: "f",
                    SamtoolsStatsV112Column.InsertSizeStandardDeviation: "f",
                    SamtoolsStatsV112Column.InwardOrientedPairs: "i",
                    SamtoolsStatsV112Column.OutwardOrientedPairs: "i",
                    SamtoolsStatsV112Column.PairsWithOtherOrientation: "i",
                    SamtoolsStatsV112Column.PairsOnDifferentChromosomes: "i",
                    SamtoolsStatsV112Column.PercentageOfProperlyPairedReads: "f",
                    SamtoolsStatsV112Column.BasesInsideTheTarget: "i",
                    SamtoolsStatsV112Column.PercentageTargetsWithCoverage: "f",
                    SamtoolsStatsV112Column.SupplementaryAligments: "i",
                    SamtoolsStatsV112Column.FileSWID: "s",
                    SamtoolsStatsV112Column.Barcodes: "s",
                    SamtoolsStatsV112Column.Lane: "i",
                    SamtoolsStatsV112Column.PineryLimsID: "s",
                    SamtoolsStatsV112Column.Run: "s",
                },
                "methylation": {
                    EmSeqMethylationColumn.Barcodes: "s",
                    EmSeqMethylationColumn.FileSWID: "s",
                    EmSeqMethylationColumn.Genome: "f",
                    EmSeqMethylationColumn.Lambda: "f",
                    EmSeqMethylationColumn.Lane: "i",
                    EmSeqMethylationColumn.PineryLimsID: "s",
                    EmSeqMethylationColumn.Puc19: "f",
                    EmSeqMethylationColumn.Run: "s",
                },
            }
        }
        self.columns = {
            2: {
                "bamqc": EmSeqBamQcColumn,
                "lambda_stats": SamtoolsStatsV112Column,
                "puc19_stats": SamtoolsStatsV112Column,
                "methylation": EmSeqMethylationColumn,
            }
        }
        self.input_format = {
            "barcode": "s",
            "file_bamqc": "p",
            "file_lambda_stats": "p",
            "file_puc19_stats": "p",
            "file_methyldackel": "p",
            "lane": "i",
            "pinery_lims_id": "s",
            "run": "s",
            "swid": "s",
        }
        self.primary_key = {
            2: {
                "bamqc": [EmSeqBamQcColumn.FileSWID],
                "lambda_stats": [SamtoolsStatsV112Column.FileSWID],
                "puc19_stats": [SamtoolsStatsV112Column.FileSWID],
                "methylation": [EmSeqMethylationColumn.FileSWID],
            }
        }
        self.input_key = {2: ("swid", EmSeqBamQcColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        if schema_version == 2:
            bamqc = qcetl.bamqc4.parse.parse_record(single_input["file_bamqc"])
            lam = qcetl.samtools.parse_stats.parse_sn(
                single_input["file_lambda_stats"]
            )
            puc = qcetl.samtools.parse_stats.parse_sn(
                single_input["file_puc19_stats"]
            )
            meth = qcetl.emseqqc.parse.parse_methyl_dackel(
                single_input["file_methyldackel"]
            )
            return {
                "bamqc": bamqc,
                "lambda_stats": lam,
                "puc19_stats": puc,
                "methylation": meth,
            }
        else:
            raise KeyError("Unknown version")

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            log = log_creator(__name__)

            if name == "bamqc":
                if cleaning_rules.fix_picard_duplicate_percentage:
                    df[EmSeqBamQcColumn.MarkDuplicates_PERCENT_DUPLICATION] = (
                        100
                        * df[
                            EmSeqBamQcColumn.MarkDuplicates_PERCENT_DUPLICATION
                        ]
                    )

                    if log:
                        log.warning(
                            "Multiplied Picard PERCENT_DUPLICATION by 100 as the "
                            "Picard output is actually a fraction"
                        )

                if cleaning_rules.normalize_downsampling:
                    # Normalization factor due to down sampling
                    norm = (
                        qcetl.bamqc4.parse.calculate_downsampling_normalization(
                            df
                        )
                    )
                    df[EmSeqBamQcColumn.ReadsOnTarget] = (
                        df[EmSeqBamQcColumn.ReadsOnTarget] * norm
                    ).round()
                    df[EmSeqBamQcColumn.TotalBasesOnTarget] = (
                        df[EmSeqBamQcColumn.TotalBasesOnTarget] * norm
                    ).round()
                    df = df.astype(
                        {
                            EmSeqBamQcColumn.ReadsOnTarget: int,
                            EmSeqBamQcColumn.TotalBasesOnTarget: int,
                        }
                    )

                    if log:
                        log.warning(
                            "Downsampled Bedtools metrics have been normalized "
                            "to reflect original input BAM"
                        )

            return df

        return filter_function

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "bamqc": {
                EmSeqBamQcColumn.Barcodes: single_input["barcode"],
                EmSeqBamQcColumn.Lane: single_input["lane"],
                EmSeqBamQcColumn.PineryLimsID: single_input["pinery_lims_id"],
                EmSeqBamQcColumn.Run: single_input["run"],
                EmSeqBamQcColumn.FileSWID: single_input["swid"],
            },
            "lambda_stats": {
                SamtoolsStatsV112Column.Barcodes: single_input["barcode"],
                SamtoolsStatsV112Column.Lane: single_input["lane"],
                SamtoolsStatsV112Column.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                SamtoolsStatsV112Column.Run: single_input["run"],
                SamtoolsStatsV112Column.FileSWID: single_input["swid"],
            },
            "puc19_stats": {
                SamtoolsStatsV112Column.Barcodes: single_input["barcode"],
                SamtoolsStatsV112Column.Lane: single_input["lane"],
                SamtoolsStatsV112Column.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                SamtoolsStatsV112Column.Run: single_input["run"],
                SamtoolsStatsV112Column.FileSWID: single_input["swid"],
            },
            "methylation": {
                EmSeqMethylationColumn.Barcodes: single_input["barcode"],
                EmSeqMethylationColumn.Lane: single_input["lane"],
                EmSeqMethylationColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                EmSeqMethylationColumn.Run: single_input["run"],
                EmSeqMethylationColumn.FileSWID: single_input["swid"],
            },
        }
