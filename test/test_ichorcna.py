import qcetl.ichorcna
import test.cachechecker


def tests_ichorcna():
    test.cachechecker.check(
        qcetl.ichorcna.IchorCnaCache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcode": "AAATTT",
                "file": "test/files/ichorcna/TEST_0001.params.txt",
                "pinery_lims_id": "ID1",
                "swid": "SWIDD",
            }
        ],
        {"ichorcna": ("test/files/ichorcna/TEST_0001.csv")},
    )


def tests_ichorcna_merged():
    test.cachechecker.check(
        qcetl.ichorcna.IchorCnaMergedCache(),
        [
            {
                "donor": "TEST_0001",
                "group_id": "G",
                "library_design": "NN",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "tissue_origin": "nn",
                "tissue_type": "R",
                "file": "test/files/ichorcna/TEST_0001.params.txt",
                "swid": "SWIDD",
            }
        ],
        {"ichorcnamerged": ("test/files/ichorcna/TEST_0001.merged.csv")},
    )
