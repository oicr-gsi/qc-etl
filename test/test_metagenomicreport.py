import qcetl.metagenomicreport
import test.cachechecker


def tests_metagenomicreport():
    test.cachechecker.check(
        qcetl.metagenomicreport.MetagenomicReportCache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcodes": "CGTCTCATAT-TATAGTAGCT",
                "swid": "SWID",
                "file": "test/files/metagenomicreport/metagenomicReport.bracken",
            }
        ],
        {
            "metagenomicreport": "test/files/metagenomicreport/metagenomicReport.csv"
        },
    )
