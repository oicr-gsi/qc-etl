import qcetl.analysis_delly
import test.cachechecker


def tests_analysis_delly():
    test.cachechecker.check(
        qcetl.analysis_delly.AnalysisDellyCache(),
        [
            {
                "swid": "swid1",
                "file": "test/files/analysis_delly/TEST_0001_somatic.somatic_filtered.delly.merged.vcf.gz",
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
            "analysis_delly": "test/files/analysis_delly/analysis_delly.csv",
        },
    )


def tests_analysis_delly_empty():
    test.cachechecker.check(
        qcetl.analysis_delly.AnalysisDellyCache(),
        [
            {
                "swid": "swid1",
                "file": "test/files/analysis_delly/TEST_0002_somatic.somatic_filtered.delly.merged.vcf.gz",
                "donor": "TEST_0002",
                "group_id": "gid1",
                "library_design": "WG",
                "reference": "hg38",
                "tissue_origin": "Pa",
                "tissue_type": "P",
                "pinery_lims_ids": ["lims_id3", "lims_id4"],
            }
        ],
        {
            "analysis_delly": "test/files/analysis_delly/analysis_delly_empty.csv",
        },
    )
