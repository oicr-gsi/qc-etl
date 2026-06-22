import qcetl.common
from qcetl.column import (
    BedToolsGenomeCovCoveragePercentileColumn as CovPercColumn,
    BedToolsGenomeCovCalculationsColumn as CalcColumn,
)
from qcetl.bedtools.parse import parse_record
from qcetl.bedtools.utility import genomecov_coverage_percentile


class BedToolsSarsCov2Cache(qcetl.common.Cache):
    def __init__(self):
        self.name = "bedtools_sars_cov2"
        self.schema_versions = {
            1: {
                "genomecov_coverage_percentile": {
                    CovPercColumn.Barcodes: "s",
                    CovPercColumn.Coverage: "i",
                    CovPercColumn.FileSWID: "s",
                    CovPercColumn.Lane: "i",
                    CovPercColumn.PercentGenomeCovered: "f",
                    CovPercColumn.PineryLimsID: "s",
                    CovPercColumn.Run: "s",
                },
                "genomecov_calculations": {
                    CalcColumn.Barcodes: "s",
                    CalcColumn.Coverage10Percentile: "i",
                    CalcColumn.Coverage90Percentile: "i",
                    CalcColumn.MeanCoverage: "f",
                    CalcColumn.MedianCoverage: "f",
                    CalcColumn.FileSWID: "s",
                    CalcColumn.Lane: "i",
                    CalcColumn.CoverageUniformity: "f",
                    CalcColumn.PineryLimsID: "s",
                    CalcColumn.Run: "s",
                },
            }
        }
        self.columns = {
            1: {
                "genomecov_coverage_percentile": CovPercColumn,
                "genomecov_calculations": CalcColumn,
            }
        }
        self.input_format = {
            "file_coverage_hist": "p",
            "file_genomecov": "p",
            "file_genomecov_per_base": "p",
            "swid": "s",
            "barcodes": "s",
            "lane": "i",
            "pinery_lims_id": "s",
            "run": "s",
        }
        self.primary_key = {
            1: {
                "genomecov_coverage_percentile": [
                    CovPercColumn.FileSWID,
                    CovPercColumn.Barcodes,
                    CovPercColumn.Lane,
                    CovPercColumn.Run,
                    CovPercColumn.Coverage,
                ],
                "genomecov_calculations": [
                    CalcColumn.FileSWID,
                    CalcColumn.Barcodes,
                    CalcColumn.Lane,
                    CalcColumn.Run,
                ],
            }
        }
        self.input_key = {1: ("swid", CovPercColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        calc, cov_percentile = parse_record(
            single_input["file_genomecov"],
            single_input["file_genomecov_per_base"],
        )
        return {
            1: {
                "genomecov_calculations": calc,
                "genomecov_coverage_percentile": cov_percentile,
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "genomecov_calculations": {
                CalcColumn.Barcodes: single_input["barcodes"],
                CalcColumn.Lane: single_input["lane"],
                CalcColumn.PineryLimsID: single_input["pinery_lims_id"],
                CalcColumn.Run: single_input["run"],
                CalcColumn.FileSWID: single_input["swid"],
            },
            "genomecov_coverage_percentile": {
                CovPercColumn.Barcodes: single_input["barcodes"],
                CovPercColumn.Lane: single_input["lane"],
                CovPercColumn.PineryLimsID: single_input["pinery_lims_id"],
                CovPercColumn.Run: single_input["run"],
                CovPercColumn.FileSWID: single_input["swid"],
            },
        }
