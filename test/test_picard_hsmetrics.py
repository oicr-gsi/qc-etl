import test.cachechecker
import qcetl.picard.hsmetrics


def tests_hsmetrics():
    test.cachechecker.check(
        qcetl.picard.hsmetrics.HsMetricsCache(),
        [
            {
                "donor": "TEST_0001",
                "file": "test/files/hsmetrics/picard_hsmetrics_TEST_0001.HS.txt",
                "group_id": "centauri",
                "library_design": "Ex",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "tissue_origin": "Bn",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {"metrics": "test/files/hsmetrics/picard_hsmetrics_TEST_0001.HS.csv"},
    )
