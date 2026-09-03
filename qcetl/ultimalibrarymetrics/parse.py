import pandas

from qcetl.column import UltimaLibraryMetricsColumn as Column

_COLUMNS = [
    Column.GeoGroupID,
    Column.Barcode,
    Column.MeanCoverage,
    Column.PercentDuplicates,
    Column.F80,
    Column.F90,
    Column.F95,
    Column.PercentGte1x,
    Column.PercentGte10x,
    Column.PercentGte20x,
    Column.PercentGte50x,
    Column.PercentGte100x,
    Column.PercentGte500x,
    Column.PercentGte1000x,
    Column.F80At30x,
    Column.F90At30x,
    Column.F95At30x,
    Column.MAPQGte1,
    Column.MAPQGte10,
    Column.MAPQGte20,
    Column.MAPQGte30,
    Column.MedianCoverage,
    Column.IndelRate,
    Column.MeanQuality,
    Column.PercentChimeras,
    Column.MismatchRate,
    Column.PercentPFAligned,
    Column.FailedQCReads,
    Column.MeanReadLength,
    Column.PercentPFQ20Bases,
    Column.PercentPFQ30Bases,
    Column.PFBarcodeReads,
    Column.PercentPFHQAligned,
    Column.MedianReadLength,
    Column.PercentFailedQCReads,
    Column.PercentPFReadsAligned,
    Column.PercentSoftclippedBases,
    Column.MeanAlignedReadLength,
    Column.PercentOpticalDuplicatesRingOverlap,
    Column.PercentOpticalDuplicatesFalseDetection,
    Column.PctPFQ20Flows,
    Column.PctPFQ30Flows,
    Column.PctPFQ20Snvq,
    Column.PctPFQ30Snvq,
    Column.PctPFQ40Snvq,
    Column.PpmseqPctReadEndUnreached,
    Column.PpmseqMixedReadMeanCoverage,
    Column.PpmseqPctFailedAdapterDimers,
    Column.PpmseqPctMixedBothTagsWhereEndreached,
]


def _optional_float(qtable, key):
    """
    Some qtable fields are only present for certain runs. Missing fields
    are stored as null rather than failing the parse.
    """
    value = qtable.get(key)
    return None if value is None else float(value)


def parse_records(data, geo_group_id):
    """
    Turn the Nexus allbarcodes/metrics response into a DataFrame, keeping
    only the entry whose qtable "Sample" field matches the requested
    geo_group_id.

    Args:
        data: List of {"barcode": ..., "qtable": {...}} dicts, as returned
            by the Nexus API.
        geo_group_id: The geo group ID to match against each entry's
            qtable "Sample" field.

    Returns:

    """
    rows = []
    for entry in data:
        qtable = entry.get("qtable", {})
        entry_geo_group_id = (qtable.get("Sample") or "").strip()
        if not entry_geo_group_id or entry_geo_group_id != geo_group_id:
            continue
        rows.append(
            {
                Column.GeoGroupID: geo_group_id,
                Column.Barcode: entry.get("barcode"),
                Column.MeanCoverage: float(qtable.get("Mean_cvg")),
                Column.PercentDuplicates: float(qtable.get("% duplicates")),
                Column.F80: float(qtable.get("F80")),
                Column.F90: float(qtable.get("F90")),
                Column.F95: float(qtable.get("F95")),
                Column.PercentGte1x: float(qtable.get("%>=1x")),
                Column.PercentGte10x: float(qtable.get("%>=10x")),
                Column.PercentGte20x: float(qtable.get("%>=20x")),
                Column.PercentGte50x: float(qtable.get("%>=50x")),
                Column.PercentGte100x: float(qtable.get("%>=100x")),
                Column.PercentGte500x: float(qtable.get("%>=500x")),
                Column.PercentGte1000x: float(qtable.get("%>=1000x")),
                Column.F80At30x: float(qtable.get("F80@30x")),
                Column.F90At30x: float(qtable.get("F90@30x")),
                Column.F95At30x: float(qtable.get("F95@30x")),
                Column.MAPQGte1: float(qtable.get("MAPQ >= 1")),
                Column.MAPQGte10: float(qtable.get("MAPQ >= 10")),
                Column.MAPQGte20: float(qtable.get("MAPQ >= 20")),
                Column.MAPQGte30: float(qtable.get("MAPQ >= 30")),
                Column.MedianCoverage: float(qtable.get("median_cvg")),
                Column.IndelRate: float(qtable.get("Indel_Rate")),
                Column.MeanQuality: float(qtable.get("Mean_quality")),
                Column.PercentChimeras: float(qtable.get("PCT_Chimeras")),
                Column.MismatchRate: float(qtable.get("Mismatch_Rate")),
                Column.PercentPFAligned: float(qtable.get("PCT_PF_aligned")),
                Column.FailedQCReads: float(qtable.get("Failed_QC_reads")),
                Column.MeanReadLength: float(qtable.get("Mean_Read_Length")),
                Column.PercentPFQ20Bases: float(qtable.get("PCT_PF_Q20_bases")),
                Column.PercentPFQ30Bases: float(qtable.get("PCT_PF_Q30_bases")),
                Column.PFBarcodeReads: float(qtable.get("PF_Barcode_reads")),
                Column.PercentPFHQAligned: float(
                    qtable.get("PCT_PF_HQ_aligned")
                ),
                Column.MedianReadLength: float(
                    qtable.get("Median_Read_Length")
                ),
                Column.PercentFailedQCReads: float(
                    qtable.get("PCT_Failed_QC_reads")
                ),
                Column.PercentPFReadsAligned: float(
                    qtable.get("PCT_PF_Reads_aligned")
                ),
                Column.PercentSoftclippedBases: float(
                    qtable.get("PCT_SOFTCLIPPED_bases")
                ),
                Column.MeanAlignedReadLength: float(
                    qtable.get("Mean_Aligned_Read_Length")
                ),
                Column.PercentOpticalDuplicatesRingOverlap: float(
                    qtable.get("% optical duplicates ring-overlap")
                ),
                Column.PercentOpticalDuplicatesFalseDetection: float(
                    qtable.get("% optical duplicates false-detection")
                ),
                Column.PctPFQ20Flows: _optional_float(
                    qtable, "PCT_PF_Q20_FLOWS"
                ),
                Column.PctPFQ30Flows: _optional_float(
                    qtable, "PCT_PF_Q30_FLOWS"
                ),
                Column.PctPFQ20Snvq: _optional_float(qtable, "PCT_PF_Q20_SNVQ"),
                Column.PctPFQ30Snvq: _optional_float(qtable, "PCT_PF_Q30_SNVQ"),
                Column.PctPFQ40Snvq: _optional_float(qtable, "PCT_PF_Q40_SNVQ"),
                Column.PpmseqPctReadEndUnreached: _optional_float(
                    qtable, "PCT_read_end_unreached"
                ),
                Column.PpmseqMixedReadMeanCoverage: _optional_float(
                    qtable, "MIXED_read_mean_coverage"
                ),
                Column.PpmseqPctFailedAdapterDimers: _optional_float(
                    qtable, "PCT_failed_adapter_dimers"
                ),
                Column.PpmseqPctMixedBothTagsWhereEndreached: _optional_float(
                    qtable, "PCT_MIXED_both_tags_where_endreached"
                ),
            }
        )
    return pandas.DataFrame(rows, columns=_COLUMNS)
