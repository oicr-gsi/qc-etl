import qcetl.common
from qcetl.column import BiomodalQcColumn, BiomodalQcMergedColumn
from qcetl.biomodalqc.parse import parse_record


class BiomodalQcMergedCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "biomodalqcmerged"
        self.schema_versions = {
            1: {
                "biomodalqc_table": {
                    BiomodalQcMergedColumn.DuplicationRate: "f",
                    BiomodalQcMergedColumn.LambdaMethylationModC: "f",
                    BiomodalQcMergedColumn.PUC19MethylationModC: "f",
                    BiomodalQcMergedColumn.Sq2hmcMethylation5mC: "f",
                    BiomodalQcMergedColumn.Sq2hmcMethylation5hmC: "f",
                    BiomodalQcMergedColumn.TotalClusters: "f",
                    BiomodalQcMergedColumn.FileSWID: "s",
                    BiomodalQcMergedColumn.Donor: "s",
                    BiomodalQcMergedColumn.GroupID: "s",
                    BiomodalQcMergedColumn.LibraryDesign: "s",
                    BiomodalQcMergedColumn.MergedPineryLimsID: "as",
                    BiomodalQcMergedColumn.TissueOrigin: "s",
                    BiomodalQcMergedColumn.TissueType: "s",
                }
            }
        }
        self.columns = {
            1: {
                "biomodalqc_table": BiomodalQcMergedColumn,
            }
        }
        self.input_format = {
            "biomodalqc_csv": "p",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {
            1: {
                "biomodalqc_table": [BiomodalQcMergedColumn.FileSWID],
            }
        }
        self.input_key = {1: ("swid", BiomodalQcMergedColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        biomodalqc_metrics = parse_record(single_input["biomodalqc_csv"])
        return {1: {"biomodalqc_table": biomodalqc_metrics}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "biomodalqc_table": {
                BiomodalQcMergedColumn.Donor: single_input["donor"],
                BiomodalQcMergedColumn.GroupID: single_input["group_id"],
                BiomodalQcMergedColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                BiomodalQcMergedColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                BiomodalQcMergedColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                BiomodalQcMergedColumn.TissueType: single_input["tissue_type"],
                BiomodalQcMergedColumn.FileSWID: single_input["swid"],
            }
        }


class BiomodalQcCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "biomodalqc"
        self.schema_versions = {
            1: {
                "biomodalqc_table": {
                    BiomodalQcColumn.DuplicationRate: "f",
                    BiomodalQcColumn.LambdaMethylationModC: "f",
                    BiomodalQcColumn.PUC19MethylationModC: "f",
                    BiomodalQcColumn.Sq2hmcMethylation5mC: "f",
                    BiomodalQcColumn.Sq2hmcMethylation5hmC: "f",
                    BiomodalQcColumn.TotalClusters: "f",
                    BiomodalQcColumn.FileSWID: "s",
                    BiomodalQcColumn.Donor: "s",
                    BiomodalQcColumn.Barcodes: "s",
                    BiomodalQcColumn.Lane: "i",
                    BiomodalQcColumn.PineryLimsID: "s",
                    BiomodalQcColumn.Run: "s",
                }
            }
        }
        self.columns = {
            1: {
                "biomodalqc_table": BiomodalQcColumn,
            }
        }
        self.input_format = {
            "biomodalqc_csv": "p",
            "donor": "s",
            "barcodes": "s",
            "lane": "s",
            "pinery_lims_id": "s",
            "run": "s",
            "swid": "s",
        }
        self.primary_key = {
            1: {
                "biomodalqc_table": [BiomodalQcColumn.FileSWID],
            }
        }
        self.input_key = {1: ("swid", BiomodalQcColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        biomodalqc_metrics = parse_record(single_input["biomodalqc_csv"])
        return {1: {"biomodalqc_table": biomodalqc_metrics}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "biomodalqc_table": {
                BiomodalQcColumn.Donor: single_input["donor"],
                BiomodalQcColumn.Barcodes: single_input["barcodes"],
                BiomodalQcColumn.Lane: single_input["lane"],
                BiomodalQcColumn.PineryLimsID: single_input["pinery_lims_id"],
                BiomodalQcColumn.Run: single_input["run"],
                BiomodalQcColumn.FileSWID: single_input["swid"],
            }
        }
