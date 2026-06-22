import qcetl.bedtools
import test.cachechecker


def tests_bedtools_sarscov2():
    test.cachechecker.check(
        qcetl.bedtools.BedToolsSarsCov2Cache(),
        [
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "barcodes": "CGTCTCATAT-TATAGTAGCT",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "file_coverage_hist": "test/files/bedtools/bedtools_coverage_hist_SRR11059944.cvghist.txt",
                "file_genomecov": "test/files/bedtools/bedtools_genomecov_SRR11059944.genomecvghist.txt",
                "file_genomecov_per_base": "test/files/bedtools/bedtools_genomecov_per_base_SRR11059944.genome.cvgperbase.txt",
            }
        ],
        {
            "genomecov_coverage_percentile": "test/files/bedtools/bedtools_genomecov_coverage_percentile_SRR11059944.genomecvghist.csv",
            "genomecov_calculations": "test/files/bedtools/bedtools_genomecov_calculations_SRR11059944.genomecvghist.csv",
        },
    )
