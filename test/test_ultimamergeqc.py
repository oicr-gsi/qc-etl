import qcetl.ultimamergeqc
import test.cachechecker


def test_ultimamergeqc():
    test.cachechecker.check(
        qcetl.ultimamergeqc.UltimaMergeQcCache(),
        [
            {
                "alignment_summary_file": "test/files/ultimamergeqc/LDI153108-ppm055-CAACTATCTGCAGAT.alignment_summary_metrics",
                "duplicate_metrics_file": "test/files/ultimamergeqc/LDI153108-ppm055-CAACTATCTGCAGAT.duplicate_metrics",
                "wgs_metrics_file": "test/files/ultimamergeqc/LDI153108-ppm055-CAACTATCTGCAGAT.wgs_metrics.txt",
                "donor": "TRNWLS_0071",
                "group_id": "TRNWLS_0071_Pl_T_PG_HMN1547603A00001",
                "pinery_lims_ids": ["9620_1_LDI153108"],
                "tissue_origin": "Pl",
                "tissue_type": "T",
                "swid": "1bc59158-8210-44c0-950c-a51346092824",
            }
        ],
        {"ultimamergeqc": "test/files/ultimamergeqc/ultimamergeqc_test.csv"},
    )
