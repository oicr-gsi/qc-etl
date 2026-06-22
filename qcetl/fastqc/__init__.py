import qcetl.common
from qcetl.column import FastqcColumn as Column
from qcetl.fastqc.parse import parse_record


class FastQcCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "fastqc"
        self.schema_versions = {
            1: {
                "fastqc": {
                    Column.Barcodes: "s",
                    Column.Encoding: "s",
                    Column.FileSWID: "s",
                    Column.FileType: "s",
                    Column.FilteredSequences: "qi",
                    Column.Lane: "i",
                    Column.PercentGC: "f",
                    Column.PineryLimsID: "s",
                    Column.ReadNumber: "i",
                    Column.Run: "s",
                    Column.SequenceLength: "i",
                    Column.SequenceLengthMax: "qi",
                    Column.SequencesFlaggedPoorQuality: "i",
                    Column.StatusBasicStatistics: "s",
                    Column.StatusKmerContent: "s",
                    Column.StatusOverrepresentedSequences: "s",
                    Column.StatusPerBaseGCContent: "s",
                    Column.StatusPerBaseNContent: "s",
                    Column.StatusPerBaseSequenceContent: "s",
                    Column.StatusPerBaseSequenceQuality: "s",
                    Column.StatusPerSequenceGCContent: "s",
                    Column.StatusPerSequenceQualityScores: "s",
                    Column.StatusSequenceDuplicationLevels: "s",
                    Column.StatusSequenceLengthDistribution: "s",
                    Column.TotalSequences: "i",
                    Column.Version: "s",
                }
            }
        }
        self.columns = {1: {"fastqc": Column}}
        self.input_format = {
            "barcode": "s",
            "file": "p",
            "lane": "i",
            "pinery_lims_id": "s",
            "read": "i",
            "run": "s",
            "swid": "s",
        }
        self.primary_key = {1: {"fastqc": [Column.FileSWID]}}
        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {"fastqc": parse_record(single_input["file"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "fastqc": {
                Column.Barcodes: single_input["barcode"],
                Column.Lane: single_input["lane"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.ReadNumber: single_input["read"],
                Column.FileSWID: single_input["swid"],
            }
        }
