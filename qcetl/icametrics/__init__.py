import qcetl.common
from qcetl.column import ICAMetricsColumn as Column
from qcetl.icametrics.parse import parse_record


class ICAMetricsCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "icametrics"
        self.schema_versions = {
            1: {
                "icametrics": {
                    Column.PineryLimsID: "s",
                    Column.Run: "s",
                    Column.Project: "s",
                    Column.DeID: "s",
                    Column.MeanCovGenome: "f",
                    Column.MeanCovFull: "f",
                    Column.MeanCovSub: "f",
                    Column.FailedRegion: "f",
                    Column.PctGenome: "f",
                    Column.UniCov: "f",
                    Column.Sex: "s",
                    Column.ObsSex: "s",
                    Column.PctMapped: "f",
                    Column.PctUnique: "f",
                    Column.MeanInsertLength: "f",
                    Column.MedInsertLength: "f",
                    Column.TiTvRatio: "f",
                    Column.PctAutosome: "f",
                    Column.CovUni: "f",
                    Column.DupDelRatio: "f",
                }
            }
        }
        self.columns = {1: {"icametrics": Column}}
        self.input_format = {
            "project": "s",
            "run": "s",
            "de_id": "s",
            "sex": "s",
            "pinery_lims_id": "s",
            "run_dir": "s",
        }
        self.primary_key = {1: {"icametrics": [Column.PineryLimsID]}}
        self.input_key = {1: ("pinery_lims_id", Column.PineryLimsID)}

    def parse_single_record(self, single_input, schema_version):
        return {
            1: {
                "icametrics": parse_record(
                    single_input["run"],
                    single_input["de_id"],
                    single_input["sex"],
                    single_input["run_dir"],
                )
            }
        }[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "icametrics": {
                Column.PineryLimsID: single_input["pinery_lims_id"],
                Column.Run: single_input["run"],
                Column.Project: single_input["project"],
            }
        }
