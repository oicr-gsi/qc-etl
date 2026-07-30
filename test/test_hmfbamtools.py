import qcetl.hmfbamtools
import test.cachechecker


def tests_hmfbamtools():
    test.cachechecker.check(
        qcetl.hmfbamtools.HmfBamToolsCache(),
        [
            {
                "path": "test/files/hmfbamtools/COLO829TESTT.bam_metric.summary.tsv",
                "swid": "SWID",
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
            "hmfbamtools": "test/files/hmfbamtools/hmfbamtools_summary.csv",
            "coverage": "test/files/hmfbamtools/hmfbamtools_coverage.csv",
            "fragment_length": "test/files/hmfbamtools/hmfbamtools_fragment_length.csv",
            "flagstat": "test/files/hmfbamtools/hmfbamtools_flagstat.csv",
        },
    )
