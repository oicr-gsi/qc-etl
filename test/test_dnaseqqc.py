import qcetl.dnaseqqc
import test.cachechecker


def tests_dnaseqqc():
    test.cachechecker.check(
        qcetl.dnaseqqc.DnaSeqQcCache(),
        [
            {
                "path": "test/files/dnaseqqc/dnaseqqc_TEST_0001_Pb_R_PE_557_WG_Matched_blood_210601_A00469_0180_AH77VJDSX2_3_CGCTGCTC-GATCTGCC.bamQC_results.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 5],
                "barcode": "CGCTGCTC-GATCTGCC",
                "run": "210601_A00469_0180_AH77VJDSX2",
                "lane": 3,
            }
        ],
        {"dnaseqqc": "test/files/dnaseqqc/dnaseqqc.csv"},
    )
