import qcetl.analysis_starfusion
import test.cachechecker


def tests_analysis_starfusion():
    test.cachechecker.check(
        qcetl.analysis_starfusion.AnalysisStarFusionCache(),
        [
            {
                "swid": "swid1",
                "file": "test/files/analysis_starfusion/star-fusion.fusion_predictions.tsv",
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
            "analysis_starfusion": "test/files/analysis_starfusion/analysis_starfusion.csv",
        },
    )


def tests_analysis_starfusion_empty():
    test.cachechecker.check(
        qcetl.analysis_starfusion.AnalysisStarFusionCache(),
        [
            {
                "swid": "swid1",
                "file": "test/files/analysis_starfusion/empty_star-fusion.fusion_predictions.tsv",
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
            "analysis_starfusion": "test/files/analysis_starfusion/analysis_starfusion_empty.csv",
        },
    )
