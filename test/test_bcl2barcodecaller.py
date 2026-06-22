import test.cachechecker
import qcetl.bcl2barcodecaller


def tests_bcl2barcode():
    test.cachechecker.check(
        qcetl.bcl2barcodecaller.Bcl2BarcodeCallerCache(),
        [
            {
                "run": "230317_M00753_0550_000000000-DJ2W7",
                "lane": 1,
                "pinery_lims_id": "LIMS_ID",
                "swid": "SWID",
                "known_barcodes": [
                    ["TEST_0001_01_LB01-01", "ACGGAACA-GTTCTCGT"],
                    ["TEST_0001_02_LB01-01", "ATCCAGAG-CGACGTTA"],
                    ["TEST_0003_01_LB01-01", "GACGTCAT-CCAGTTGA"],
                    ["TEST_0004_01_LB01-01", "CCGCTTAA-GTCATCGT"],
                    ["TEST_0005_01_LB01-01", "GACGAACT-CAATGCGA"],
                    ["TEST_0006_01_LB01-01", "TCCACGTT-GGTTGAAC"],
                    ["TEST_0007_01_LB01-01", "AACCAGAG-CTTCGGTT"],
                    ["TEST_0008_01_LB01-01", "GTCAGTCA-CGGCATTA"],
                    ["TEST_0009_01_LB01-01", "CTTACAGC-TGGTGAAG"],
                    ["TEST_0010_01_LB01-01", "TACCTGCA-GGACATCA"],
                    ["TEST_0011_01_LB01-01", "AGACGCTA-GGTGTACA"],
                    ["TEST_0012_01_LB01-01", "CAACACAG-GATAGCCA"],
                    ["TEST_0013_01_LB01-01", "GTACCACA-CCACAACA"],
                    ["TEST_0014_01_LB01-01", "CGAATACG-TTACCGAC"],
                    ["TEST_0015_Ly_R_PE_404_MG", "GTCCTTGA-TCGTCTGA"],
                    ["TEST_0016_Ly_R_PE_416_MG", "CCTTCCAT-CACGCAAT"],
                    ["TEST_0017_nn_R_PE_3201_WT", "ATTACTCG-TAATCTTA"],
                    ["TEST_0018_nn_R_PE_34000_WT", "GAATTCGT-GTACTGAC"],
                    ["TEST_0019_nn_R_PE_34200_WT", "ATTCAGAA-GTACTGAC"],
                    ["TEST_0020_nn_n_PE_176_PG", "ACTGAGGT-GCGTCATT"],
                    ["TEST_0021_Pb_T_PE_343_PG", "GAGCAGTA-ACAGCTCA"],
                    ["TEST_0021_Pb_T_PE_346_PG", "GTTGTTCG-GAAGTTGG"],
                    ["TEST_0022_01_LB02-01", "TCCGGAGA-TAATCTTA"],
                    ["TEST_0023_01_LB02-01", "CGCTCATT-TAATCTTA"],
                    ["TEST_0024_01_LB02-01", "GAGATTCC-TAATCTTA"],
                    ["TEST_0025_02_LB02-01", "ATTCAGAA-TAATCTTA"],
                    ["TEST_0026_02_LB02-01", "GAATTCGT-TAATCTTA"],
                    ["TEST_0027_02_LB02-01", "CTGAAGCT-TAATCTTA"],
                    ["TEST_0028_02_LB02-01", "TAATGCGC-TAATCTTA"],
                    ["TEST_0029_Ct_T_nn_1-11_LB02-01", "ATGACGTC-GAAGGAAG"],
                    ["TEST_0029_Ct_T_nn_1-11_LB03-01", "CGCTCTAT-CGTTGCAA"],
                    ["TEST_0030_Lv_M_PE_310_WT", "CGGCTATG-TAATCTTA"],
                    ["TEST_0030_Lv_M_PE_562_WG", "ACGACTTG-TCGCTGTT"],
                    ["TEST_0030_Ly_R_PE_476_WG", "CCGTAAGA-TGGACTCT"],
                    ["TEST_0031_Lv_M_PE_549_WG", "CGTTGCAA-CGCTCTAT"],
                    ["TEST_0031_Ly_R_PE_468_WG", "GAAGGAAG-ATGACGTC"],
                    ["TEST_0032_01_LB03-01", "TCCGCGAA-TAATCTTA"],
                    ["TEST_0033_01_LB03-01", "TCTCGCGC-TAATCTTA"],
                    ["TEST_0034_Fa_P_PE_334_WG", "TGGACTCT-CCGTAAGA"],
                    ["TEST_0034_Ly_R_PE_361_WG", "ACTAGGAG-GTGCCATA"],
                    ["TEST_0034_Pl_T_PE_398_WG", "CAGTCCAA-GATTACCG"],
                    ["TEST_0035_Ly_R_PE_341_WG", "TATCGGTC-ATCCGGTA"],
                    ["TEST_0035_Ov_P_PE_318_WG", "GCTATCCT-CACCTGTT"],
                    ["TEST_0035_Pl_T_PE_438_WG", "CGTGTGTA-TTCGTTGG"],
                    ["TEST_0036_Pl_T_PE_398_WG", "CACCTGTT-GCTATCCT"],
                    ["TEST_0037_Ly_R_PE_401_WG", "GTGCCATA-ACTAGGAG"],
                    ["TEST_0037_Ov_P_PE_346_WG", "GATTACCG-CAGTCCAA"],
                    ["TEST_0038_Pl_T_PE_408_WG", "TACGCTAC-ATCACACG"],
                ],
                "path": "test/files/bcl2barcodecaller/bcl2barcodecaller.counts.gz",
            }
        ],
        {
            "known": "test/files/bcl2barcodecaller/bcl2barcodecaller_known.csv",
            "summary": "test/files/bcl2barcodecaller/bcl2barcodecaller_summary.csv",
            "unknown": "test/files/bcl2barcodecaller/bcl2barcodecaller_unknown.csv",
        },
    )


def tests_bcl2barcode_empty():
    test.cachechecker.check(
        qcetl.bcl2barcodecaller.Bcl2BarcodeCallerCache(),
        [
            {
                "run": "230317_M00753_0550_000000000-DJ2W7",
                "lane": 1,
                "pinery_lims_id": "LIMS_ID",
                "swid": "SWID",
                # No called barcodes, so this can be empty
                "known_barcodes": [],
                "path": "test/files/bcl2barcodecaller/bcl2barcodecaller_empty.counts.gz",
            }
        ],
        {
            "known": "test/files/bcl2barcodecaller/bcl2barcodecaller_empty_known.csv",
            "summary": "test/files/bcl2barcodecaller/bcl2barcodecaller_empty_summary.csv",
            "unknown": "test/files/bcl2barcodecaller/bcl2barcodecaller_empty_unknown.csv",
        },
    )
