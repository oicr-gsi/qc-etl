import qcetl.umiqc
import test.cachechecker


def test_umiqc():
    test.cachechecker.check(
        qcetl.umiqc.umiQcCache(),
        [
            {
                "umiCountsPerPosition": "test/files/umiqc/umiCountsPerPosition.tsv",
                "pre_dedup_bam_metrics": "test/files/umiqc/preDedup.bamQC_results.json",
                "post_dedup_bam_metrics": "test/files/umiqc/postDedup.bamQC_results.json",
                "extraction_metrics": "test/files/umiqc/output_extraction_metrics.json",
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcodes": "CGTCTCATAT-TATAGTAGCT",
                "swid": "SWID",
                "reference": "hg38",
            }
        ],
        {
            "umiqc_metrics": "test/files/umiqc/umiqc_metrics.csv",
            "pre_dedup_bam_metrics": "test/files/umiqc/pre_dedup_bam_metrics.csv",
            "post_dedup_bam_metrics": "test/files/umiqc/post_dedup_bam_metrics.csv",
            "family_size_distribution": "test/files/umiqc/family_size_distribution.csv",
            "extraction_metrics": "test/files/umiqc/extraction_metrics.csv",
        },
    )
