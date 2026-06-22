import qcetl.common
from qcetl.column import (
    CfMeDipQcColumn as Column,
    InsertSizeMetricsColumn as InsertColumn,
)
from qcetl.cfmedipqc.parse import parse_record


class CfMeDipQcCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "cfmedipqc"
        self.schema_versions = {
            4: {
                "cfmedipqc": {
                    Column.ATDropout: "f",
                    Column.AccumulationLevel: "s",
                    Column.Barcodes: "s",
                    Column.CInRegions: "i",
                    Column.Category: "s",
                    Column.CpGInRegions: "i",
                    Column.CpGsInReference: "f",
                    Column.CsInReference: "f",
                    Column.EstimatedLibrarySize: "qi",
                    Column.FileSWID: "s",
                    Column.GCDropout: "f",
                    Column.GInRegions: "i",
                    Column.GsInReference: "f",
                    Column.Lane: "i",
                    Column.MeanReadLength: "f",
                    Column.MethylationBeta: "f",
                    Column.NormalizedCoverageQ1: "f",
                    Column.NormalizedCoverageQ2: "f",
                    Column.NormalizedCoverageQ3: "f",
                    Column.NormalizedCoverageQ4: "f",
                    Column.NormalizedCoverageQ5: "f",
                    Column.NumAlignedReads: "i",
                    Column.NumAthalianaMethylReads: "i",
                    Column.NumAthalianaUnmethylReads: "i",
                    Column.NumBadCycles: "i",
                    Column.NumDuplicatePairs: "i",
                    Column.NumNonPrimaryReads: "i",
                    Column.NumNonPrimaryReadsExamined: "i",
                    Column.NumOpticalDuplicatePairs: "i",
                    Column.NumReadsAfterDuplicateMarking: "i",
                    Column.NumReadsAlignedInPairs: "i",
                    Column.NumReadsWithCpG: "i",
                    Column.NumReadsWithoutCpG: "i",
                    Column.NumUnmappedReads: "i",
                    Column.NumUnmappedReadsAfterDuplicateMarking: "i",
                    Column.NumUnpairedDuplicateReads: "i",
                    Column.NumUnpairedReadsExamined: "i",
                    Column.NumWindowsWith0Reads: "i",
                    Column.NumWindowsWith100Reads: "i",
                    Column.NumWindowsWith10Reads: "i",
                    Column.NumWindowsWith1Reads: "i",
                    Column.NumWindowsWith50Reads: "i",
                    Column.ObservedToExpectedEnrichment: "f",
                    Column.ObservedToExpectedInReference: "f",
                    Column.ObservedToExpectedInRegions: "f",
                    Column.PassedFilterAlignedBases: "i",
                    Column.PassedFilterAlignedReads: "i",
                    Column.PassedFilterHQAlignedBases: "i",
                    Column.PassedFilterHQAlignedQ20Bases: "i",
                    Column.PassedFilterHQAlignedReads: "i",
                    Column.PassedFilterHQErrorFraction: "f",
                    Column.PassedFilterHQMedianMismatches: "i",
                    Column.PassedFilterIndelFraction: "f",
                    Column.PassedFilterMismatchFraction: "f",
                    Column.PassedFilterNoiseReads: "i",
                    Column.PassedFilterReads: "i",
                    Column.PercentChimeras: "f",
                    Column.PercentDuplication: "f",
                    Column.PercentPassedFilterAlignedReads: "f",
                    Column.PercentPassedFilterReads: "f",
                    Column.PercentReadsAlignedInPairs: "f",
                    Column.PercentageAthaliana: "f",
                    Column.PineryLimsID: "s",
                    Column.Reference: "s",
                    Column.RelativeCpGFreqInReference: "f",
                    Column.RelativeCpGFreqInRegions: "f",
                    Column.RelativeCpGFrequencyEnrichment: "f",
                    Column.Run: "s",
                    Column.SaturationAnalysisDoubledPearsonCorrelation: "f",
                    Column.SaturationAnalysisDoubledReads: "i",
                    Column.SaturationAnalysisTruePearsonCorrelation: "f",
                    Column.SaturationAnalysisTrueReads: "i",
                    Column.StrandBalance: "f",
                    Column.TotalClusters: "i",
                    Column.TotalReads: "i",
                    Column.WindowSize: "i",
                },
                "insert_metrics": {
                    InsertColumn.MedianInsertSize: "f",
                    InsertColumn.ModeInsertSize: "f",
                    InsertColumn.MedianAbsoluteDeviation: "f",
                    InsertColumn.MinInsertSize: "i",
                    InsertColumn.MaxInsertSize: "i",
                    InsertColumn.MeanInsertSize: "f",
                    InsertColumn.StandardDeviation: "f",
                    InsertColumn.ReadPairs: "i",
                    InsertColumn.PairOrientation: "s",
                    InsertColumn.PineryLimsID: "s",
                    InsertColumn.WidthOf10Percent: "i",
                    InsertColumn.WidthOf20Percent: "i",
                    InsertColumn.WidthOf30Percent: "i",
                    InsertColumn.WidthOf40Percent: "i",
                    InsertColumn.WidthOf50Percent: "i",
                    InsertColumn.WidthOf60Percent: "i",
                    InsertColumn.WidthOf70Percent: "i",
                    InsertColumn.WidthOf80Percent: "i",
                    InsertColumn.WidthOf90Percent: "i",
                    InsertColumn.WidthOf95Percent: "i",
                    InsertColumn.WidthOf99Percent: "i",
                    InsertColumn.InsertMedian10Percentile: "i",
                    InsertColumn.InsertMedian90Percentile: "i",
                    InsertColumn.Sample: "s",
                    InsertColumn.Library: "s",
                    InsertColumn.ReadGroup: "s",
                    InsertColumn.FileSWID: "s",
                    InsertColumn.Reference: "s",
                    InsertColumn.Run: "s",
                    InsertColumn.Lane: "i",
                    InsertColumn.Barcodes: "s",
                },
            }
        }
        self.columns = {
            4: {"cfmedipqc": Column, "insert_metrics": InsertColumn}
        }
        self.input_format = {
            "barcode": "s",
            "file": "p",
            "file_insert_stats": "p",
            "lane": "i",
            "pinery_lims_id": "s",
            "reference": "s",
            "run": "s",
            "swid": "s",
        }
        self.primary_key = {
            4: {
                "cfmedipqc": [Column.FileSWID],
                "insert_metrics": [InsertColumn.FileSWID],
            }
        }
        self.input_key = {4: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        df_dict = parse_record(
            single_input["file"], single_input["file_insert_stats"]
        )
        if schema_version == 4:
            return df_dict
        else:
            raise KeyError("Unknown version")

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "cfmedipqc": {
                Column.Barcodes: single_input["barcode"],
                Column.Lane: single_input["lane"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.Reference: single_input["reference"],
                Column.FileSWID: single_input["swid"],
            },
            "insert_metrics": {
                Column.Barcodes: single_input["barcode"],
                Column.Lane: single_input["lane"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.Reference: single_input["reference"],
                Column.FileSWID: single_input["swid"],
            },
        }
