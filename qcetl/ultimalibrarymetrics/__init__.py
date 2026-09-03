import logging
import os

import qcetl.common
from qcetl.column import UltimaLibraryMetricsColumn as Column
from qcetl.common.utility import load_json_from_url
from qcetl.ultimalibrarymetrics.parse import parse_records

logger = logging.getLogger(__name__)


class UltimaLibraryMetricsCache(qcetl.common.Cache):
    def __init__(self, host=None, token_file=None):
        """

        Args:
            host: Nexus hostname. Can be set by the QC_ETL_NEXUS_URL
                environmental variable.
            token_file: Path to a file containing the Nexus auth token.
                Can be set by the QC_ETL_NEXUS_TOKEN_FILE environmental
                variable.
        """
        self.name = "ultimalibrarymetrics"
        self.schema_versions = {
            1: {
                "ultimalibrarymetrics": {
                    Column.Run: "s",
                    Column.GeoGroupID: "s",
                    Column.Barcode: "s",
                    Column.PineryLimsID: "s",
                    Column.MeanCoverage: "f",
                    Column.PercentDuplicates: "f",
                    Column.F80: "f",
                    Column.F90: "f",
                    Column.F95: "f",
                    Column.PercentGte1x: "f",
                    Column.PercentGte10x: "f",
                    Column.PercentGte20x: "f",
                    Column.PercentGte50x: "f",
                    Column.PercentGte100x: "f",
                    Column.PercentGte500x: "f",
                    Column.PercentGte1000x: "f",
                    Column.F80At30x: "f",
                    Column.F90At30x: "f",
                    Column.F95At30x: "f",
                    Column.MAPQGte1: "f",
                    Column.MAPQGte10: "f",
                    Column.MAPQGte20: "f",
                    Column.MAPQGte30: "f",
                    Column.MedianCoverage: "f",
                    Column.IndelRate: "f",
                    Column.MeanQuality: "f",
                    Column.PercentChimeras: "f",
                    Column.MismatchRate: "f",
                    Column.PercentPFAligned: "f",
                    Column.FailedQCReads: "f",
                    Column.MeanReadLength: "f",
                    Column.PercentPFQ20Bases: "f",
                    Column.PercentPFQ30Bases: "f",
                    Column.PFBarcodeReads: "f",
                    Column.PercentPFHQAligned: "f",
                    Column.MedianReadLength: "f",
                    Column.PercentFailedQCReads: "f",
                    Column.PercentPFReadsAligned: "f",
                    Column.PercentSoftclippedBases: "f",
                    Column.MeanAlignedReadLength: "f",
                    Column.PercentOpticalDuplicatesRingOverlap: "f",
                    Column.PercentOpticalDuplicatesFalseDetection: "f",
                    Column.PctPFQ20Flows: "qf",
                    Column.PctPFQ30Flows: "qf",
                    Column.PctPFQ20Snvq: "qf",
                    Column.PctPFQ30Snvq: "qf",
                    Column.PctPFQ40Snvq: "qf",
                    Column.PpmseqPctReadEndUnreached: "qf",
                    Column.PpmseqMixedReadMeanCoverage: "qf",
                    Column.PpmseqPctFailedAdapterDimers: "qf",
                    Column.PpmseqPctMixedBothTagsWhereEndreached: "qf",
                }
            }
        }
        self.columns = {1: {"ultimalibrarymetrics": Column}}
        self.input_format = {
            "run": "s",
            "geo_group_id": "s",
            "pinery_lims_id": "s",
        }
        self.primary_key = {
            1: {
                "ultimalibrarymetrics": [
                    Column.Run,
                    Column.GeoGroupID,
                    Column.PineryLimsID,
                ]
            }
        }
        self.input_key = {1: ("pinery_lims_id", Column.PineryLimsID)}

        self.host = host
        self.token_file = token_file

    def fetch(self, run_id):
        """
        Loads JSON from the Nexus allbarcodes/metrics API for a single run.
        """
        host = self.host or os.getenv("QC_ETL_NEXUS_URL")
        if host is None:
            raise TypeError(
                "Nexus host never specified. Do it during initialization "
                "or via QC_ETL_NEXUS_URL environmental variable"
            )

        token_file = self.token_file or os.getenv("QC_ETL_NEXUS_TOKEN_FILE")
        if token_file is None:
            raise TypeError(
                "Nexus token file never specified. Do it during "
                "initialization or via QC_ETL_NEXUS_TOKEN_FILE "
                "environmental variable"
            )
        with open(token_file, "r") as f:
            token = f.readline().strip()

        url = "https://{}/api/data/allbarcodes/metrics/{}".format(host, run_id)
        data = load_json_from_url(url, headers={"Authorization": token})
        if data is None:
            raise qcetl.common.InvalidRecordError(
                "No data returned from Nexus for run {}".format(run_id)
            )
        return data

    def parse_single_record(self, single_input, schema_version):
        run_id = single_input["run"]
        geo_group_id = single_input["geo_group_id"]
        data = self.fetch(run_id)
        table = parse_records(data, geo_group_id)
        if table.empty:
            logger.warning(
                "No entry for geo_group_id {} found in run {}".format(
                    geo_group_id, run_id
                )
            )
        return {1: {"ultimalibrarymetrics": table}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "ultimalibrarymetrics": {
                Column.Run: single_input["run"],
                Column.PineryLimsID: single_input["pinery_lims_id"],
            }
        }
