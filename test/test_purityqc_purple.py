import qcetl.purityqc_purple
import test.cachechecker


def test_purityqc_purple():
    test.cachechecker.check(
        qcetl.purityqc_purple.PurityQcPurpleCache(),
        [
            {
                "purple_purity_input": "test/files/purityqc_purple/purple_purity_test.tsv",
                "donor": "DONOR",
                "group_id": "GROUP",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "tissue_origin": "NN",
                "tissue_type": "P",
                "swid": "SWID",
            }
        ],
        {
            "purple_purity_ploidy_table": "test/files/purityqc_purple/purple_purity_ploidy.csv",
        },
    )
