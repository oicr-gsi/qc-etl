import qcetl.purityqc_sequenza
import test.cachechecker


def test_purityqc():
    test.cachechecker.check(
        qcetl.purityqc_sequenza.PurityQcSequenzaCache(),
        [
            {
                "sequenza_input": "test/files/purityqc_sequenza/sequenza_test_input.zip",
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
            "sequenza_purity_ploidy_table": "test/files/purityqc_sequenza/purity_ploidy_table.csv"
        },
    )
