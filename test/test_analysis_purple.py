import qcetl.analysis_purple
import test.cachechecker


def test_analysis_purple():
    test.cachechecker.check(
        qcetl.analysis_purple.AnalysisPurpleCache(),
        [
            {
                "purity_tsv_file": "test/files/analysis_purple/purple_purity_test.tsv",
                "cnv_somatic_file": "test/files/analysis_purple/analysis_purple_cnv_somatic_test.tsv",
                "qc_file": "test/files/analysis_purple/analysis_purple.qc",
                "donor": "DONOR",
                "group_id": "GROUP",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "reference": "hg38",
                "tissue_origin": "NN",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "analysis_purple": "test/files/analysis_purple/analysis_purple.csv",
        },
    )
