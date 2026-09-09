import qcetl.common
from qcetl.column import HmfRnaSeqMetricsColumn as Column
from qcetl.hmfrnaseqmetrics.parse import parse_record


class HmfRnaSeqMetricsCache(qcetl.common.Cache):
    """
    RNA QC from Picard ``CollectRnaSeqMetrics``, run on a merged/call-ready RNA
    BAM in the hmftools pipeline. One build record points at the
    ``*.rna_seq_metrics.txt`` file. ``PCT_CODING_BASES`` is the "mapped to
    coding" metric.
    """

    def __init__(self):
        self.name = "hmfrnaseqmetrics"

        # Merged/call-ready identifiers
        identifiers = {
            Column.Donor: "s",
            Column.FileSWID: "s",
            Column.GroupID: "s",
            Column.LibraryDesign: "s",
            Column.MergedPineryLimsID: "as",
            Column.Project: "s",
            Column.Reference: "s",
            Column.TissueOrigin: "s",
            Column.TissueType: "s",
        }

        self.schema_versions = {
            1: {
                "summary": {
                    **identifiers,
                    Column.WorkflowVersion: "qs",
                    Column.PfBases: "i",
                    Column.PfAlignedBases: "i",
                    Column.RibosomalBases: "qi",
                    Column.CodingBases: "i",
                    Column.UtrBases: "i",
                    Column.IntronicBases: "i",
                    Column.IntergenicBases: "i",
                    Column.IgnoredReads: "i",
                    Column.CorrectStrandReads: "i",
                    Column.IncorrectStrandReads: "i",
                    Column.NumR1TranscriptStrandReads: "i",
                    Column.NumR2TranscriptStrandReads: "i",
                    Column.NumUnexplainedReads: "i",
                    Column.PctR1TranscriptStrandReads: "f",
                    Column.PctR2TranscriptStrandReads: "f",
                    Column.PctRibosomalBases: "f",
                    Column.PctCodingBases: "f",
                    Column.PctUtrBases: "f",
                    Column.PctIntronicBases: "f",
                    Column.PctIntergenicBases: "f",
                    Column.PctMrnaBases: "f",
                    Column.PctUsableBases: "f",
                    Column.PctCorrectStrandReads: "f",
                    Column.MedianCvCoverage: "f",
                    Column.Median5PrimeBias: "f",
                    Column.Median3PrimeBias: "f",
                    Column.Median5PrimeTo3PrimeBias: "f",
                },
            }
        }

        self.columns = {1: {"summary": Column}}

        self.input_format = {
            "project": "s",
            "pinery_lims_ids": "as",
            "donor": "s",
            "group_id": "s",
            "library_design": "s",
            "tissue_origin": "s",
            "tissue_type": "s",
            "reference": "s",
            "path": "p",
            "swid": "s",
            "workflow_version": ["i", "i", "i"],
        }

        self.primary_key = {1: {"summary": [Column.FileSWID]}}

        self.input_key = {1: ("swid", Column.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        df = parse_record(single_input["path"])
        return {1: {"summary": df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "summary": {
                Column.MergedPineryLimsID: single_input["pinery_lims_ids"],
                Column.Project: single_input["project"],
                Column.Reference: single_input.get("reference", "Unknown"),
                Column.FileSWID: single_input["swid"],
                Column.Donor: single_input["donor"],
                Column.GroupID: single_input["group_id"],
                Column.LibraryDesign: single_input["library_design"],
                Column.TissueOrigin: single_input["tissue_origin"],
                Column.TissueType: single_input["tissue_type"],
                Column.WorkflowVersion: ".".join(
                    str(x) for x in single_input["workflow_version"]
                ),
            }
        }
