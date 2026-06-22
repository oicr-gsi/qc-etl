import qcetl.analysis_mutect2
import test.cachechecker


def tests_analysis_mutect2_vcf():
    test.cachechecker.check(
        qcetl.analysis_mutect2.AnalysisMutect2Cache(),
        [
            {
                "swid": "swid1",
                "vcf": "test/files/analysis_mutect2/TEST_0001.mutect2.filtered.vep.vcf.gz",
                "tsv": None,
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
            "analysis_mutect2": "test/files/analysis_mutect2/analysis_mutect2_vcf.csv",
        },
    )


def tests_analysis_mutect2_tsv():
    test.cachechecker.check(
        qcetl.analysis_mutect2.AnalysisMutect2Cache(),
        [
            {
                "swid": "swid1",
                "vcf": None,
                "tsv": "test/files/analysis_mutect2/Test.mutect2.tumor_only.filtered.metrics.tsv",
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
            "analysis_mutect2": "test/files/analysis_mutect2/analysis_mutect2_tsv.csv",
        },
    )


def tests_analysis_mutect2_empty():
    test.cachechecker.check(
        qcetl.analysis_mutect2.AnalysisMutect2Cache(),
        [
            {
                "swid": "swid1",
                "vcf": "test/files/analysis_mutect2/TEST_0002.filter.deduped.realigned.recalibrated.mutect2.filtered.vcf.gz",
                "tsv": None,
                "donor": "TEST_0002",
                "group_id": "gid1",
                "library_design": "WG",
                "reference": "hg38",
                "tissue_origin": "Pa",
                "tissue_type": "P",
                "pinery_lims_ids": ["lims_id1", "lims_id2"],
            }
        ],
        {
            "analysis_mutect2": "test/files/analysis_mutect2/analysis_mutect2_empty.csv",
        },
    )
