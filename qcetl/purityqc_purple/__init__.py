import qcetl.common
from qcetl.column import PurityQcPurpleColumn as PurpleColumn
from qcetl.purityqc_purple.parse import parse_record


class PurityQcPurpleCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "purityqc_purple"
        self.schema_versions = {
            1: {
                "purple_purity_ploidy_table": {
                    PurpleColumn.Purity: "f",
                    PurpleColumn.Ploidy: "f",
                    PurpleColumn.NormFactor: "f",
                    PurpleColumn.Score: "f",
                    PurpleColumn.DiploidProportion: "f",
                    PurpleColumn.PolyclonalProportion: "f",
                    PurpleColumn.MinPurity: "f",
                    PurpleColumn.MaxPurity: "f",
                    PurpleColumn.MinPloidy: "f",
                    PurpleColumn.MaxPloidy: "f",
                    PurpleColumn.MinDiploidProportion: "f",
                    PurpleColumn.MaxDiploidProportion: "f",
                    PurpleColumn.SomaticPenalty: "f",
                    PurpleColumn.FileSWID: "s",
                    PurpleColumn.Donor: "s",
                    PurpleColumn.GroupID: "s",
                    PurpleColumn.LibraryDesign: "s",
                    PurpleColumn.MergedPineryLimsID: "as",
                    PurpleColumn.TissueOrigin: "s",
                    PurpleColumn.TissueType: "s",
                }
            }
        }
        self.columns = {
            1: {
                "purple_purity_ploidy_table": PurpleColumn,
            }
        }
        self.input_format = {
            "purple_purity_input": "p",
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
                "purple_purity_ploidy_table": [
                    PurpleColumn.FileSWID,
                    PurpleColumn.Ploidy,
                    PurpleColumn.Purity,
                ],
            }
        }
        self.input_key = {1: ("swid", PurpleColumn.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        purple_purity_df = parse_record(single_input["purple_purity_input"])
        return {1: {"purple_purity_ploidy_table": purple_purity_df}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "purple_purity_ploidy_table": {
                PurpleColumn.Donor: single_input["donor"],
                PurpleColumn.GroupID: single_input["group_id"],
                PurpleColumn.LibraryDesign: single_input["library_design"],
                PurpleColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                PurpleColumn.TissueOrigin: single_input["tissue_origin"],
                PurpleColumn.TissueType: single_input["tissue_type"],
                PurpleColumn.FileSWID: single_input["swid"],
            }
        }
