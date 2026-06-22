import qcetl.sequenza
import test.cachechecker


def test_sequenza():
    test.cachechecker.check(
        qcetl.sequenza.SequenzaCache(),
        [
            {
                "input": "test/files/sequenza/sequenza_test_input.zip",
                "swid": "SWID",
                "donor": "DONOR",
                "group_id": "GROUP",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "tissue_origin": "NN",
                "tissue_type": "P",
            }
        ],
        {"sequenza": "test/files/sequenza/sequenza.csv"},
    )


def test_sequenza_empty():
    test.cachechecker.check(
        qcetl.sequenza.SequenzaCache(),
        [
            {
                "input": "test/files/sequenza/sequenza_test_empty_input.zip",
                "swid": "SWID",
                "donor": "DONOR",
                "group_id": "GROUP",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "tissue_origin": "NN",
                "tissue_type": "P",
            }
        ],
        {"sequenza": "test/files/sequenza/sequenza_empty.csv"},
    )
