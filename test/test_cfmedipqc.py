import test.cachechecker
import qcetl.cfmedipqc


def tests_cfmedip():
    test.cachechecker.check(
        qcetl.cfmedipqc.CfMeDipQcCache(),
        [
            {
                "barcode": "ATGCATGC",
                "file": "test/files/cfmedipqc/medip.qc_metrics.json",
                "file_insert_stats": "test/files/cfmedipqc/medip.insert_size_metrics",
                "lane": 1,
                "pinery_lims_id": "ID1",
                "reference": "hg19",
                "run": "181109_A00469_0016_AHGC37DMXX",
                "swid": "SWID",
            }
        ],
        {
            "cfmedipqc": "test/files/cfmedipqc/medip.qc_metrics_4.csv",
            "insert_metrics": "test/files/cfmedipqc/medip.insert_size_metrics_3.csv",
        },
    )


def test_cfmedip_scientific_notation():
    test.cachechecker.check(
        qcetl.cfmedipqc.CfMeDipQcCache(),
        [
            {
                "barcode": "ATGCATGC",
                "file": "test/files/cfmedipqc/medip.qc_metrics.scientific_notation.json",
                "file_insert_stats": "test/files/cfmedipqc/medip.scientific_notation.insert_size_metrics",
                "lane": 1,
                "pinery_lims_id": "ID1",
                "reference": "hg19",
                "run": "181109_A00469_0016_AHGC37DMXX",
                "swid": "SWID",
            }
        ],
        {
            "cfmedipqc": "test/files/cfmedipqc/medip.scientific_notation.qc_metrics.csv",
            "insert_metrics": "test/files/cfmedipqc/medip.scientific_notation.insert_size_metrics.csv",
        },
    )
