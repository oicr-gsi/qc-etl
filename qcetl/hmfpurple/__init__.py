import qcetl.common
from qcetl.column import HmfPurpleColumn as Column
from qcetl.hmfpurple.parse import parse_record


class HmfPurpleCache(qcetl.common.Cache):
    """
    Tumour purity/ploidy QC from hmftools PURPLE, run on a merged/call-ready
    tumour. One build record points at the ``*.purple.purity.tsv`` file.
    """

    def __init__(self):
        self.name = "hmfpurple"

        # Merged/call-ready identifiers
        identifiers = {
            Column.Donor: "s",
            Column.FileSWID: "s",
            Column.GroupID: "s",
            Column.LibraryDesign: "s",
            Column.MergedPineryLimsID: "as",
            Column.Project: "s",
            Column.Reference: "s",
            Column.TissueOrigin: "s",
            Column.TissueType: "s",
        }

        self.schema_versions = {
            1: {
                "purity": {
                    **identifiers,
                    Column.WorkflowVersion: "qs",
                    Column.Purity: "f",
                },
            }
        }

        self.columns = {1: {"purity": Column}}

        self.input_format = {
            "project": "s",
            "pinery_lims_ids": "as",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "reference": "s",
            "path": "p",
            "swid": "s",
            "workflow_version": ["i", "i", "i"],
        }

        self.primary_key = {1: {"purity": [Column.FileSWID]}}

        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(single_input["path"])
        return {1: {"purity": df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "purity": {
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.Project: single_input["project"],
                Column.Reference: single_input.get("reference", "Unknown"),
                Column.FileSWID: single_input["swid"],
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.LibraryDesign: single_input["library_design"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.WorkflowVersion: ".".join(
                    str(x) for x in single_input["workflow_version"]
                ),
            }
        }
