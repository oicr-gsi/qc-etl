import qcetl.ichorcna2
import test.cachechecker


def tests_ichorcna2():
    test.cachechecker.check(
        qcetl.ichorcna2.IchorCna2Cache(),
        [
            {
                "barcodes": "AAATTT",
                "lane": 1,
                "run": "181109_A00469_0016_AHGC37DMXX",
                "pinery_lims_id": "ID1",
                "file": "test/files/ichorcna2/TEST_0001.params.txt",
                "bamqc_file": "test/files/ichorcna2/TEST_0001.bamQC_results.json",
                "swid": "SWIDunique",
            }
        ],
        {
            "main": "test/files/ichorcna2/ichorcna2_main.csv",
            "solution": "test/files/ichorcna2/ichorcna2_solution.csv",
            "bamqc": "test/files/ichorcna2/ichorcna2_bamqc.csv",
        },
    )


def tests_ichorcna2_merged():
    test.cachechecker.check(
        qcetl.ichorcna2.IchorCna2MergedCache(),
        [
            {
                "donor": "TEST_0001",
                "group_id": "G",
                "library_design": "NN",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "tissue_origin": "nn",
                "tissue_type": "R",
                "file": "test/files/ichorcna2/TEST_0001.params.txt",
                "bamqc_file": "test/files/ichorcna2/TEST_0001-merged.bamQC_results.json",
                "swid": "SWIDD",
            }
        ],
        {
            "main": "test/files/ichorcna2/ichorcna2_merged_main.csv",
            "solution": "test/files/ichorcna2/ichorcna2_merged_solution.csv",
            "bamqc": "test/files/ichorcna2/ichorcna2_merged_bamqc.csv",
        },
    )
