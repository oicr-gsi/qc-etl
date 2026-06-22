import qcetl.analysis_rsem
import test.cachechecker


def tests_analysis_rsem():
    test.cachechecker.check(
        qcetl.analysis_rsem.AnalysisRSEMCache(),
        [
            {
                "swid": "swid1",
                "file": "test/files/analysis_rsem/TEST_0001.genes.results",
                "donor": "TEST_0001",
                "group_id": "gid1",
                "library_design": "WG",
                "reference": "hg38",
                "tissue_origin": "Pa",
                "tissue_type": "P",
                "pinery_lims_ids": ["lims_id1", "lims_id2"],
            }
        ],
        {
            "analysis_rsem": "test/files/analysis_rsem/analysis_rsem.csv",
        },
    )
