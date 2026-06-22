import test.cachechecker
import qcetl.picard.hsmetrics_consensus_cruncher


def tests_consensus_cruncher_with_MIN_TARGET_COVERAGE():
    test.cachechecker.check(
        qcetl.picard.hsmetrics_consensus_cruncher.HsMetricsConsensusCruncherCache(),
        [
            {
                "donor": "TEST_0001",
                "file": "test/files/hsmetrics_consensus_cruncher/picard_hsmetrics_consensus_cruncher_TEST_0001.HS.txt",
                "group_id": "centauri",
                "library_design": "Ex",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "tissue_origin": "Bn",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "metrics": "test/files/hsmetrics_consensus_cruncher/picard_hsmetrics_consensus_cruncher_TEST_0001.HS.csv"
        },
    )


def tests_consensus_cruncher_without_MIN_TARGET_COVERAGE():
    test.cachechecker.check(
        qcetl.picard.hsmetrics_consensus_cruncher.HsMetricsConsensusCruncherCache(),
        [
            {
                "donor": "TEST_0002",
                "file": "test/files/hsmetrics_consensus_cruncher/picard_hsmetrics_consensus_cruncher_TEST_0002.HS.txt",
                "group_id": "centauri",
                "library_design": "Ex",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "tissue_origin": "Bn",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "metrics": "test/files/hsmetrics_consensus_cruncher/picard_hsmetrics_consensus_cruncher_TEST_0002.HS.csv"
        },
    )
