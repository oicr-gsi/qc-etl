import qcetl.common
from qcetl.column import PurityQcSequenzaColumn as SequenzaColumn
from qcetl.purityqc_sequenza.parse import parse_record


class PurityQcSequenzaCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "purityqc_sequenza"
        self.schema_versions = {
            1: {
                "sequenza_purity_ploidy_table": {
                    SequenzaColumn.defaultGamma: "i",
                    SequenzaColumn.defaultPurity: "f",
                    SequenzaColumn.defaultPloidy: "f",
                    SequenzaColumn.minPurity: "f",
                    SequenzaColumn.minPloidy: "f",
                    SequenzaColumn.maxPurity: "f",
                    SequenzaColumn.maxPloidy: "f",
                    SequenzaColumn.FileSWID: "s",
                    SequenzaColumn.Donor: "s",
                    SequenzaColumn.GroupID: "s",
                    SequenzaColumn.LibraryDesign: "s",
                    SequenzaColumn.MergedPineryLimsID: "as",
                    SequenzaColumn.TissueOrigin: "s",
                    SequenzaColumn.TissueType: "s",
                }
            }
        }
        self.columns = {1: {"sequenza_purity_ploidy_table": SequenzaColumn}}
        self.input_format = {
            "sequenza_input": "p",
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
                "sequenza_purity_ploidy_table": [
                    SequenzaColumn.FileSWID,
                    SequenzaColumn.defaultPloidy,
                    SequenzaColumn.defaultGamma,
                ]
            }
        }
        self.input_key = {1: ("swid", SequenzaColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        purity_ploidy_table_df = parse_record(single_input["sequenza_input"])
        return {1: {"sequenza_purity_ploidy_table": purity_ploidy_table_df}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "sequenza_purity_ploidy_table": {
                SequenzaColumn.Donor: single_input["donor"],
                SequenzaColumn.GroupID: single_input["group_id"],
                SequenzaColumn.LibraryDesign: single_input["library_design"],
                SequenzaColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                SequenzaColumn.TissueOrigin: single_input["tissue_origin"],
                SequenzaColumn.TissueType: single_input["tissue_type"],
                SequenzaColumn.FileSWID: single_input["swid"],
            }
        }
