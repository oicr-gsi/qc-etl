import qcetl.analysis_mrd
import test.cachechecker


def test_analysis_mrd():
    test.cachechecker.check(
        qcetl.analysis_mrd.AnalysisMrdCache(),
        [
            {
                "mrd_txt_file": "test/files/analysis_mrd/mrd_report.txt",
                "donor": "Test_01",
                "group_id": "gid1",
                "swid": "swid1",
                "tissue_type": "P",
                "tissue_origin": "NN",
                "pinery_lims_ids": ["id1", "id2"],
                "library_design": "WG",
                "reference": "hg38",
            }
        ],
        {"analysis_mrd": "test/files/analysis_mrd/expected_analysis_mrd.csv"},
    )
