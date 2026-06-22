import qcetl.rnaseqqc2
import test.cachechecker


def tests_rnaseqqc_2():
    test.cachechecker.check(
        qcetl.rnaseqqc2.RnaSeqQc2Cache(),
        [
            {
                "barcode": "ATTG",
                "lane": 3,
                "path": "test/files/rnaseqqc2/RNASeqQC.collatedMetrics.json",
                "pinery_lims_id": "ID",
                "run": "RUN",
                "swid": "SWID",
            }
        ],
        {
            3: {"rnaseqqc2": "test/files/rnaseqqc2/rnaseqqc2_v3.csv"},
        },
    )


def tests_rnaseqqc_2_merged():
    test.cachechecker.check(
        qcetl.rnaseqqc2.RnaSeqQc2MergedCache(),
        [
            {
                "donor": "DONOR",
                "group_id": "GROUP",
                "library_design": "MR",
                "pinery_lims_ids": ["id1", "id2"],
                "path": "test/files/rnaseqqc2/RNASeqQC.collatedMetrics.json",
                "project": "PROJ",
                "swid": "SWID",
                "tissue_origin": "NN",
                "tissue_type": "P",
            }
        ],
        {
            3: {
                "rnaseqqc2merged": "test/files/rnaseqqc2/rnaseqqc2-merged_v3.csv"
            },
        },
    )
