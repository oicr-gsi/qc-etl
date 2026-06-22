import test.cachechecker
import qcetl.bcl2barcode


def tests_bcl2barcode():
    test.cachechecker.check(
        qcetl.bcl2barcode.Bcl2BarcodeCache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "path": "test/files/bcl2barcode/bcl2barcode.counts.gz",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
            }
        ],
        {
            "bcl2barcode": "test/files/bcl2barcode/bcl2barcode.csv",
            "run_summary": "test/files/bcl2barcode/bcl2barcode_run_summary.csv",
        },
    )
