import test.cachechecker
import qcetl.picard.umiconsensus


def tests_umiconsensus_with_MIN_TARGET_COVERAGE():
    test.cachechecker.check(
        qcetl.picard.umiconsensus.HsMetricsUmiConsensusCache(),
        [
            {
                "donor": "TEST_0001",
                "file": "test/files/umiconsensus/picard_hsmetrics_consensus_cruncher_TEST_0001.HS.txt",
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
            "metrics": "test/files/umiconsensus/picard_hsmetrics_consensus_cruncher_TEST_0001.HS.csv"
        },
    )


def tests_umiconsensus_cruncher_without_MIN_TARGET_COVERAGE():
    test.cachechecker.check(
        qcetl.picard.umiconsensus.HsMetricsUmiConsensusCache(),
        [
            {
                "donor": "TEST_0002",
                "file": "test/files/umiconsensus/picard_hsmetrics_consensus_cruncher_TEST_0002.HS.txt",
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
            "metrics": "test/files/umiconsensus/picard_hsmetrics_consensus_cruncher_TEST_0002.HS.csv"
        },
    )
