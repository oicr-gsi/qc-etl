import qcetl.common
from qcetl.column import (
    IchorCnaColumn,
    IchorCnaMergedColumn,
    BaseIchorCnaColumn,
)
from qcetl.ichorcna.parse import parse_record


class BaseIchorCnaCache(qcetl.common.Cache):
    def __init__(
        self,
        name,
        column,
        identifiers,
        input_identifiers,
        primary_key,
        input_key,
    ):
        self.name = name
        self.schema_versions = {
            1: {
                name: {
                    **identifiers,
                    BaseIchorCnaColumn.ChrXMedianLogRation: "f",
                    BaseIchorCnaColumn.ChrYCoverageFraction: "f",
                    BaseIchorCnaColumn.Coverage: "f",
                    BaseIchorCnaColumn.FractionCnaSubclonal: "f",
                    BaseIchorCnaColumn.FractionGenomeSubclonal: "f",
                    BaseIchorCnaColumn.GCMapCorrectionMAD: "f",
                    BaseIchorCnaColumn.GammaRateInit: "f",
                    BaseIchorCnaColumn.Gender: "s",
                    BaseIchorCnaColumn.Ploidy: "f",
                    BaseIchorCnaColumn.SubcloneFraction: "f",
                    BaseIchorCnaColumn.TumorFraction: "f",
                }
            }
        }
        self.columns = {1: {name: column}}
        self.input_format = {**input_identifiers, "file": "p", "swid": "s"}
        self.primary_key = primary_key
        self.input_key = input_key

    def parse_single_record(self, single_input, schema_version):
        cols = self.schema_versions[schema_version][self.name]
        return {1: {self.name: parse_record(single_input["file"], cols)}}[
            schema_version
        ]

    def add_shesmu_metadata(self, single_input, schema_version):
        raise NotImplementedError


class IchorCnaCache(BaseIchorCnaCache):
    def __init__(self):
        super().__init__(
            "ichorcna",
            IchorCnaColumn,
            {
                IchorCnaColumn.Barcodes: "s",
                IchorCnaColumn.Lane: "i",
                IchorCnaColumn.PineryLimsID: "s",
                IchorCnaColumn.Run: "s",
                IchorCnaColumn.Reference: "s",
                IchorCnaColumn.FileSWID: "s",
            },
            {
                "run": "s",
                "lane": "i",
                "barcode": "s",
                "pinery_lims_id": "s",
                "reference": "s",
            },
            {1: {"ichorcna": [IchorCnaColumn.FileSWID]}},
            {1: ("swid", IchorCnaColumn.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ichorcna": {
                IchorCnaColumn.Run: single_input["run"],
                IchorCnaColumn.Lane: single_input["lane"],
                IchorCnaColumn.Barcodes: single_input["barcode"],
                IchorCnaColumn.PineryLimsID: single_input["pinery_lims_id"],
                IchorCnaColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCnaColumn.FileSWID: single_input["swid"],
            }
        }


class IchorCnaMergedCache(BaseIchorCnaCache):
    def __init__(self):
        super().__init__(
            "ichorcnamerged",
            IchorCnaMergedColumn,
            {
                IchorCnaMergedColumn.Donor: "s",
                IchorCnaMergedColumn.GroupID: "s",
                IchorCnaMergedColumn.LibraryDesign: "s",
                IchorCnaMergedColumn.MergedPineryLimsID: "as",
                IchorCnaMergedColumn.Project: "s",
                IchorCnaMergedColumn.Reference: "s",
                IchorCnaMergedColumn.TissueOrigin: "s",
                IchorCnaMergedColumn.TissueType: "s",
                IchorCnaMergedColumn.FileSWID: "s",
            },
            {
                "donor": "s",
                "group_id": "s",
                "library_design": "s",
                "pinery_lims_ids": "as",
                "project": "s",
                "reference": "s",
                "tissue_origin": "s",
                "tissue_type": "s",
            },
            {1: {"ichorcnamerged": [IchorCnaMergedColumn.FileSWID]}},
            {1: ("swid", IchorCnaColumn.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ichorcnamerged": {
                IchorCnaMergedColumn.Donor: single_input["donor"],
                IchorCnaMergedColumn.GroupID: single_input["group_id"],
                IchorCnaMergedColumn.LibraryDesign: single_input[
                    "library_design"
                ],
                IchorCnaMergedColumn.MergedPineryLimsID: single_input[
                    "pinery_lims_ids"
                ],
                IchorCnaMergedColumn.Project: single_input["project"],
                IchorCnaMergedColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
                IchorCnaMergedColumn.TissueOrigin: single_input[
                    "tissue_origin"
                ],
                IchorCnaMergedColumn.TissueType: single_input["tissue_type"],
                IchorCnaMergedColumn.FileSWID: single_input["swid"],
            }
        }
