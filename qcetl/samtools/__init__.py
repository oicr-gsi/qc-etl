import qcetl.common
from qcetl.column import SamtoolsStatsColumn as Column
from qcetl.samtools.parse_stats import parse_sn


class SamtoolsStatsCov2Cache(qcetl.common.Cache):
    def __init__(self):
        self.name = "samtools_stats_sars_cov2"
        self.schema_versions = {
            1: {
                "human": {
                    Column.RawTotalSequences: "i",
                    Column.FilteredSequences: "i",
                    Column.Sequences: "i",
                    Column.IsSorted: "i",
                    Column.FirstFragments: "i",
                    Column.LastFragments: "i",
                    Column.ReadsMapped: "i",
                    Column.ReadsMappedAndPaired: "i",
                    Column.ReadsUnmapped: "i",
                    Column.ReadsProperlyPaired: "i",
                    Column.ReadsPaired: "i",
                    Column.ReadsDuplicated: "i",
                    Column.ReadsmQ0: "i",
                    Column.ReadsQCFailed: "i",
                    Column.NonPrimaryAlignments: "i",
                    Column.TotalLength: "i",
                    Column.TotalFirstFragmentLength: "i",
                    Column.TotalLastFragmentLength: "i",
                    Column.BasesMapped: "i",
                    Column.BasesMappedCigar: "i",
                    Column.BasesTrimmed: "i",
                    Column.BasesDuplicated: "i",
                    Column.Mismatches: "i",
                    Column.ErrorRate: "f",
                    Column.AverageLength: "f",
                    Column.AverageFirstFragmentLength: "f",
                    Column.AverageLastFragmentLength: "f",
                    Column.MaximumLength: "i",
                    Column.MaximumFirstFragmentLength: "i",
                    Column.MaximumLastFragmentLength: "i",
                    Column.AverageQuality: "f",
                    Column.InsertSizeAverage: "f",
                    Column.InsertSizeStandardDeviation: "f",
                    Column.InwardOrientedPairs: "i",
                    Column.OutwardOrientedPairs: "i",
                    Column.PairsWithOtherOrientation: "i",
                    Column.PairsOnDifferentChromosomes: "i",
                    Column.PercentageOfProperlyPairedReads: "f",
                    Column.FileSWID: "s",
                    Column.Barcodes: "s",
                    Column.Lane: "i",
                    Column.PineryLimsID: "s",
                    Column.Run: "s",
                },
                "depleted": {
                    Column.RawTotalSequences: "i",
                    Column.FilteredSequences: "i",
                    Column.Sequences: "i",
                    Column.IsSorted: "i",
                    Column.FirstFragments: "i",
                    Column.LastFragments: "i",
                    Column.ReadsMapped: "i",
                    Column.ReadsMappedAndPaired: "i",
                    Column.ReadsUnmapped: "i",
                    Column.ReadsProperlyPaired: "i",
                    Column.ReadsPaired: "i",
                    Column.ReadsDuplicated: "i",
                    Column.ReadsmQ0: "i",
                    Column.ReadsQCFailed: "i",
                    Column.NonPrimaryAlignments: "i",
                    Column.TotalLength: "i",
                    Column.TotalFirstFragmentLength: "i",
                    Column.TotalLastFragmentLength: "i",
                    Column.BasesMapped: "i",
                    Column.BasesMappedCigar: "i",
                    Column.BasesTrimmed: "i",
                    Column.BasesDuplicated: "i",
                    Column.Mismatches: "i",
                    Column.ErrorRate: "f",
                    Column.AverageLength: "f",
                    Column.AverageFirstFragmentLength: "f",
                    Column.AverageLastFragmentLength: "f",
                    Column.MaximumLength: "i",
                    Column.MaximumFirstFragmentLength: "i",
                    Column.MaximumLastFragmentLength: "i",
                    Column.AverageQuality: "f",
                    Column.InsertSizeAverage: "f",
                    Column.InsertSizeStandardDeviation: "f",
                    Column.InwardOrientedPairs: "i",
                    Column.OutwardOrientedPairs: "i",
                    Column.PairsWithOtherOrientation: "i",
                    Column.PairsOnDifferentChromosomes: "i",
                    Column.PercentageOfProperlyPairedReads: "f",
                    Column.FileSWID: "s",
                    Column.Barcodes: "s",
                    Column.Lane: "i",
                    Column.PineryLimsID: "s",
                    Column.Run: "s",
                },
            }
        }
        self.columns = {1: {"human": Column, "depleted": Column}}
        self.input_format = {
            "file_human": "p",
            "file_depleted": "p",
            "swid": "s",
            "barcodes": "s",
            "lane": "i",
            "pinery_lims_id": "s",
            "run": "s",
        }
        self.primary_key = {
            1: {"human": [Column.FileSWID], "depleted": [Column.FileSWID]}
        }
        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {
            1: {
                "human": parse_sn(single_input["file_human"]),
                "depleted": parse_sn(single_input["file_depleted"]),
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "human": {
                Column.Barcodes: single_input["barcodes"],
                Column.Lane: single_input["lane"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.FileSWID: single_input["swid"],
            },
            "depleted": {
                Column.Barcodes: single_input["barcodes"],
                Column.Lane: single_input["lane"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.FileSWID: single_input["swid"],
            },
        }
