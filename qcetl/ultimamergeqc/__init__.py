import qcetl.common
from qcetl.column import UltimaMergeQcColumn as Column
from qcetl.ultimamergeqc.parse import parse_record


class UltimaMergeQcCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "ultimamergeqc"
        self.schema_versions = {
            1: {
                "ultimamergeqc": {
                    # Shesmu metadata
                    Column.Donor: "s",
                    Column.GroupID: "s",
                    Column.MergedPineryLimsID: "as",
                    Column.TissueOrigin: "s",
                    Column.TissueType: "s",
                    Column.WorkflowRunSWID: "s",
                    # ALN: CollectAlignmentSummaryMetrics
                    Column.Category: "s",
                    Column.TotalReads: "i",
                    Column.PfReads: "i",
                    Column.PercentPFReads: "f",
                    Column.PfNoiseReads: "i",
                    Column.PfReadsAligned: "i",
                    Column.PercentPFReadsAligned: "f",
                    Column.PfAlignedBases: "i",
                    Column.PfHqAlignedReads: "i",
                    Column.PfHqAlignedBases: "i",
                    Column.PfHqAlignedQ20Bases: "i",
                    Column.PfHqMedianMismatches: "f",
                    Column.PfMismatchRate: "f",
                    Column.PfHqErrorRate: "f",
                    Column.PfIndelRate: "f",
                    Column.MeanReadLength: "f",
                    Column.SdReadLength: "f",
                    Column.MedianReadLength: "f",
                    Column.MadReadLength: "f",
                    Column.MinReadLength: "i",
                    Column.MaxReadLength: "i",
                    Column.MeanAlignedReadLength: "f",
                    Column.ReadsAlignedInPairs: "i",
                    Column.PercentReadsAlignedInPairs: "f",
                    Column.PfReadsImproperPairs: "i",
                    Column.PercentPfReadsImproperPairs: "f",
                    Column.BadCycles: "i",
                    Column.StrandBalance: "f",
                    Column.PercentChimeras: "f",
                    Column.PercentAdapter: "f",
                    Column.PercentSoftclip: "f",
                    Column.PercentHardclip: "f",
                    Column.AvgPos3PrimeSoftclipLength: "f",
                    # DUP: MarkDuplicates
                    Column.Library: "s",
                    Column.UnpairedReadsExamined: "i",
                    Column.ReadPairsExamined: "i",
                    Column.SecondaryOrSupplementaryReads: "i",
                    Column.UnmappedReads: "i",
                    Column.UnpairedReadDuplicates: "i",
                    Column.ReadPairDuplicates: "i",
                    Column.ReadPairOpticalDuplicates: "i",
                    Column.PercentDuplication: "f",
                    # WGS: CollectWgsMetrics
                    Column.GenomeTerritory: "i",
                    Column.MeanCoverage: "f",
                    Column.SdCoverage: "f",
                    Column.MedianCoverage: "f",
                    Column.MadCoverage: "f",
                    Column.PercentExcAdapter: "f",
                    Column.PercentExcMapq: "f",
                    Column.PercentExcDupe: "f",
                    Column.PercentExcUnpaired: "f",
                    Column.PercentExcBaseq: "f",
                    Column.PercentExcOverlap: "f",
                    Column.PercentExcCapped: "f",
                    Column.PercentExcTotal: "f",
                    Column.Percent1X: "f",
                    Column.Percent5X: "f",
                    Column.Percent10X: "f",
                    Column.Percent15X: "f",
                    Column.Percent20X: "f",
                    Column.Percent25X: "f",
                    Column.Percent30X: "f",
                    Column.Percent40X: "f",
                    Column.Percent50X: "f",
                    Column.Percent60X: "f",
                    Column.Percent70X: "f",
                    Column.Percent80X: "f",
                    Column.Percent90X: "f",
                    Column.Percent100X: "f",
                    Column.Fold80BasePenalty: "f",
                    Column.Fold90BasePenalty: "f",
                    Column.Fold95BasePenalty: "f",
                    Column.HetSnpSensitivity: "f",
                    Column.HetSnpQ: "f",
                }
            }
        }
        self.columns = {
            1: {
                "ultimamergeqc": Column,
            }
        }
        self.input_format = {
            "alignment_summary_file": "p",
            "duplicate_metrics_file": "p",
            "wgs_metrics_file": "p",
            "donor": "s",
            "group_id": "s",
            "pinery_lims_ids": "as",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {
            1: {
                "ultimamergeqc": [
                    Column.WorkflowRunSWID,
                ],
            }
        }
        self.input_key = {1: ("swid", Column.WorkflowRunSWID)}

    def parse_single_record(self, single_input, schema_version):
        ultima_df = parse_record(
            single_input["alignment_summary_file"],
            single_input["duplicate_metrics_file"],
            single_input["wgs_metrics_file"],
            self.schema_versions[schema_version]["ultimamergeqc"],
        )
        return {
            1: {
                "ultimamergeqc": ultima_df,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ultimamergeqc": {
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.WorkflowRunSWID: single_input["swid"],
            }
        }
