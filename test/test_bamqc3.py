import qcetl.bamqc3
import test.cachechecker


def tests_bamqc_3():
    test.cachechecker.check(
        qcetl.bamqc3.BamQc3Cache(),
        [{"path": "test/files/bamqc3/bamqc3.json", "swid": "SWID"}],
        {
            "bamqc3": "test/files/bamqc3/bamqc3.csv",
            "histogram": "test/files/bamqc3/bamqc3_hist.csv",
        },
    )


def tests_bamqc_3_merged():
    test.cachechecker.check(
        qcetl.bamqc3.BamQc3MergedCache(),
        [
            {
                "path": "test/files/bamqc3/TEST_0001.sorted.filter.deduped.realign.recal.bam.BamQC3.json",
                "project": "PROJ",
                "swid": "SWID",
            }
        ],
        {
            "bamqc3merged": "test/files/bamqc3/TEST_0001.sorted.filter.deduped.realign.recal.bam.BamQC3.csv",
            "histogram": "test/files/bamqc3/TEST_0001.sorted.filter.deduped.realign.recal.bam.BamQC3_hist.csv",
        },
    )
