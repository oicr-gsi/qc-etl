import qcetl.common
from qcetl.column import HsMetricsColumn as MetricsCol
from qcetl.column import HsMetricsConsensusCruncherColumn
from qcetl.picard.hsmetrics.parse import parse_record


class HsMetricsCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "hsmetrics"
        self.schema_versions = {
            1: {
                "metrics": {
                    MetricsCol.AtDropout: "f",
                    MetricsCol.BaitdesignEfficiency: "i",
                    MetricsCol.BaitSet: "s",
                    MetricsCol.BaitTerritory: "i",
                    MetricsCol.Donor: "s",
                    MetricsCol.FileSWID: "s",
                    MetricsCol.Fold80BasePenalty: "f",
                    MetricsCol.FoldEnrichment: "f",
                    MetricsCol.GCDropout: "f",
                    MetricsCol.GenomeSize: "i",
                    MetricsCol.GroupID: "s",
                    MetricsCol.HetSnpQ: "i",
                    MetricsCol.HetSnpSensitivity: "f",
                    MetricsCol.HsLibrarySize: "qi",
                    MetricsCol.HsPenalty100x: "f",
                    MetricsCol.HsPenalty10x: "f",
                    MetricsCol.HsPenalty20x: "f",
                    MetricsCol.HsPenalty30x: "f",
                    MetricsCol.HsPenalty40x: "f",
                    MetricsCol.HsPenalty50x: "f",
                    MetricsCol.Library: "s",
                    MetricsCol.LibraryDesign: "s",
                    MetricsCol.MaxTargetCoverage: "i",
                    MetricsCol.MeanBaitCoverage: "f",
                    MetricsCol.MeanTargetCoverage: "f",
                    MetricsCol.MedianTargetCoverage: "i",
                    MetricsCol.NearBaitBases: "i",
                    MetricsCol.OffBaitBases: "i",
                    MetricsCol.OnBaitBases: "i",
                    MetricsCol.OnBaitVsSelected: "f",
                    MetricsCol.OnTargetBases: "i",
                    MetricsCol.PctExcAdapter: "i",
                    MetricsCol.PctExcBaseq: "f",
                    MetricsCol.PctExcDupe: "f",
                    MetricsCol.PctExcMapq: "f",
                    MetricsCol.PctExcOffTarget: "f",
                    MetricsCol.PctExcOverlap: "f",
                    MetricsCol.PctOffBait: "f",
                    MetricsCol.PctPfReads: "i",
                    MetricsCol.PctPfUqReads: "f",
                    MetricsCol.PctPfUqReadsAligned: "i",
                    MetricsCol.PctSelectedBases: "f",
                    MetricsCol.PctTargetBases100x: "f",
                    MetricsCol.PctTargetBases10x: "f",
                    MetricsCol.PctTargetBases1x: "f",
                    MetricsCol.PctTargetBases20x: "f",
                    MetricsCol.PctTargetBases2x: "f",
                    MetricsCol.PctTargetBases30x: "f",
                    MetricsCol.PctTargetBases40x: "f",
                    MetricsCol.PctTargetBases50x: "f",
                    MetricsCol.PctUsableBasesOnBait: "f",
                    MetricsCol.PctUsableBasesOnTarget: "f",
                    MetricsCol.PfBases: "i",
                    MetricsCol.PfBasesAligned: "i",
                    MetricsCol.PfReads: "i",
                    MetricsCol.PfUniqueReads: "i",
                    MetricsCol.PfUqBasesAligned: "i",
                    MetricsCol.PfUqReadsAligned: "i",
                    MetricsCol.MergedPineryLimsID: "as",
                    MetricsCol.Project: "s",
                    MetricsCol.ReadGroup: "s",
                    MetricsCol.Reference: "s",
                    MetricsCol.Sample: "s",
                    MetricsCol.TargetTerritory: "i",
                    MetricsCol.TotalReads: "i",
                    MetricsCol.TissueOrigin: "s",
                    MetricsCol.TissueType: "s",
                    MetricsCol.ZeroCvgTargetsPct: "f",
                }
            }
        }
        self.columns = {1: {"metrics": MetricsCol}}
        self.input_format = {
            "donor": "s",
            "file": "p",
            "group_id": "s",
            "library_design": "s",
            "pinery_lims_ids": "as",
            "project": "s",
            "reference": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "swid": "s",
        }
        self.primary_key = {1: {"metrics": [MetricsCol.FileSWID]}}
        self.input_key = {1: ("swid", MetricsCol.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        metrics, _ = parse_record(single_input["file"])
        return {1: {"metrics": metrics}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "metrics": {
                MetricsCol.Donor: single_input["donor"],
                MetricsCol.GroupID: single_input["group_id"],
                MetricsCol.LibraryDesign: single_input["library_design"],
                MetricsCol.MergedPineryLimsID: single_input["pinery_lims_ids"],
                MetricsCol.Project: single_input["project"],
                MetricsCol.TissueOrigin: single_input["tissue_origin"],
                MetricsCol.TissueType: single_input["tissue_type"],
                MetricsCol.FileSWID: single_input["swid"],
                MetricsCol.Reference: single_input.get("reference", "Unknown"),
            }
        }
