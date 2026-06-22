import qcetl.bamqclite
import test.cachechecker


def tests_bamqc_lite():
    test.cachechecker.check(
        qcetl.bamqclite.BamQcLiteCache(),
        [
            {
                "path": "test/files/bamqclite/TEST_0001_lane_level.bamQClite_results.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 0],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {
            "bamqclite": "test/files/bamqclite/TEST_0001_lane_level.bamQClite_results.csv"
        },
    )


def tests_bamqc_lite_merged():
    test.cachechecker.check(
        qcetl.bamqclite.BamQcLiteMergedCache(),
        [
            {
                "path": "test/files/bamqclite/bamqclite_callready_TEST_0001.json",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "swid": "SWID",
                "workflow_version": [3, 0, 3],
                "donor": "TEST_0001",
                "group_id": "NO",
                "library_design": "WG",
                "tissue_origin": "Co",
                "tissue_type": "P",
            }
        ],
        {
            "bamqclitemerged": "test/files/bamqclite/bamqclite_callready_TEST_0001.csv"
        },
    )


def tests_bamqc_lite_coverage_histogram():
    # GR-1243: Confirm that `coverage_histogram` is used if it is present
    test.cachechecker.check(
        qcetl.bamqclite.BamQcLiteCache(),
        [
            {
                "path": "test/files/bamqclite/TEST_0001_lane_level.bamQClite_results.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 3],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {
            "bamqclite": "test/files/bamqclite/bamqclite_TEST_0001_coverage_histogram.csv"
        },
    )


def tests_bamqc_lite_empty():
    test.cachechecker.check(
        qcetl.bamqclite.BamQcLiteCache(),
        [
            {
                "path": "test/files/bamqclite/empty_lane_level.bamQClite_results.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [5, 3, 5],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {"bamqclite": "test/files/bamqclite/empty.bamQClite_results.csv"},
    )
