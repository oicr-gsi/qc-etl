import qcetl.analysis_sequenza
import test.cachechecker


def tests_analysis_sequenza():
    test.cachechecker.check(
        qcetl.analysis_sequenza.AnalysisSequenzaCache(),
        [
            {
                "swid": "swid1",
                "alt_soln_file": "test/files/analysis_sequenza/TEST_0001_alternative_solutions.json",
                "zip_file": "test/files/analysis_sequenza/tumour_results.zip",
                "donor": "TEST_0001",
                "group_id": "gid1",
                "library_design": "WG",
                "reference": "hg38",
                "tissue_origin": "Pa",
                "tissue_type": "P",
                "pinery_lims_ids": ["lims_id1", "lims_id2"],
                "genome_size": 3088269832,  # size of hg38.p12
                "fga_gamma": 500,
                "fga_threshold": 0.1,
            }
        ],
        {
            "analysis_sequenza_alternative_solutions": "test/files/analysis_sequenza/analysis_sequenza_alternative_solutions.csv",
            "analysis_sequenza_gamma_500_fga": "test/files/analysis_sequenza/analysis_sequenza_gamma_500_fga.csv",
        },
    )
