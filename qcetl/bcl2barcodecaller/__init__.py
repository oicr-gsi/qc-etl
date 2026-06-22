import qcetl.common
from qcetl.column import (
    Bcl2BarcodeCallerSummaryColumn,
    Bcl2BarcodeCallerKnownColumn,
    Bcl2BarcodeCallerUnknownColumn,
)
from qcetl.bcl2barcodecaller.parse import parse_record


class Bcl2BarcodeCallerCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "bcl2barcodecaller"
        self.schema_versions = {
            1: {
                "known": {
                    Bcl2BarcodeCallerKnownColumn.Barcodes: "s",
                    Bcl2BarcodeCallerKnownColumn.Count: "i",
                    Bcl2BarcodeCallerKnownColumn.LibraryAlias: "s",
                    Bcl2BarcodeCallerKnownColumn.FileSWID: "s",
                    Bcl2BarcodeCallerKnownColumn.Lane: "i",
                    Bcl2BarcodeCallerKnownColumn.PineryLimsID: "s",
                    Bcl2BarcodeCallerKnownColumn.Run: "s",
                },
                "summary": {
                    Bcl2BarcodeCallerSummaryColumn.TotalClusters: "i",
                    Bcl2BarcodeCallerSummaryColumn.ExcludedClusters: "i",
                    Bcl2BarcodeCallerSummaryColumn.KnownClusters: "i",
                    Bcl2BarcodeCallerSummaryColumn.UnknownClusters: "i",
                    Bcl2BarcodeCallerSummaryColumn.Lane: "i",
                    Bcl2BarcodeCallerSummaryColumn.FileSWID: "s",
                    Bcl2BarcodeCallerSummaryColumn.PineryLimsID: "s",
                    Bcl2BarcodeCallerSummaryColumn.Run: "s",
                },
                "unknown": {
                    Bcl2BarcodeCallerUnknownColumn.Barcodes: "s",
                    Bcl2BarcodeCallerUnknownColumn.Count: "i",
                    Bcl2BarcodeCallerUnknownColumn.FileSWID: "s",
                    Bcl2BarcodeCallerUnknownColumn.Lane: "i",
                    Bcl2BarcodeCallerUnknownColumn.PineryLimsID: "s",
                    Bcl2BarcodeCallerUnknownColumn.Run: "s",
                },
            }
        }
        self.columns = {
            1: {
                "known": Bcl2BarcodeCallerKnownColumn,
                "summary": Bcl2BarcodeCallerSummaryColumn,
                "unknown": Bcl2BarcodeCallerUnknownColumn,
            }
        }
        self.input_format = {
            "lane": "i",
            "path": "p",
            "run": "s",
            "pinery_lims_id": "s",
            "swid": "s",
            "known_barcodes": "at2ss",
        }
        self.primary_key = {
            1: {
                "known": [
                    Bcl2BarcodeCallerKnownColumn.FileSWID,
                    Bcl2BarcodeCallerKnownColumn.Barcodes,
                    Bcl2BarcodeCallerKnownColumn.Lane,
                    Bcl2BarcodeCallerKnownColumn.Run,
                ],
                "summary": [
                    Bcl2BarcodeCallerSummaryColumn.FileSWID,
                    Bcl2BarcodeCallerSummaryColumn.Lane,
                    Bcl2BarcodeCallerSummaryColumn.Run,
                ],
                "unknown": [
                    Bcl2BarcodeCallerKnownColumn.FileSWID,
                    Bcl2BarcodeCallerKnownColumn.Barcodes,
                    Bcl2BarcodeCallerKnownColumn.Lane,
                    Bcl2BarcodeCallerKnownColumn.Run,
                ],
            }
        }
        self.input_key = {1: ("swid", Bcl2BarcodeCallerSummaryColumn.FileSWID)}

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            if cleaning_rules.collapse_bcl2barcode_merged_flowcell:
                # Keep first lane of merged flowcell (all lanes have same File SWID)
                # The sorting puts min lane for each run on top
                # Dropping duplicates then will always keep the min lane for each run
                if name == "known" or name == "unknown":
                    df = df.sort_values(
                        [
                            Bcl2BarcodeCallerKnownColumn.Run,
                            Bcl2BarcodeCallerKnownColumn.Lane,
                            Bcl2BarcodeCallerKnownColumn.Count,
                        ]
                    )
                    df = df.drop_duplicates(
                        [
                            Bcl2BarcodeCallerKnownColumn.Run,
                            Bcl2BarcodeCallerKnownColumn.Barcodes,
                            Bcl2BarcodeCallerKnownColumn.FileSWID,
                        ]
                    )
                elif name == "summary":
                    df = df.sort_values(
                        [
                            Bcl2BarcodeCallerSummaryColumn.Run,
                            Bcl2BarcodeCallerSummaryColumn.Lane,
                        ]
                    )
                    df = df.drop_duplicates(
                        [
                            Bcl2BarcodeCallerSummaryColumn.Run,
                            Bcl2BarcodeCallerSummaryColumn.FileSWID,
                        ]
                    )

            return df

        return filter_function

    def parse_single_record(self, single_input, schema_version):
        return {
            1: parse_record(
                single_input["path"], single_input["known_barcodes"]
            )
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "known": {
                Bcl2BarcodeCallerKnownColumn.Run: single_input["run"],
                Bcl2BarcodeCallerKnownColumn.Lane: single_input["lane"],
                Bcl2BarcodeCallerKnownColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                Bcl2BarcodeCallerKnownColumn.FileSWID: single_input["swid"],
            },
            "summary": {
                Bcl2BarcodeCallerSummaryColumn.Run: single_input["run"],
                Bcl2BarcodeCallerSummaryColumn.Lane: single_input["lane"],
                Bcl2BarcodeCallerSummaryColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                Bcl2BarcodeCallerSummaryColumn.FileSWID: single_input["swid"],
            },
            "unknown": {
                Bcl2BarcodeCallerUnknownColumn.Run: single_input["run"],
                Bcl2BarcodeCallerUnknownColumn.Lane: single_input["lane"],
                Bcl2BarcodeCallerUnknownColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                Bcl2BarcodeCallerUnknownColumn.FileSWID: single_input["swid"],
            },
        }
