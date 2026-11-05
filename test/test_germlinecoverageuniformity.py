import pandas
import pytest

import test.cachechecker
from qcetl.common import InvalidRecordError
from qcetl.column import GermlineCoverageUniformityCnvColumn as CnvColumn
from qcetl.germlinecoverageuniformity import GermlineCoverageUniformityCache
from qcetl.germlinecoverageuniformity.parse import parse_cnv, parse_coverage

FILES = "test/files/germlinecoverageuniformity"


def metadata(swid):
    return {
        "swid": swid,
        "donor": "DONOR",
        "group_id": "GROUP",
        "library_design": "WG",
        "pinery_lims_ids": ["id1", "id2"],
        "tissue_origin": "Ly",
        "tissue_type": "R",
    }


def tests_germlinecoverageuniformity():
    test.cachechecker.check(
        GermlineCoverageUniformityCache(),
        [
            {
                "coverage_path": f"{FILES}/HG008.wgs_coverage_metrics.csv",
                "cnv_path": f"{FILES}/HG008.cnv_metrics.csv",
                "cnv_swid": "CNV_SWID1",
                **metadata("SWID1"),
            },
            {
                "coverage_path": f"{FILES}/padded.wgs_coverage_metrics.csv",
                "cnv_path": f"{FILES}/padded.cnv_metrics.csv",
                "cnv_swid": "CNV_SWID2",
                **metadata("SWID2"),
            },
            {
                "coverage_path": f"{FILES}/HG008.wgs_coverage_metrics.csv",
                "cnv_path": None,
                "cnv_swid": None,
                **metadata("SWID3"),
            },
        ],
        {
            "coverage_metrics": f"{FILES}/coverage_metrics.csv",
            "cnv_metrics": f"{FILES}/cnv_metrics.csv",
        },
    )


def tests_germlinecoverageuniformity_no_deletions(tmp_path):
    path = tmp_path / "zero.cnv_metrics.csv"
    path.write_text(
        "CNV SUMMARY,,PMAD,0.2\n"
        "CNV SUMMARY,,Coverage uniformity,0.1\n"
        "CNV SUMMARY,,Number of amplifications,5\n"
        "CNV SUMMARY,,Number of deletions,0\n"
    )
    df = parse_cnv(str(path))
    assert pandas.isna(df.at[0, CnvColumn.AmplificationDeletionRatio])


def tests_germlinecoverageuniformity_missing_required(tmp_path):
    path = tmp_path / "bad.wgs_coverage_metrics.csv"
    path.write_text("COVERAGE SUMMARY,,Aligned bases,100\n")
    with pytest.raises(InvalidRecordError):
        parse_coverage(str(path))
