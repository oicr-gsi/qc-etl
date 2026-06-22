import qcetl.common
from qcetl.column import BwaMemCutAdaptColumn
from qcetl.bwamem.parse import parse_record


class BwaMemCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "bwamem"
        self.schema_versions = {
            1: {
                "cutadapt": {
                    BwaMemCutAdaptColumn.Barcodes: "s",
                    BwaMemCutAdaptColumn.FileSWID: "s",
                    BwaMemCutAdaptColumn.Lane: "i",
                    BwaMemCutAdaptColumn.Reference: "s",
                    BwaMemCutAdaptColumn.Run: "s",
                    BwaMemCutAdaptColumn.TotalReadPairsProcessed: "i",
                    BwaMemCutAdaptColumn.Read1WithAdapter: "i",
                    BwaMemCutAdaptColumn.Read1WithAdapterPercentage: "f",
                    BwaMemCutAdaptColumn.Read2WithAdapter: "i",
                    BwaMemCutAdaptColumn.Read2WithAdapterPercentage: "f",
                    BwaMemCutAdaptColumn.PairsThatWereTooShort: "i",
                    BwaMemCutAdaptColumn.PairsThatWereTooShortPercentage: "f",
                    BwaMemCutAdaptColumn.PairsWrittenPassingFilters: "i",
                    BwaMemCutAdaptColumn.PairsWrittenPassingFiltersPercentage: "f",
                    BwaMemCutAdaptColumn.TotalBasepairsProcessed: "i",
                    BwaMemCutAdaptColumn.TotalBasepairsProcessedRead1: "i",
                    BwaMemCutAdaptColumn.TotalBasepairsProcessedRead2: "i",
                    BwaMemCutAdaptColumn.QualityTrimmed: "i",
                    BwaMemCutAdaptColumn.QualityTrimmedPercentage: "f",
                    BwaMemCutAdaptColumn.QualityTrimmedRead1: "i",
                    BwaMemCutAdaptColumn.QualityTrimmedRead2: "i",
                    BwaMemCutAdaptColumn.TotalWrittenFiltered: "i",
                    BwaMemCutAdaptColumn.TotalWrittenFilteredPercentage: "f",
                    BwaMemCutAdaptColumn.TotalWrittenFilteredRead1: "i",
                    BwaMemCutAdaptColumn.TotalWrittenFilteredRead2: "i",
                }
            }
        }
        self.columns = {1: {"cutadapt": BwaMemCutAdaptColumn}}
        self.input_format = {
            "lane": "i",
            "path": "p",
            "run": "s",
            "swid": "s",
            "reference": "s",
            "barcode": "s",
        }
        self.primary_key = {1: {"cutadapt": [BwaMemCutAdaptColumn.FileSWID]}}
        self.input_key = {1: ("swid", BwaMemCutAdaptColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        return {1: {"cutadapt": parse_record(single_input["path"])}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "cutadapt": {
                BwaMemCutAdaptColumn.Barcodes: single_input["barcode"],
                BwaMemCutAdaptColumn.Lane: single_input["lane"],
                BwaMemCutAdaptColumn.Run: single_input["run"],
                BwaMemCutAdaptColumn.Reference: single_input["reference"],
                BwaMemCutAdaptColumn.FileSWID: single_input["swid"],
            }
        }
