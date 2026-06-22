import qcetl.bamqc4
from qcetl.column import DnaSeqQCColumn


class DnaSeqQcCache(qcetl.bamqc4.BaseBamQc4Cache):
    def __init__(self):
        super().__init__(
            "dnaseqqc",
            DnaSeqQCColumn,
            {
                DnaSeqQCColumn.Barcodes: "s",
                DnaSeqQCColumn.FileSWID: "s",
                DnaSeqQCColumn.Lane: "i",
                DnaSeqQCColumn.PineryLimsID: "s",
                DnaSeqQCColumn.Run: "s",
                DnaSeqQCColumn.Reference: "s",
            },
            {DnaSeqQCColumn.Instrument: "s", DnaSeqQCColumn.Library: "qs"},
            {"pinery_lims_id": "s", "run": "s", "lane": "i", "barcode": "s"},
            {5: {"dnaseqqc": [DnaSeqQCColumn.FileSWID]}},
            {5: ("swid", DnaSeqQCColumn.FileSWID)},
        )

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            self.name: {
                DnaSeqQCColumn.FileSWID: single_input["swid"],
                DnaSeqQCColumn.PineryLimsID: single_input["pinery_lims_id"],
                DnaSeqQCColumn.Run: single_input["run"],
                DnaSeqQCColumn.Lane: single_input["lane"],
                DnaSeqQCColumn.Barcodes: single_input["barcode"],
                DnaSeqQCColumn.Reference: single_input.get(
                    "reference", "Unknown"
                ),
            }
        }
