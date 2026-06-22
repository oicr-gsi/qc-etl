import qcetl.samtools
import test.cachechecker


def tests_samtools_stats_sarscov2():
    test.cachechecker.check(
        qcetl.samtools.SamtoolsStatsCov2Cache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcodes": "CGTCTCATAT-TATAGTAGCT",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "file_human": "test/files/samtools/samtools_stats_SRR11059944.host.mapped.samstats.txt",
                "file_depleted": "test/files/samtools/samtools_stats_SRR11059944.samstats.txt",
            }
        ],
        {
            "human": "test/files/samtools/samtools_stats_SRR11059944.host.mapped.samstats.csv",
            "depleted": "test/files/samtools/samtools_stats_SRR11059944.samstats.csv",
        },
    )
