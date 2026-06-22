import test.cachechecker
import qcetl.bwamem


def tests_bwamem():
    test.cachechecker.check(
        qcetl.bwamem.BwaMemCache(),
        [
            {
                "barcode": "CGCTCTAT-TTGCAACG",
                "run": "200615_NB551051_0161_AHCG7MBGXF",
                "lane": 1,
                "path": "test/files/bwamem/TEST_0001_200615_NB551051_0161_AHCG7MBGXF_1_CGCTCTAT-TTGCAACG.log_",
                "swid": "SWID",
                "reference": "hg38",
            }
        ],
        {
            "cutadapt": "test/files/bwamem/TEST_0001_200615_NB551051_0161_AHCG7MBGXF_1_CGCTCTAT-TTGCAACG.csv"
        },
    )
