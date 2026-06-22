import qcetl.fastqc
import test.cachechecker


def tests_HGC37DMXX_1():
    test.cachechecker.check(
        qcetl.fastqc.FastQcCache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "read": 1,
                "lane": 1,
                "barcode": "CGTCTCATAT-TATAGTAGCT",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "file": "test/files/fastqc/SWID_12909889_GLCS_0022_Br_P_PE_288_EX_NFBT_08Nov2018-3_181109_A00469_0016_AHGC37DMXX_CGTCTCATAT-TATAGTAGCT_L001_R1_001_fastqc.zip",
            }
        ],
        {
            "fastqc": "test/files/fastqc/SWID_12909889_GLCS_0022_Br_P_PE_288_EX_NFBT_08Nov2018-3_181109_A00469_0016_AHGC37DMXX_CGTCTCATAT-TATAGTAGCT_L001_R1_001_fastqc.csv"
        },
    )
