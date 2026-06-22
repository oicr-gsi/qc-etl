import qcetl.biomodalqc
import test.cachechecker


def test_biomodalqc_merged():
    test.cachechecker.check(
        qcetl.biomodalqc.BiomodalQcMergedCache(),
        [
            {
                "biomodalqc_csv": "test/files/biomodalqc/biomodalqcmerged_test.csv",
                "donor": "TEST_0001",
                "group_id": "NO",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "tissue_origin": "NN",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "biomodalqc_table": "test/files/biomodalqc/biomodalqcmerged_metrics.csv",
        },
    )


def test_biomodalqc():
    test.cachechecker.check(
        qcetl.biomodalqc.BiomodalQcCache(),
        [
            {
                "biomodalqc_csv": "test/files/biomodalqc/biomodalqc_test.csv",
                "donor": "TEST_0002",
                "barcodes": "NO",
                "lane": "1",
                "pinery_lims_id": "id1",
                "run": "NN",
                "swid": "SWID",
            }
        ],
        {
            "biomodalqc_table": "test/files/biomodalqc/biomodalqc_metrics.csv",
        },
    )
