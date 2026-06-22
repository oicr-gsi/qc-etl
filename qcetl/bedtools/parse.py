import logging
import numpy
import pandas
from pandas import DataFrame
from typing import Tuple

from qcetl.column import (
    BedFormatColumn,
    BedToolsCoverageHistColumn,
    BedToolsGenomeCovColumn,
    BedToolsGenomeCovPerBaseColumn,
    BedToolsGenomeCovCalculationsColumn as CalcCol,
    BedToolsGenomeCovCoveragePercentileColumn as CovPercColumn,
)
from qcetl.bedtools.utility import (
    mean_coverage_genomecov,
    coverage_uniformity_genomecov,
    genomecov_coverage_percentile,
)

BED_COLUMNS = list(BedFormatColumn.values())
logger = logging.getLogger(__name__)


def parse_coverage_histogram(path: str) -> DataFrame:
    """
    Parses bedtools output created by `bedtools coverage` with histogram option. Any
    columns provided by the bed file will be in the output. To deal with this, all
    valid bed format columns are returned. The special `all` chromosome is added by
    bedtools

    Args:
        path: Path to file

    Returns: DataFrame with 12 bed format columns and 4 added bedtools column

    """
    # engine is required here because the "c" engine will not handle variable number
    # of columns; if unspecified, the function picks based on file size
    raw = pandas.read_csv(path, header=None, sep="\t", engine="python")
    chrom = raw[raw[0] != "all"]

    # Name columns that are present in bedtools output
    existing = BED_COLUMNS[0 : len(chrom.columns) - 4]
    existing = existing + [
        BedToolsCoverageHistColumn.Coverage,
        BedToolsCoverageHistColumn.BasesAtCoverage,
        BedToolsCoverageHistColumn.FeatureLength,
        BedToolsCoverageHistColumn.FractionAtCoverage,
    ]
    chrom.columns = existing

    # These bed format columns were not in the output and are added for consistency
    to_add = BED_COLUMNS[len(chrom.columns) - 4 :]
    to_add_df = {x: [numpy.nan] for x in to_add}
    parsed = pandas.concat([chrom, pandas.DataFrame(to_add_df)], axis=1)

    # `all` output is always the same, regardless of bed input
    all_df = raw[raw[0] == "all"]
    all_df = all_df[all_df.columns[0:5]]
    all_df.columns = [
        BedToolsCoverageHistColumn.Chrom,
        BedToolsCoverageHistColumn.Coverage,
        BedToolsCoverageHistColumn.BasesAtCoverage,
        BedToolsCoverageHistColumn.FeatureLength,
        BedToolsCoverageHistColumn.FractionAtCoverage,
    ]
    # Last two columns of `all` align with arbitrary bed column, so make type explicit
    all_df = all_df.astype(
        {
            BedToolsCoverageHistColumn.FeatureLength: int,
            BedToolsCoverageHistColumn.FractionAtCoverage: float,
        }
    )

    return pandas.concat([parsed, all_df]).infer_objects()


def parse_genomecov(path: str) -> DataFrame:
    """
    Parses default output from `bedtools genomecov` (always 5 columns)

    Args:
        path: Path to file

    Returns:

    """
    return pandas.read_csv(
        path,
        sep="\t",
        header=None,
        names=[
            BedToolsGenomeCovColumn.Chrom,
            BedToolsGenomeCovColumn.Coverage,
            BedToolsGenomeCovColumn.BasesAtCoverage,
            BedToolsGenomeCovColumn.ChromLength,
            BedToolsGenomeCovColumn.FractionAtCoverage,
        ],
        engine="python",  # Probably unnecessary, but here for consistency
    )


def parse_genomecov_per_base(path: str) -> DataFrame:
    """
    Parses `bedtools genomecov -d` output (always 3 columns)

    Args:
        path: Path to file

    Returns:

    """
    return pandas.read_csv(
        path,
        sep="\t",
        header=None,
        names=[
            BedToolsGenomeCovPerBaseColumn.Chrom,
            BedToolsGenomeCovPerBaseColumn.Position,
            BedToolsGenomeCovPerBaseColumn.Coverage,
        ],
        engine="python",  # Probably unnecessary, but here for consistency
    )


def parse_record(
    path_genomecov: str, path_genomecov_per_page: str
) -> Tuple[DataFrame, DataFrame]:
    """
    The SARSCov2 workflow produces five bedtools output per workflow run.

    Args:
        path_genomecov: File path to genome coverage output
        path_genomecov_per_page: File path to genome coverage per base output

    Returns: The calculated metrics and the coverage percentiles.

    """
    genomecov = parse_genomecov(path_genomecov)
    genomecov_per_base = parse_genomecov_per_base(path_genomecov_per_page)
    mean_cov = mean_coverage_genomecov(genomecov)
    uniform = coverage_uniformity_genomecov(genomecov, mean_cov)
    median_cov = genomecov_per_base[
        BedToolsGenomeCovPerBaseColumn.Coverage
    ].median()
    cov_10, cov_90 = genomecov_per_base[
        BedToolsGenomeCovPerBaseColumn.Coverage
    ].quantile([0.1, 0.9], "nearest")
    calc = pandas.DataFrame(
        {
            CalcCol.MeanCoverage: mean_cov,
            CalcCol.CoverageUniformity: uniform,
            CalcCol.MedianCoverage: median_cov,
            CalcCol.Coverage10Percentile: cov_10,
            CalcCol.Coverage90Percentile: cov_90,
        },
        index=[0],
    )
    cov_perc = genomecov_coverage_percentile(
        genomecov,
        coverage_name=CovPercColumn.Coverage,
        percent_name=CovPercColumn.PercentGenomeCovered,
    )

    return calc, cov_perc
