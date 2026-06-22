import qcetl.common
from qcetl.column import (
    IchorCna2MainColumn,
    IchorCna2SolutionColumn,
    IchorCna2MergedMainColumn,
    IchorCna2MergedSolutionColumn,
    IchorCna2BamqcColumn,
    IchorCna2MergedBamqcColumn,
)
from qcetl.ichorcna2.parse import parse_record
import qcetl.bamqc4.parse


class IchorCna2Cache(qcetl.common.Cache):
    def __init__(self):
        self.name = "ichorcna2"
        self.schema_versions = {
            1: {
                "main": {
                    IchorCna2MainColumn.Barcodes: "s",
                    IchorCna2MainColumn.Lane: "i",
                    IchorCna2MainColumn.PineryLimsID: "s",
                    IchorCna2MainColumn.Run: "s",
                    IchorCna2MainColumn.Reference: "s",
                    IchorCna2MainColumn.FileSWID: "s",
                    IchorCna2MainColumn.ChrXMedianLogRation: "f",
                    IchorCna2MainColumn.ChrYCoverageFraction: "f",
                    IchorCna2MainColumn.Coverage: "f",
                    IchorCna2MainColumn.FractionCnaSubclonal: "f",
                    IchorCna2MainColumn.FractionGenomeSubclonal: "f",
                    IchorCna2MainColumn.GCMapCorrectionMAD: "f",
                    IchorCna2MainColumn.GammaRateInit: "f",
                    IchorCna2MainColumn.Gender: "s",
                    IchorCna2MainColumn.PloidyBestSolution: "f",
                    IchorCna2MainColumn.SubcloneFraction: "f",
                    IchorCna2MainColumn.TumorFractionBestSolution: "f",
                },
                "solution": {
                    IchorCna2SolutionColumn.Barcodes: "s",
                    IchorCna2SolutionColumn.Lane: "i",
                    IchorCna2SolutionColumn.PineryLimsID: "s",
                    IchorCna2SolutionColumn.Run: "s",
                    IchorCna2SolutionColumn.Reference: "s",
                    IchorCna2SolutionColumn.FileSWID: "s",
                    IchorCna2SolutionColumn.Init: "s",
                    IchorCna2SolutionColumn.TumorFractionPerSolution: "f",
                    IchorCna2SolutionColumn.PloidyPerSolution: "f",
                    IchorCna2SolutionColumn.NEst: "f",
                    IchorCna2SolutionColumn.PhiEst: "f",
                    IchorCna2SolutionColumn.Bic: "f",
                    IchorCna2SolutionColumn.FractionGenomeSubclonalPerSolution: "f",
                    IchorCna2SolutionColumn.FractionCnaSubclonalPerSolution: "f",
                    IchorCna2SolutionColumn.LogLikPerSolution: "f",
                },
                "bamqc": {
                    IchorCna2BamqcColumn.Barcodes: "s",
                    IchorCna2BamqcColumn.Lane: "i",
                    IchorCna2BamqcColumn.PineryLimsID: "s",
                    IchorCna2BamqcColumn.Run: "s",
                    IchorCna2BamqcColumn.Reference: "s",
                    IchorCna2BamqcColumn.FileSWID: "s",
                    IchorCna2BamqcColumn.Instrument: "s",
                    IchorCna2BamqcColumn.Library: "qs",
                    IchorCna2BamqcColumn.AlignedReference: "p",
                    IchorCna2BamqcColumn.AverageReadLength: "f",
                    IchorCna2BamqcColumn.BasesMapped: "i",
                    IchorCna2BamqcColumn.Coverage: "f",
                    IchorCna2BamqcColumn.CoverageDeduplicated: "f",
                    IchorCna2BamqcColumn.CoverageMedian: "qf",
                    IchorCna2BamqcColumn.CoverageMedian10Percentile: "qi",
                    IchorCna2BamqcColumn.CoverageMedian90Percentile: "qi",
                    IchorCna2BamqcColumn.DeletedBases: "i",
                    IchorCna2BamqcColumn.DownsampledTotal: "qi",
                    IchorCna2BamqcColumn.HardClipBases: "i",
                    IchorCna2BamqcColumn.InsertMax: "i",
                    IchorCna2BamqcColumn.InsertMean: "f",
                    IchorCna2BamqcColumn.InsertMedian: "f",
                    IchorCna2BamqcColumn.InsertSD: "f",
                    IchorCna2BamqcColumn.InsertCount: "i",
                    IchorCna2BamqcColumn.Insert10Percentile: "qi",
                    IchorCna2BamqcColumn.Insert90Percentile: "qi",
                    IchorCna2BamqcColumn.LowQualityReadsMeta: "i",
                    IchorCna2BamqcColumn.MappedReads: "i",
                    IchorCna2BamqcColumn.MarkDuplicates_ESTIMATED_LIBRARY_SIZE: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_LIBRARY: "qs",
                    IchorCna2BamqcColumn.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    IchorCna2BamqcColumn.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_UNMAPPED_READS: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    IchorCna2BamqcColumn.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    IchorCna2BamqcColumn.MismatchBases: "i",
                    IchorCna2BamqcColumn.NonPrimaryReads: "i",
                    IchorCna2BamqcColumn.NonPrimaryReadsMeta: "i",
                    IchorCna2BamqcColumn.NumberOfTargets: "i",
                    IchorCna2BamqcColumn.PackageVersion: "s",
                    IchorCna2BamqcColumn.PairedEnd: "b",
                    IchorCna2BamqcColumn.PairedReads: "i",
                    IchorCna2BamqcColumn.PairsMappedAbnormallyFar: "i",
                    IchorCna2BamqcColumn.PairsMappedToDifferentChr: "i",
                    IchorCna2BamqcColumn.ProperlyPairedReads: "i",
                    IchorCna2BamqcColumn.QualityCutoff: "qf",
                    IchorCna2BamqcColumn.QualityFailedReads: "i",
                    IchorCna2BamqcColumn.Read1AverageLength: "f",
                    IchorCna2BamqcColumn.Read2AverageLength: "f",
                    IchorCna2BamqcColumn.ReadsMappedAndPaired: "i",
                    IchorCna2BamqcColumn.ReadsOnTarget: "i",
                    IchorCna2BamqcColumn.ReadsPerStartPoint: "f",
                    IchorCna2BamqcColumn.ReadsMissingMDTags: "i",
                    IchorCna2BamqcColumn.Sample: "qs",
                    IchorCna2BamqcColumn.SampleLevel: "qi",
                    IchorCna2BamqcColumn.SoftClipBases: "i",
                    IchorCna2BamqcColumn.TargetFile: "p",
                    IchorCna2BamqcColumn.TotalBasesOnTarget: "i",
                    IchorCna2BamqcColumn.TotalInputReadsMeta: "i",
                    IchorCna2BamqcColumn.TotalClusters: "i",
                    IchorCna2BamqcColumn.TotalReads: "i",
                    IchorCna2BamqcColumn.TotalTargetSize: "i",
                    IchorCna2BamqcColumn.UnmappedReads: "i",
                    IchorCna2BamqcColumn.UnmappedReadsMeta: "i",
                    IchorCna2BamqcColumn.WorkflowVersion: "qs",
                },
            }
        }
        self.columns = {
            1: {
                "main": IchorCna2MainColumn,
                "solution": IchorCna2SolutionColumn,
                "bamqc": IchorCna2BamqcColumn,
            }
        }
        self.input_format = {
            "barcodes": "s",
            "lane": "i",
            "run": "s",
            "pinery_lims_id": "s",
            "file": "p",
            "bamqc_file": "p",
            "swid": "s",
        }
        self.primary_key = {
            1: {
                "main": [
                    IchorCna2MainColumn.Barcodes,
                    IchorCna2MainColumn.Lane,
                    IchorCna2MainColumn.Run,
                ],
                "solution": [
                    IchorCna2SolutionColumn.FileSWID,
                    IchorCna2SolutionColumn.Init,
                ],
                "bamqc": [IchorCna2BamqcColumn.FileSWID],
            }
        }
        self.input_key = {1: ("swid", IchorCna2MainColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        main_schema = {
            IchorCna2MainColumn.ChrXMedianLogRation: "f",
            IchorCna2MainColumn.ChrYCoverageFraction: "f",
            IchorCna2MainColumn.Coverage: "f",
            IchorCna2MainColumn.FractionCnaSubclonal: "f",
            IchorCna2MainColumn.FractionGenomeSubclonal: "f",
            IchorCna2MainColumn.GCMapCorrectionMAD: "f",
            IchorCna2MainColumn.GammaRateInit: "f",
            IchorCna2MainColumn.Gender: "s",
            IchorCna2MainColumn.PloidyBestSolution: "f",
            IchorCna2MainColumn.SubcloneFraction: "f",
            IchorCna2MainColumn.TumorFractionBestSolution: "f",
        }
        sol_schema = {
            IchorCna2SolutionColumn.Init: "s",
            IchorCna2SolutionColumn.TumorFractionPerSolution: "f",
            IchorCna2SolutionColumn.PloidyPerSolution: "f",
            IchorCna2SolutionColumn.NEst: "f",
            IchorCna2SolutionColumn.PhiEst: "f",
            IchorCna2SolutionColumn.Bic: "f",
            IchorCna2SolutionColumn.FractionGenomeSubclonalPerSolution: "f",
            IchorCna2SolutionColumn.FractionCnaSubclonalPerSolution: "f",
            IchorCna2SolutionColumn.LogLikPerSolution: "f",
        }
        main_df, solution_df, bamqc_df = parse_record(
            single_input["file"],
            single_input["bamqc_file"],
            main_schema,
            sol_schema,
        )

        return {
            1: {"main": main_df, "solution": solution_df, "bamqc": bamqc_df}
        }[schema_version]

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            log = log_creator(__name__)

            if name == "bamqc":
                if cleaning_rules.fix_picard_duplicate_percentage:
                    df[
                        IchorCna2BamqcColumn.MarkDuplicates_PERCENT_DUPLICATION
                    ] = (
                        100
                        * df[
                            IchorCna2BamqcColumn.MarkDuplicates_PERCENT_DUPLICATION
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
                    df[IchorCna2BamqcColumn.ReadsOnTarget] = (
                        df[IchorCna2BamqcColumn.ReadsOnTarget] * norm
                    ).round()
                    df[IchorCna2BamqcColumn.TotalBasesOnTarget] = (
                        df[IchorCna2BamqcColumn.TotalBasesOnTarget] * norm
                    ).round()
                    df = df.astype(
                        {
                            IchorCna2BamqcColumn.ReadsOnTarget: int,
                            IchorCna2BamqcColumn.TotalBasesOnTarget: int,
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
            "main": {
                IchorCna2MainColumn.Run: single_input["run"],
                IchorCna2MainColumn.Lane: single_input["lane"],
                IchorCna2MainColumn.Barcodes: single_input["barcodes"],
                IchorCna2MainColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                IchorCna2MainColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2MainColumn.FileSWID: single_input["swid"],
            },
            "solution": {
                IchorCna2SolutionColumn.Run: single_input["run"],
                IchorCna2SolutionColumn.Lane: single_input["lane"],
                IchorCna2SolutionColumn.Barcodes: single_input["barcodes"],
                IchorCna2SolutionColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                IchorCna2SolutionColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2SolutionColumn.FileSWID: single_input["swid"],
            },
            "bamqc": {
                IchorCna2BamqcColumn.Run: single_input["run"],
                IchorCna2BamqcColumn.Lane: single_input["lane"],
                IchorCna2BamqcColumn.Barcodes: single_input["barcodes"],
                IchorCna2BamqcColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                IchorCna2BamqcColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2BamqcColumn.FileSWID: single_input["swid"],
            },
        }


class IchorCna2MergedCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "ichorcna2merged"
        self.schema_versions = {
            2: {
                "main": {
                    IchorCna2MergedMainColumn.Donor: "s",
                    IchorCna2MergedMainColumn.GroupID: "s",
                    IchorCna2MergedMainColumn.LibraryDesign: "s",
                    IchorCna2MergedMainColumn.MergedPineryLimsID: "as",
                    IchorCna2MergedMainColumn.Project: "s",
                    IchorCna2MergedMainColumn.Reference: "s",
                    IchorCna2MergedMainColumn.TissueOrigin: "s",
                    IchorCna2MergedMainColumn.TissueType: "s",
                    IchorCna2MergedMainColumn.FileSWID: "s",
                    IchorCna2MergedMainColumn.ChrXMedianLogRation: "f",
                    IchorCna2MergedMainColumn.ChrYCoverageFraction: "f",
                    IchorCna2MergedMainColumn.Coverage: "f",
                    IchorCna2MergedMainColumn.FractionCnaSubclonal: "f",
                    IchorCna2MergedMainColumn.FractionGenomeSubclonal: "f",
                    IchorCna2MergedMainColumn.GCMapCorrectionMAD: "f",
                    IchorCna2MergedMainColumn.GammaRateInit: "f",
                    IchorCna2MergedMainColumn.Gender: "s",
                    IchorCna2MergedMainColumn.PloidyBestSolution: "f",
                    IchorCna2MergedMainColumn.SubcloneFraction: "f",
                    IchorCna2MergedMainColumn.TumorFractionBestSolution: "f",
                },
                "solution": {
                    IchorCna2MergedSolutionColumn.Donor: "s",
                    IchorCna2MergedSolutionColumn.GroupID: "s",
                    IchorCna2MergedSolutionColumn.LibraryDesign: "s",
                    IchorCna2MergedSolutionColumn.MergedPineryLimsID: "as",
                    IchorCna2MergedSolutionColumn.Project: "s",
                    IchorCna2MergedSolutionColumn.Reference: "s",
                    IchorCna2MergedSolutionColumn.TissueOrigin: "s",
                    IchorCna2MergedSolutionColumn.TissueType: "s",
                    IchorCna2MergedSolutionColumn.FileSWID: "s",
                    IchorCna2MergedSolutionColumn.Init: "s",
                    IchorCna2MergedSolutionColumn.TumorFractionPerSolution: "f",
                    IchorCna2MergedSolutionColumn.PloidyPerSolution: "f",
                    IchorCna2MergedSolutionColumn.NEst: "f",
                    IchorCna2MergedSolutionColumn.PhiEst: "f",
                    IchorCna2MergedSolutionColumn.Bic: "f",
                    IchorCna2MergedSolutionColumn.FractionGenomeSubclonalPerSolution: "f",
                    IchorCna2MergedSolutionColumn.FractionCnaSubclonalPerSolution: "f",
                    IchorCna2MergedSolutionColumn.LogLikPerSolution: "f",
                },
                "bamqc": {
                    IchorCna2MergedBamqcColumn.Donor: "s",
                    IchorCna2MergedBamqcColumn.GroupID: "s",
                    IchorCna2MergedBamqcColumn.LibraryDesign: "s",
                    IchorCna2MergedBamqcColumn.MergedPineryLimsID: "as",
                    IchorCna2MergedBamqcColumn.Project: "s",
                    IchorCna2MergedBamqcColumn.Reference: "s",
                    IchorCna2MergedBamqcColumn.TissueOrigin: "s",
                    IchorCna2MergedBamqcColumn.TissueType: "s",
                    IchorCna2MergedBamqcColumn.FileSWID: "s",
                    IchorCna2MergedBamqcColumn.Instrument: "as",
                    IchorCna2MergedBamqcColumn.Library: "s",
                    IchorCna2MergedBamqcColumn.AlignedReference: "p",
                    IchorCna2MergedBamqcColumn.AverageReadLength: "f",
                    IchorCna2MergedBamqcColumn.BasesMapped: "i",
                    IchorCna2MergedBamqcColumn.Coverage: "f",
                    IchorCna2MergedBamqcColumn.CoverageDeduplicated: "f",
                    IchorCna2MergedBamqcColumn.CoverageMedian: "qf",
                    IchorCna2MergedBamqcColumn.CoverageMedian10Percentile: "qi",
                    IchorCna2MergedBamqcColumn.CoverageMedian90Percentile: "qi",
                    IchorCna2MergedBamqcColumn.DeletedBases: "i",
                    IchorCna2MergedBamqcColumn.DownsampledTotal: "qi",
                    IchorCna2MergedBamqcColumn.HardClipBases: "i",
                    IchorCna2MergedBamqcColumn.InsertMax: "i",
                    IchorCna2MergedBamqcColumn.InsertMean: "f",
                    IchorCna2MergedBamqcColumn.InsertMedian: "f",
                    IchorCna2MergedBamqcColumn.InsertSD: "f",
                    IchorCna2MergedBamqcColumn.InsertCount: "i",
                    IchorCna2MergedBamqcColumn.Insert10Percentile: "qi",
                    IchorCna2MergedBamqcColumn.Insert90Percentile: "qi",
                    IchorCna2MergedBamqcColumn.LowQualityReadsMeta: "i",
                    IchorCna2MergedBamqcColumn.MappedReads: "i",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_ESTIMATED_LIBRARY_SIZE: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_LIBRARY: "qs",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_PERCENT_DUPLICATION: "qf",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_READ_PAIR_DUPLICATES: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_READ_PAIRS_EXAMINED: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_UNMAPPED_READS: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_UNPAIRED_READ_DUPLICATES: "qi",
                    IchorCna2MergedBamqcColumn.MarkDuplicates_UNPAIRED_READS_EXAMINED: "qi",
                    IchorCna2MergedBamqcColumn.MismatchBases: "i",
                    IchorCna2MergedBamqcColumn.NonPrimaryReads: "i",
                    IchorCna2MergedBamqcColumn.NonPrimaryReadsMeta: "i",
                    IchorCna2MergedBamqcColumn.NumberOfTargets: "i",
                    IchorCna2MergedBamqcColumn.PackageVersion: "s",
                    IchorCna2MergedBamqcColumn.PairedEnd: "b",
                    IchorCna2MergedBamqcColumn.PairedReads: "i",
                    IchorCna2MergedBamqcColumn.PairsMappedAbnormallyFar: "i",
                    IchorCna2MergedBamqcColumn.PairsMappedToDifferentChr: "i",
                    IchorCna2MergedBamqcColumn.ProperlyPairedReads: "i",
                    IchorCna2MergedBamqcColumn.QualityCutoff: "qf",
                    IchorCna2MergedBamqcColumn.QualityFailedReads: "i",
                    IchorCna2MergedBamqcColumn.Read1AverageLength: "f",
                    IchorCna2MergedBamqcColumn.Read2AverageLength: "f",
                    IchorCna2MergedBamqcColumn.ReadsMappedAndPaired: "i",
                    IchorCna2MergedBamqcColumn.ReadsOnTarget: "i",
                    IchorCna2MergedBamqcColumn.ReadsPerStartPoint: "f",
                    IchorCna2MergedBamqcColumn.ReadsMissingMDTags: "i",
                    IchorCna2MergedBamqcColumn.Sample: "qs",
                    IchorCna2MergedBamqcColumn.SampleLevel: "qi",
                    IchorCna2MergedBamqcColumn.SoftClipBases: "i",
                    IchorCna2MergedBamqcColumn.TargetFile: "p",
                    IchorCna2MergedBamqcColumn.TotalBasesOnTarget: "i",
                    IchorCna2MergedBamqcColumn.TotalInputReadsMeta: "i",
                    IchorCna2MergedBamqcColumn.TotalClusters: "i",
                    IchorCna2MergedBamqcColumn.TotalReads: "i",
                    IchorCna2MergedBamqcColumn.TotalTargetSize: "i",
                    IchorCna2MergedBamqcColumn.UnmappedReads: "i",
                    IchorCna2MergedBamqcColumn.UnmappedReadsMeta: "i",
                    IchorCna2MergedBamqcColumn.WorkflowVersion: "qs",
                },
            }
        }
        self.columns = {
            2: {
                "main": IchorCna2MergedMainColumn,
                "solution": IchorCna2MergedSolutionColumn,
                "bamqc": IchorCna2MergedBamqcColumn,
            }
        }
        self.input_format = {
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "project": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "file": "s",
            "bamqc_file": "s",
            "swid": "s",
        }
        self.primary_key = {
            2: {
                "main": [
                    IchorCna2MergedSolutionColumn.FileSWID,
                ],
                "solution": [
                    IchorCna2MergedSolutionColumn.FileSWID,
                    IchorCna2MergedSolutionColumn.Init,
                ],
                "bamqc": [IchorCna2MergedBamqcColumn.FileSWID],
            }
        }
        self.input_key = {2: ("swid", IchorCna2MergedMainColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        main_schema = {
            IchorCna2MergedMainColumn.ChrXMedianLogRation: "f",
            IchorCna2MergedMainColumn.ChrYCoverageFraction: "f",
            IchorCna2MergedMainColumn.Coverage: "f",
            IchorCna2MergedMainColumn.FractionCnaSubclonal: "f",
            IchorCna2MergedMainColumn.FractionGenomeSubclonal: "f",
            IchorCna2MergedMainColumn.GCMapCorrectionMAD: "f",
            IchorCna2MergedMainColumn.GammaRateInit: "f",
            IchorCna2MergedMainColumn.Gender: "s",
            IchorCna2MergedMainColumn.PloidyBestSolution: "f",
            IchorCna2MergedMainColumn.SubcloneFraction: "f",
            IchorCna2MergedMainColumn.TumorFractionBestSolution: "f",
        }
        sol_schema = {
            IchorCna2MergedSolutionColumn.Init: "s",
            IchorCna2MergedSolutionColumn.TumorFractionPerSolution: "f",
            IchorCna2MergedSolutionColumn.PloidyPerSolution: "f",
            IchorCna2MergedSolutionColumn.NEst: "f",
            IchorCna2MergedSolutionColumn.PhiEst: "f",
            IchorCna2MergedSolutionColumn.Bic: "f",
            IchorCna2MergedSolutionColumn.FractionGenomeSubclonalPerSolution: "f",
            IchorCna2MergedSolutionColumn.FractionCnaSubclonalPerSolution: "f",
            IchorCna2MergedSolutionColumn.LogLikPerSolution: "f",
        }
        main_df, solution_df, bamqc_df = parse_record(
            single_input["file"],
            single_input["bamqc_file"],
            main_schema,
            sol_schema,
        )

        return {
            2: {"main": main_df, "solution": solution_df, "bamqc": bamqc_df}
        }[schema_version]

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            log = log_creator(__name__)

            if name == "bamqc":
                if cleaning_rules.fix_picard_duplicate_percentage:
                    df[
                        IchorCna2BamqcColumn.MarkDuplicates_PERCENT_DUPLICATION
                    ] = (
                        100
                        * df[
                            IchorCna2BamqcColumn.MarkDuplicates_PERCENT_DUPLICATION
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
                    df[IchorCna2BamqcColumn.ReadsOnTarget] = (
                        df[IchorCna2BamqcColumn.ReadsOnTarget] * norm
                    ).round()
                    df[IchorCna2BamqcColumn.TotalBasesOnTarget] = (
                        df[IchorCna2BamqcColumn.TotalBasesOnTarget] * norm
                    ).round()
                    df = df.astype(
                        {
                            IchorCna2BamqcColumn.ReadsOnTarget: int,
                            IchorCna2BamqcColumn.TotalBasesOnTarget: int,
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
            "main": {
                IchorCna2MergedMainColumn.Donor: single_input["donor"],
                IchorCna2MergedMainColumn.GroupID: single_input["group_id"],
                IchorCna2MergedMainColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                IchorCna2MergedMainColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                IchorCna2MergedMainColumn.Project: single_input["project"],
                IchorCna2MergedMainColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2MergedMainColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                IchorCna2MergedMainColumn.TissueType: single_input[
                    "tissue_type"
                ],
                IchorCna2MergedMainColumn.FileSWID: single_input["swid"],
            },
            "solution": {
                IchorCna2MergedSolutionColumn.Donor: single_input["donor"],
                IchorCna2MergedSolutionColumn.GroupID: single_input["group_id"],
                IchorCna2MergedSolutionColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                IchorCna2MergedSolutionColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                IchorCna2MergedSolutionColumn.Project: single_input["project"],
                IchorCna2MergedSolutionColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2MergedSolutionColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                IchorCna2MergedSolutionColumn.TissueType: single_input[
                    "tissue_type"
                ],
                IchorCna2MergedSolutionColumn.FileSWID: single_input["swid"],
            },
            "bamqc": {
                IchorCna2MergedBamqcColumn.Donor: single_input["donor"],
                IchorCna2MergedBamqcColumn.GroupID: single_input["group_id"],
                IchorCna2MergedBamqcColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                IchorCna2MergedBamqcColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                IchorCna2MergedBamqcColumn.Project: single_input["project"],
                IchorCna2MergedBamqcColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCna2MergedBamqcColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                IchorCna2MergedBamqcColumn.TissueType: single_input[
                    "tissue_type"
                ],
                IchorCna2MergedBamqcColumn.FileSWID: single_input["swid"],
            },
        }
