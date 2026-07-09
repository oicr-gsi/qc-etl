__all__ = ["ICA_DIR", "row_in_csv"]


ICA_DIR = "/mnt/seqdata/misoruns".replace("seqdata", "clinical/rawsequencedata")

row_in_csv = {
    "wgs_coverage_metrics": [
        "Average alignment coverage over genome",
        "PCT of genome with coverage [  20x: inf)",
        "Uniformity of coverage (PCT > 0.2*mean) over genome",
    ],
    "ploidy_estimation_metrics": ["Ploidy estimation"],
    "mapping_metrics": [
        "Mapped reads",
        "Number of unique reads (excl. duplicate marked reads)",
        "Insert length: median",
    ],
    "gvcf_metrics": ["Ti/Tv ratio", "Percent Autosome Callability"],
    "cnv_metrics": [
        "Coverage uniformity",
        "Number of amplifications",
        "Number of deletions",
    ],
}
