import qcetl.common
from qcetl.column import (
    HmfBamToolsIdentifierColumn as Identifier,
    HmfBamToolsSummaryColumn as Summary,
    HmfBamToolsCoverageColumn as Coverage,
    HmfBamToolsFragmentLengthColumn as FragLength,
    HmfBamToolsFlagstatColumn as Flagstat,
)
from qcetl.hmfbamtools.parse import parse_record


class HmfBamToolsCache(qcetl.common.Cache):
    """
    QC metrics from hmftools ``bam-tools`` (BamMetrics), run on a merged/
    call-ready BAM. One build record points at ``*.bam_metric.summary.tsv``;
    the sibling coverage, fragment-length and flag-count files are derived.
    """

    def __init__(self):
        self.name = "hmfbamtools"

        # Merged/call-ready identifiers shared by every table
        identifiers = {
            Identifier.Donor: "s",
            Identifier.FileSWID: "s",
            Identifier.GroupID: "s",
            Identifier.LibraryDesign: "s",
            Identifier.MergedPineryLimsID: "as",
            Identifier.Project: "s",
            Identifier.Reference: "s",
            Identifier.TissueOrigin: "s",
            Identifier.TissueType: "s",
        }

        self.schema_versions = {
            1: {
                "hmfbamtools": {
                    **identifiers,
                    Summary.WorkflowVersion: "qs",
                    Summary.TotalRegionBases: "i",
                    Summary.TotalReads: "i",
                    Summary.DuplicateReads: "i",
                    Summary.DualStrandReads: "i",
                    Summary.MeanCoverage: "f",
                    Summary.StdDevCoverage: "f",
                    Summary.MedianCoverage: "i",
                    Summary.MadCoverage: "i",
                    Summary.LowMapQualPercent: "f",
                    Summary.DuplicatePercent: "f",
                    Summary.UnpairedPercent: "f",
                    Summary.LowBaseQualPercent: "f",
                    Summary.OverlappingReadPercent: "f",
                    Summary.CappedCoverage: "f",
                    Summary.DepthCoverage1: "f",
                    Summary.DepthCoverage5: "f",
                    Summary.DepthCoverage10: "f",
                    Summary.DepthCoverage15: "f",
                    Summary.DepthCoverage20: "f",
                    Summary.DepthCoverage25: "f",
                    Summary.DepthCoverage30: "f",
                    Summary.DepthCoverage40: "f",
                    Summary.DepthCoverage50: "f",
                    Summary.DepthCoverage60: "f",
                    Summary.DepthCoverage70: "f",
                    Summary.DepthCoverage80: "f",
                    Summary.DepthCoverage90: "f",
                    Summary.DepthCoverage100: "f",
                },
                "coverage": {
                    **identifiers,
                    Coverage.Coverage: "i",
                    Coverage.Count: "i",
                },
                "fragment_length": {
                    **identifiers,
                    FragLength.FragmentLength: "i",
                    FragLength.Count: "i",
                },
                "flagstat": {
                    **identifiers,
                    Flagstat.Category: "s",
                    Flagstat.QcPassedReads: "i",
                    Flagstat.QcFailedReads: "i",
                    Flagstat.Percentage: "qf",
                },
            }
        }

        self.columns = {
            1: {
                "hmfbamtools": Summary,
                "coverage": Coverage,
                "fragment_length": FragLength,
                "flagstat": Flagstat,
            }
        }

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

        self.primary_key = {
            1: {
                "hmfbamtools": [Identifier.FileSWID],
                "coverage": [Identifier.FileSWID, Coverage.Coverage],
                "fragment_length": [
                    Identifier.FileSWID,
                    FragLength.FragmentLength,
                ],
                "flagstat": [Identifier.FileSWID, Flagstat.Category],
            }
        }

        self.input_key = {1: ("swid", Identifier.FileSWID)}

    def parse_single_record(self, single_input, schema_version):
        tables = parse_record(single_input["path"])
        return {1: tables}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        identifiers = {
            Identifier.MergedPineryLimsID: single_input["pinery_lims_ids"],
            Identifier.Project: single_input["project"],
            Identifier.Reference: single_input.get("reference", "Unknown"),
            Identifier.FileSWID: single_input["swid"],
            Identifier.Donor: single_input["donor"],
            Identifier.GroupID: single_input["group_id"],
            Identifier.LibraryDesign: single_input["library_design"],
            Identifier.TissueOrigin: single_input["tissue_origin"],
            Identifier.TissueType: single_input["tissue_type"],
        }

        summary = dict(identifiers)
        summary[Summary.WorkflowVersion] = ".".join(
            str(x) for x in single_input["workflow_version"]
        )

        return {
            "hmfbamtools": summary,
            "coverage": dict(identifiers),
            "fragment_length": dict(identifiers),
            "flagstat": dict(identifiers),
        }
