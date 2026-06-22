import qcetl.bamqc4
import test.cachechecker


def tests_bamqc_4():
    test.cachechecker.check(
        qcetl.bamqc4.BamQc4Cache(),
        [
            {
                "path": "test/files/bamqc4/bamqc4.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 0],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {"bamqc4": "test/files/bamqc4/bamqc4.csv"},
    )


def tests_bamqc_4_merged():
    test.cachechecker.check(
        qcetl.bamqc4.BamQc4MergedCache(),
        [
            {
                "path": "test/files/bamqc4/TEST_0001.sorted.filter.deduped.realign.recal.bam.BamQC4.json",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "swid": "SWID",
                "workflow_version": [3, 0, 3],
                "donor": "TEST_0001",
                "group_id": "NO",
                "library_design": "WG",
                "tissue_origin": "Co",
                "tissue_type": "P",
            }
        ],
        {
            "bamqc4merged": "test/files/bamqc4/TEST_0001.sorted.filter.deduped.realign.recal.bam.BamQC4.csv"
        },
    )


def tests_bamqc_4_coverage_histogram():
    # GR-1243: Confirm that `coverage_histogram` is used if it is present
    test.cachechecker.check(
        qcetl.bamqc4.BamQc4Cache(),
        [
            {
                "path": "test/files/bamqc4/bamqc4_coverage_histogram.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 3],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {"bamqc4": "test/files/bamqc4/bamqc4_coverage_histogram.csv"},
    )
