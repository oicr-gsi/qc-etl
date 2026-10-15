import qcetl.hmfisofox
import test.cachechecker


def tests_hmfisofox():
    test.cachechecker.check(
        qcetl.hmfisofox.HmfIsofoxCache(),
        [
            {
                "path": "test/files/hmfisofox/COLO829TESTR-RNA.isf.summary.csv",
                "swid": "SWID_RNA",
                "project": "COLO829TEST",
                "pinery_lims_ids": ["ID3"],
                "donor": "COLO829TESTT",
                "group_id": "NO",
                "library_design": "WT",
                "tissue_origin": "Sk",
                "tissue_type": "M",
                "reference": "hg38",
                "workflow_version": [6, 2, 0],
            }
        ],
        {
            "summary": "test/files/hmfisofox/hmfisofox_summary.csv",
        },
    )
