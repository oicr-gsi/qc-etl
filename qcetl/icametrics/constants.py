__all__ = [
    "row_in_csv",
    "read_from_val",
    "optional_files",
    "sex_to_karyotype",
]

row_in_csv = {
    "wgs_coverage_metrics": [
        "Average alignment coverage over genome",
        "PCT of genome with coverage [  20x: inf)",
        "Uniformity of coverage (PCT > 0.2*mean) over genome",
    ],
    "ploidy_estimation_metrics": ["Ploidy estimation"],
    "mapping_metrics": [
        "Total input reads",
        "Mapped reads",
        "Number of unique reads (excl. duplicate marked reads)",
        "Number of duplicate marked reads",
        "Insert length: mean",
        "Insert length: median",
        "Estimated sample contamination",
    ],
    "gvcf_metrics": ["Ti/Tv ratio", "Percent Autosome Callability"],
    "cnv_metrics": [
        "Coverage uniformity",
        "Number of amplifications",
        "Number of deletions",
    ],
}

# DRAGEN only writes cnv_metrics when CNV calling is enabled. 
# Any other missing file rejects the record.
optional_files = {"cnv_metrics"}

# mapping_metrics rows are read from the percentage column (val_extra), except
# these, whose value is in the count/value column (val)
read_from_val = {
    "Total input reads",
    "Insert length: mean",
    "Insert length: median",
    "Estimated sample contamination",
}

# MISO Identity donor sex (DonorSex enum) mapped to the expected DRAGEN
# karyotype. OTHER, UNSPECIFIED and UNKNOWN have no expected karyotype, so
# no sex check is done for them.
sex_to_karyotype = {
    "male": "XY",
    "female": "XX",
}
