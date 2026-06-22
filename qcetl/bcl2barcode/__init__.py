import qcetl.common
from qcetl.column import Bcl2BarcodeColumn, Bcl2BarcodeRunSummaryColumn
from qcetl.bcl2barcode.parse import parse_record


class Bcl2BarcodeCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "bcl2barcode"
        self.schema_versions = {
            2: {
                "bcl2barcode": {
                    Bcl2BarcodeColumn.Barcodes: "s",
                    Bcl2BarcodeColumn.Count: "i",
                    Bcl2BarcodeColumn.FileSWID: "s",
                    Bcl2BarcodeColumn.Lane: "i",
                    Bcl2BarcodeColumn.PineryLimsID: "s",
                    Bcl2BarcodeColumn.Run: "s",
                },
                "run_summary": {
                    Bcl2BarcodeRunSummaryColumn.TotalClusters: "i",
                    Bcl2BarcodeRunSummaryColumn.Lane: "i",
                    Bcl2BarcodeRunSummaryColumn.FileSWID: "s",
                    Bcl2BarcodeRunSummaryColumn.PineryLimsID: "s",
                    Bcl2BarcodeRunSummaryColumn.Run: "s",
                },
            }
        }
        self.columns = {
            2: {
                "bcl2barcode": Bcl2BarcodeColumn,
                "run_summary": Bcl2BarcodeRunSummaryColumn,
            }
        }
        self.input_format = {
            "lane": "i",
            "path": "p",
            "run": "s",
            "pinery_lims_id": "s",
            "swid": "s",
        }
        self.primary_key = {
            2: {
                "bcl2barcode": [
                    Bcl2BarcodeColumn.FileSWID,
                    Bcl2BarcodeColumn.Barcodes,
                    Bcl2BarcodeColumn.Lane,
                    Bcl2BarcodeColumn.Run,
                ],
                "run_summary": [
                    Bcl2BarcodeRunSummaryColumn.FileSWID,
                    Bcl2BarcodeRunSummaryColumn.Lane,
                    Bcl2BarcodeRunSummaryColumn.Run,
                ],
            }
        }
        self.input_key = {2: ("swid", Bcl2BarcodeColumn.FileSWID)}

    @staticmethod
    def load_fixer_function(cleaning_rules, log_creator):
        def filter_function(df, name):
            if cleaning_rules.collapse_bcl2barcode_merged_flowcell:
                # Keep first lane of merged flowcell (all lanes have same File SWID)
                # The sorting puts min lane for each run on top
                # Dropping duplicates then will always keep the min lane for each run
                if name == "bcl2barcode":
                    df = df.sort_values(
                        [
                            Bcl2BarcodeColumn.Run,
                            Bcl2BarcodeColumn.Lane,
                            Bcl2BarcodeColumn.Count,
                        ]
                    )
                    df = df.drop_duplicates(
                        [
                            Bcl2BarcodeColumn.Run,
                            Bcl2BarcodeColumn.Barcodes,
                            Bcl2BarcodeColumn.FileSWID,
                        ]
                    )
                elif name == "run_summary":
                    df = df.sort_values(
                        [
                            Bcl2BarcodeRunSummaryColumn.Run,
                            Bcl2BarcodeRunSummaryColumn.Lane,
                        ]
                    )
                    df = df.drop_duplicates(
                        [
                            Bcl2BarcodeRunSummaryColumn.Run,
                            Bcl2BarcodeRunSummaryColumn.FileSWID,
                        ]
                    )

            return df

        return filter_function

    def parse_single_record(self, single_input, schema_version):
        df, summary = parse_record(single_input["path"])
        return {2: {"bcl2barcode": df, "run_summary": summary}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "bcl2barcode": {
                Bcl2BarcodeColumn.Run: single_input["run"],
                Bcl2BarcodeColumn.Lane: single_input["lane"],
                Bcl2BarcodeColumn.PineryLimsID: single_input["pinery_lims_id"],
                Bcl2BarcodeColumn.FileSWID: single_input["swid"],
            },
            "run_summary": {
                Bcl2BarcodeRunSummaryColumn.Run: single_input["run"],
                Bcl2BarcodeRunSummaryColumn.Lane: single_input["lane"],
                Bcl2BarcodeRunSummaryColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                Bcl2BarcodeRunSummaryColumn.FileSWID: single_input["swid"],
            },
        }
