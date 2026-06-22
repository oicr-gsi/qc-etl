import qcetl.emseqqc
import test.cachechecker


def tests_emseqqc():
    test.cachechecker.check(
        qcetl.emseqqc.EmSeqQcCache(),
        [
            {
                "barcode": "ATCG",
                "file_bamqc": "test/files/emseqqc/emseq_bamqc.json",
                "file_lambda_stats": "test/files/emseqqc/emseq_lambda.stats",
                "file_puc19_stats": "test/files/emseqqc/emseq_puc19.stats",
                "file_methyldackel": "test/files/emseqqc/emseq_methyldackel.bedGraph.gz",
                "lane": 2,
                "pinery_lims_id": "LDI1234",
                "run": "NovaSeqX++",
                "swid": "SWID",
            }
        ],
        {
            "bamqc": "test/files/emseqqc/emseq_bamqc.csv",
            "lambda_stats": "test/files/emseqqc/emseq_lambda.csv",
            "puc19_stats": "test/files/emseqqc/emseq_puc10.csv",
            "methylation": "test/files/emseqqc/emseq_methylation.csv",
        },
    )
