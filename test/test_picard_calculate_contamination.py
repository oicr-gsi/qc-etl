import test.cachechecker
import qcetl.picard.calculatecontamination


def tests_picard_calculatecontamination_call_ready():
    test.cachechecker.check(
        qcetl.picard.calculatecontamination.CalculateContaminationCallReady(),
        [
            {
                "donor": "TEST_0001",
                "file": "test/files/calculatecontamination/picard_calculate_contamination.table",
                "group_id": "centauri",
                "library_design": "Ex",
                "pinery_lims_ids": ["ID1", "ID2"],
                "tissue_origin": "Bn",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "calculatecontamination": "test/files/calculatecontamination/picard_calculate_contamination.csv"
        },
    )


def tests_picard_calculate_contamination_lane_level():
    test.cachechecker.check(
        qcetl.picard.calculatecontamination.CalculateContaminationLaneLevel(),
        [
            {
                "donor": "TEST_0002",
                "barcode": "GTTTA",
                "lane": 2,
                "run": "vanilla",
                "pinery_lims_id": "ID21",
                "reference": "hg19",
                "file": "test/files/calculatecontamination/picard_calculate_contamination_lane_level.table",
                "swid": "SWIDwild",
            }
        ],
        {
            "calculatecontamination": "test/files/calculatecontamination/picard_calculate_contamination_lane_level.csv"
        },
    )
