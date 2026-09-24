import json
import pandas
import test.cachechecker
from qcetl.column import UltimaLibraryMetricsColumn as Column
from qcetl.ultimalibrarymetrics import UltimaLibraryMetricsCache
from qcetl.ultimalibrarymetrics.parse import parse_records


class CannedUltimaLibraryMetrics(UltimaLibraryMetricsCache):
    """
    The actual class gets data from the Nexus API using `fetch`. For testing
    purposes, this class is over-written to load from local disk
    """

    def fetch(self, run_id):
        with open(self.host, "r") as f:
            return json.load(f)


def tests_ultimalibrarymetrics():
    test.cachechecker.check(
        CannedUltimaLibraryMetrics(
            host="test/files/ultimalibrarymetrics/sample_response.json"
        ),
        [
            {"run": "RUN0001", "barcode": "Z1428", "pinery_lims_id": "ID1"},
            {"run": "RUN0001", "barcode": "Z1500", "pinery_lims_id": "ID2"},
            {"run": "RUN0001", "barcode": "Z1600", "pinery_lims_id": "ID3"},
        ],
        {"ultimalibrarymetrics": "test/files/ultimalibrarymetrics/RUN0001.csv"},
    )


_MINIMAL_QTABLE = {
    "Mean_cvg": "0",
    "% duplicates": "0",
    "F80": "0",
    "F90": "0",
    "F95": "0",
    "%>=1x": "0",
    "%>=10x": "0",
    "%>=20x": "0",
    "%>=50x": "0",
    "%>=100x": "0",
    "%>=500x": "0",
    "%>=1000x": "0",
    "F80@30x": "0",
    "F90@30x": "0",
    "F95@30x": "0",
    "MAPQ >= 1": "0",
    "MAPQ >= 10": "0",
    "MAPQ >= 20": "0",
    "MAPQ >= 30": "0",
    "median_cvg": "0",
    "Indel_Rate": "0",
    "Mean_quality": "30.0",
    "PCT_Chimeras": "0",
    "Mismatch_Rate": "0",
    "PCT_PF_aligned": "0",
    "Failed_QC_reads": "0",
    "Mean_Read_Length": "0",
    "PCT_PF_Q20_bases": "0",
    "PCT_PF_Q30_bases": "0",
    "PF_Barcode_reads": "0",
    "PCT_PF_HQ_aligned": "0",
    "Median_Read_Length": "0",
    "PCT_Failed_QC_reads": "0",
    "PCT_PF_Reads_aligned": "0",
    "PCT_SOFTCLIPPED_bases": "0",
    "Mean_Aligned_Read_Length": "0",
    "% optical duplicates ring-overlap": "0",
    "% optical duplicates false-detection": "0",
}


def tests_ppm_barcode_normalization():
    data = [{"barcode": "ppm044", "qtable": _MINIMAL_QTABLE}]

    # Zero-padding difference between the input barcode and the Nexus
    # response barcode shouldn't stop the match.
    table = parse_records(data, "ppm0044")
    assert len(table) == 1
    assert table.iloc[0][Column.Barcode] == "ppm0044"
    assert table.iloc[0][Column.MeanQuality] == 30.0

    # A genuinely different barcode still shouldn't match.
    table = parse_records(data, "ppm045")
    assert len(table) == 0


def tests_bracketed_f_at_30x_values_are_null():
    qtable = dict(
        _MINIMAL_QTABLE,
        **{"F80@30x": "(1.26)", "F90@30x": "(2.5)", "F95@30x": "3.1"},
    )
    data = [{"barcode": "Z1428", "qtable": qtable}]

    table = parse_records(data, "Z1428")
    assert len(table) == 1
    assert pandas.isna(table.iloc[0][Column.F80At30x])
    assert pandas.isna(table.iloc[0][Column.F90At30x])
    assert table.iloc[0][Column.F95At30x] == 3.1
