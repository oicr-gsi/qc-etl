import pandas

from qcetl.column import UltimaLibraryMetricsColumn as Column

_COLUMNS = [
    Column.SampleName,
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


def _to_float(value):
    """
    Nexus sometimes wraps values in parentheses, e.g. "(1.26)", which
    `float()` cannot parse directly.
    """
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("(") and value.endswith(")"):
            value = value[1:-1]
    return float(value)


def _optional_float(qtable, key):
    """
    Some qtable fields are only present for certain runs. Missing fields
    are stored as null rather than failing the parse.
    """
    value = qtable.get(key)
    return None if value is None else _to_float(value)


def parse_records(data):
    """
    Turn the Nexus allbarcodes/metrics response into a DataFrame, keeping
    only entries with a non-blank Sample name.

    Args:
        data: List of {"barcode": ..., "qtable": {...}} dicts, as returned
            by the Nexus API.

    Returns:

    """
    rows = []
    for entry in data:
        qtable = entry.get("qtable", {})
        sample = (qtable.get("Sample") or "").strip()
        if not sample:
            continue
        rows.append(
            {
                Column.SampleName: sample,
                Column.Barcode: entry.get("barcode"),
                Column.MeanCoverage: _to_float(qtable.get("Mean_cvg")),
                Column.PercentDuplicates: _to_float(qtable.get("% duplicates")),
                Column.F80: _to_float(qtable.get("F80")),
                Column.F90: _to_float(qtable.get("F90")),
                Column.F95: _to_float(qtable.get("F95")),
                Column.PercentGte1x: _to_float(qtable.get("%>=1x")),
                Column.PercentGte10x: _to_float(qtable.get("%>=10x")),
                Column.PercentGte20x: _to_float(qtable.get("%>=20x")),
                Column.PercentGte50x: _to_float(qtable.get("%>=50x")),
                Column.PercentGte100x: _to_float(qtable.get("%>=100x")),
                Column.PercentGte500x: _to_float(qtable.get("%>=500x")),
                Column.PercentGte1000x: _to_float(qtable.get("%>=1000x")),
                Column.F80At30x: _to_float(qtable.get("F80@30x")),
                Column.F90At30x: _to_float(qtable.get("F90@30x")),
                Column.F95At30x: _to_float(qtable.get("F95@30x")),
                Column.MAPQGte1: _to_float(qtable.get("MAPQ >= 1")),
                Column.MAPQGte10: _to_float(qtable.get("MAPQ >= 10")),
                Column.MAPQGte20: _to_float(qtable.get("MAPQ >= 20")),
                Column.MAPQGte30: _to_float(qtable.get("MAPQ >= 30")),
                Column.MedianCoverage: _to_float(qtable.get("median_cvg")),
                Column.IndelRate: _to_float(qtable.get("Indel_Rate")),
                Column.MeanQuality: _to_float(qtable.get("Mean_quality")),
                Column.PercentChimeras: _to_float(qtable.get("PCT_Chimeras")),
                Column.MismatchRate: _to_float(qtable.get("Mismatch_Rate")),
                Column.PercentPFAligned: _to_float(
                    qtable.get("PCT_PF_aligned")
                ),
                Column.FailedQCReads: _to_float(qtable.get("Failed_QC_reads")),
                Column.MeanReadLength: _to_float(
                    qtable.get("Mean_Read_Length")
                ),
                Column.PercentPFQ20Bases: _to_float(
                    qtable.get("PCT_PF_Q20_bases")
                ),
                Column.PercentPFQ30Bases: _to_float(
                    qtable.get("PCT_PF_Q30_bases")
                ),
                Column.PFBarcodeReads: _to_float(
                    qtable.get("PF_Barcode_reads")
                ),
                Column.PercentPFHQAligned: _to_float(
                    qtable.get("PCT_PF_HQ_aligned")
                ),
                Column.MedianReadLength: _to_float(
                    qtable.get("Median_Read_Length")
                ),
                Column.PercentFailedQCReads: _to_float(
                    qtable.get("PCT_Failed_QC_reads")
                ),
                Column.PercentPFReadsAligned: _to_float(
                    qtable.get("PCT_PF_Reads_aligned")
                ),
                Column.PercentSoftclippedBases: _to_float(
                    qtable.get("PCT_SOFTCLIPPED_bases")
                ),
                Column.MeanAlignedReadLength: _to_float(
                    qtable.get("Mean_Aligned_Read_Length")
                ),
                Column.PercentOpticalDuplicatesRingOverlap: _to_float(
                    qtable.get("% optical duplicates ring-overlap")
                ),
                Column.PercentOpticalDuplicatesFalseDetection: _to_float(
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
