from typing import Dict

from pandas import DataFrame, read_csv

import qcetl.common
from qcetl.column import (
    CrosscheckFingerprintCallerCallsColumn as CallsColumn,
    CrosscheckFingerprintCallerDetailedColumn as DetailedColumn,
)


class CrosscheckFingerprintCaller(qcetl.common.Cache):
    def __init__(self):
        self.name = "crosscheckfingerprint_caller"
        self.schema_versions = {
            1: {
                "calls": {
                    CallsColumn.Barcode: "s",
                    CallsColumn.Batches: "s",
                    CallsColumn.Donor: "s",
                    CallsColumn.ExternalDonor: "s",
                    CallsColumn.FileSWID: "s",
                    CallsColumn.Grouping: "s",
                    CallsColumn.GroupingName: "s",
                    CallsColumn.Lane: "i",
                    CallsColumn.LibraryDesign: "s",
                    CallsColumn.LibraryName: "s",
                    CallsColumn.PineryLimsID: "s",
                    CallsColumn.Project: "s",
                    CallsColumn.Run: "s",
                    CallsColumn.SwapCall: "b",
                    CallsColumn.TissueOrigin: "s",
                    CallsColumn.TissueType: "s",
                },
                "detailed": {
                    DetailedColumn.Barcode: "s",
                    DetailedColumn.BarcodeMatch: "s",
                    DetailedColumn.Batches: "s",
                    DetailedColumn.BatchesMatched: "s",
                    DetailedColumn.Donor: "s",
                    DetailedColumn.DonorMatch: "s",
                    DetailedColumn.ExternalDonor: "s",
                    DetailedColumn.ExternalDonorMatch: "s",
                    DetailedColumn.FileSWID: "s",
                    DetailedColumn.Grouping: "s",
                    DetailedColumn.GroupingName: "s",
                    DetailedColumn.Lane: "i",
                    DetailedColumn.LaneMatch: "i",
                    DetailedColumn.LibraryDesign: "s",
                    DetailedColumn.LibraryDesignMatch: "s",
                    DetailedColumn.LibraryName: "s",
                    DetailedColumn.LibraryNameMatch: "s",
                    DetailedColumn.LODScore: "f",
                    DetailedColumn.MatchCalled: "b",
                    DetailedColumn.OverlapBatch: "qs",
                    DetailedColumn.PairwiseSwap: "b",
                    DetailedColumn.PineryLimsID: "s",
                    DetailedColumn.PineryLimsIDMatch: "s",
                    DetailedColumn.Project: "s",
                    DetailedColumn.ProjectMatch: "s",
                    DetailedColumn.Run: "s",
                    DetailedColumn.RunMatch: "s",
                    DetailedColumn.SameBatch: "b",
                    DetailedColumn.SwapCall: "b",
                    DetailedColumn.TissueOrigin: "s",
                    DetailedColumn.TissueOriginMatch: "s",
                    DetailedColumn.TissueType: "s",
                    DetailedColumn.TissueTypeMatch: "s",
                },
            }
        }
        self.columns = {
            1: {
                "calls": CallsColumn,
                "detailed": DetailedColumn,
            }
        }
        self.input_format = {
            "file_detailed": "p",
            "file_calls": "p",
            "grouping": "s",
            "grouping_name": "s",
            "swid": "s",
        }

        self.primary_key = {
            1: {
                "calls": [
                    CallsColumn.FileSWID,
                    CallsColumn.Barcode,
                    CallsColumn.Lane,
                    CallsColumn.Run,
                ],
                "detailed": [
                    DetailedColumn.FileSWID,
                    DetailedColumn.Barcode,
                    DetailedColumn.BarcodeMatch,
                    DetailedColumn.Lane,
                    DetailedColumn.LaneMatch,
                    DetailedColumn.Run,
                    DetailedColumn.RunMatch,
                ],
            }
        }

        self.input_key = {1: ("swid", CallsColumn.FileSWID)}

    def parse_single_record(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, DataFrame]:
        calls = read_csv(single_input["file_calls"])
        detailed = read_csv(single_input["file_detailed"])

        return {
            "calls": calls,
            "detailed": detailed,
        }

    def add_shesmu_metadata(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, Dict[str, str]]:
        return {
            "calls": {
                CallsColumn.Grouping: single_input["grouping"],
                CallsColumn.GroupingName: single_input["grouping_name"],
                CallsColumn.FileSWID: single_input["swid"],
            },
            "detailed": {
                DetailedColumn.Grouping: single_input["grouping"],
                DetailedColumn.GroupingName: single_input["grouping_name"],
                DetailedColumn.FileSWID: single_input["swid"],
            },
        }


class CrosscheckFingerprintCallerAutoVerification(CrosscheckFingerprintCaller):
    def __init__(self):
        super().__init__()
        self.name = "crosscheckfingerprint_caller_autoverification"
