import qcetl.hmfrnaseqmetrics
import test.cachechecker


def tests_hmfrnaseqmetrics():
    test.cachechecker.check(
        qcetl.hmfrnaseqmetrics.HmfRnaSeqMetricsCache(),
        [
            {
                "path": "test/files/hmfrnaseqmetrics/COLO829TESTT.rna_seq_metrics.txt",
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
            "summary": "test/files/hmfrnaseqmetrics/hmfrnaseqmetrics_summary.csv",
        },
    )
