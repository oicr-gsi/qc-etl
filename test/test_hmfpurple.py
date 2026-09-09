import qcetl.hmfpurple
import test.cachechecker


def tests_hmfpurple():
    test.cachechecker.check(
        qcetl.hmfpurple.HmfPurpleCache(),
        [
            {
                "path": "test/files/hmfpurple/COLO829TESTT.purple.purity.tsv",
                "swid": "SWID_T",
                "project": "COLO829TEST",
                "pinery_lims_ids": ["ID1", "ID2"],
                "donor": "COLO829TESTT",
                "group_id": "NO",
                "library_design": "WG",
                "tissue_origin": "Sk",
                "tissue_type": "M",
                "reference": "hg38",
                "workflow_version": [6, 2, 0],
            }
        ],
        {
            "purity": "test/files/hmfpurple/hmfpurple_purity.csv",
        },
    )
