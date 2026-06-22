import qcetl.common
import qcetl.picard.calculatecontamination.parse
from qcetl.column import (
    BaseCalculateContaminationColumn,
    CalculateContaminationCallReadyColumn,
    CalculateContaminationLaneLevelColumn,
)


class CalculateContaminationCallReady(qcetl.common.Cache):
    def __init__(self):
        self.name = "calculatecontamination"
        self.schema_versions = {
            2: {
                "calculatecontamination": {
                    CalculateContaminationCallReadyColumn.Donor: "s",
                    CalculateContaminationCallReadyColumn.GroupID: "s",
                    CalculateContaminationCallReadyColumn.FileSWID: "s",
                    CalculateContaminationCallReadyColumn.LibraryDesign: "s",
                    CalculateContaminationCallReadyColumn.MergedPineryLimsID: "as",
                    CalculateContaminationCallReadyColumn.Reference: "s",
                    CalculateContaminationCallReadyColumn.TissueOrigin: "s",
                    CalculateContaminationCallReadyColumn.TissueType: "s",
                    BaseCalculateContaminationColumn.Contamination: "f",
                    BaseCalculateContaminationColumn.Error: "f",
                    BaseCalculateContaminationColumn.Sample: "s",
                }
            }
        }
        self.columns = {
            2: {"calculatecontamination": CalculateContaminationCallReadyColumn}
        }
        self.input_format = {
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "reference": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "file": "p",
            "swid": "s",
        }
        # Workflow can be run in tumor + normal mode, but sample column is always tumor
        # Contamination can come from tumor or normal, so have a row for each
        # It is up to the consumer which workflow input they search/filter for
        self.primary_key = {
            2: {
                "calculatecontamination": [
                    CalculateContaminationCallReadyColumn.FileSWID,
                    CalculateContaminationCallReadyColumn.Donor,
                    CalculateContaminationCallReadyColumn.GroupID,
                    CalculateContaminationCallReadyColumn.LibraryDesign,
                    CalculateContaminationCallReadyColumn.TissueOrigin,
                    CalculateContaminationCallReadyColumn.TissueType,
                ]
            }
        }
        self.input_key = {
            2: ("swid", CalculateContaminationCallReadyColumn.FileSWID)
        }

    def parse_single_record(self, single_input, schema_version):
        df = qcetl.picard.calculatecontamination.parse.parse_record(
            single_input["file"]
        )
        return {2: {self.name: df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "calculatecontamination": {
                CalculateContaminationCallReadyColumn.Donor: single_input[
                    "donor"
                ],
                CalculateContaminationCallReadyColumn.GroupID: single_input[
                    "group_id"
                ],
                CalculateContaminationCallReadyColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                CalculateContaminationCallReadyColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                CalculateContaminationCallReadyColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                CalculateContaminationCallReadyColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                CalculateContaminationCallReadyColumn.TissueType: single_input[
                    "tissue_type"
                ],
                CalculateContaminationCallReadyColumn.FileSWID: single_input[
                    "swid"
                ],
            }
        }


class CalculateContaminationLaneLevel(qcetl.common.Cache):
    def __init__(self):
        self.name = "calculatecontamination_lane_level"
        self.schema_versions = {
            3: {
                "calculatecontamination": {
                    CalculateContaminationLaneLevelColumn.Donor: "s",
                    CalculateContaminationLaneLevelColumn.Barcodes: "s",
                    CalculateContaminationLaneLevelColumn.Lane: "i",
                    CalculateContaminationLaneLevelColumn.Run: "s",
                    CalculateContaminationLaneLevelColumn.PineryLimsID: "s",
                    CalculateContaminationLaneLevelColumn.Reference: "s",
                    CalculateContaminationLaneLevelColumn.FileSWID: "s",
                    BaseCalculateContaminationColumn.Contamination: "f",
                    BaseCalculateContaminationColumn.Error: "f",
                    BaseCalculateContaminationColumn.Sample: "s",
                }
            }
        }
        self.columns = {
            3: {"calculatecontamination": CalculateContaminationLaneLevelColumn}
        }
        self.input_format = {
            "donor": "s",
            "barcode": "s",
            "lane": "i",
            "run": "s",
            "pinery_lims_id": "s",
            "reference": "s",
            "file": "p",
            "swid": "s",
        }
        self.primary_key = {
            3: {
                "calculatecontamination": [
                    CalculateContaminationLaneLevelColumn.FileSWID
                ]
            }
        }
        self.input_key = {
            3: ("swid", CalculateContaminationLaneLevelColumn.FileSWID)
        }

    def parse_single_record(self, single_input, schema_version):
        df = qcetl.picard.calculatecontamination.parse.parse_record(
            single_input["file"]
        )
        return {3: {"calculatecontamination": df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "calculatecontamination": {
                CalculateContaminationLaneLevelColumn.Donor: single_input[
                    "donor"
                ],
                CalculateContaminationLaneLevelColumn.Barcodes: single_input[
                    "barcode"
                ],
                CalculateContaminationLaneLevelColumn.Lane: single_input[
                    "lane"
                ],
                CalculateContaminationLaneLevelColumn.Run: single_input["run"],
                CalculateContaminationLaneLevelColumn.PineryLimsID: single_input[
                    "pinery_lims_id"
                ],
                CalculateContaminationLaneLevelColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                CalculateContaminationLaneLevelColumn.FileSWID: single_input[
                    "swid"
                ],
            }
        }
