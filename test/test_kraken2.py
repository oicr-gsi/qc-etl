import qcetl.kraken2
import test.cachechecker


def tests_kraken2():
    test.cachechecker.check(
        qcetl.kraken2.Kraken2Cache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcodes": "CGTCTCATAT-TATAGTAGCT",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "reference": "hg38",
                "file": "test/files/kraken2/kraken2_SRR11059945.kreport2",
            }
        ],
        {"kraken2": "test/files/kraken2/kraken2_SRR11059945.csv"},
    )
