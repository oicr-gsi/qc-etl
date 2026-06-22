import pandas
from pandas import DataFrame

from qcetl.column import BedToolsGenomeCovColumn as GenCovCol


def genomecov_coverage_percentile(
    df,
    max_coverage=200,
    coverage_steps=10,
    coverage_name="Coverage",
    percent_name="Percent Genome Covered",
) -> DataFrame:
    """
    Calculate what percentage of genome is at or above a range of coverages

    Args:
        df: DataFrame with IUS columsn
        max_coverage: Maximum coverage to consider
        coverage_steps: Steps between the coverages that are considered
        coverage_name: The name of the column that specifies coverage
        percent_name: The name of the column that specifies percent of genome at
            coverage

    Returns:

    """
    df = df[df[GenCovCol.Chrom] == "genome"]

    genome_length = max(df[GenCovCol.ChromLength])
    min_cov = []
    per_cov = []
    for i in range(1, max_coverage, coverage_steps):
        min_cov.append(i)
        per_cov.append(
            sum(df[df[GenCovCol.Coverage] > i][GenCovCol.BasesAtCoverage])
            / genome_length
            * 100
        )

    return pandas.DataFrame({coverage_name: min_cov, percent_name: per_cov})


def mean_coverage_genomecov(df: DataFrame) -> float:
    """
    Calculate mean coverage from the `bedtools genomecov` call

    Args:
        df: DataFrame of bedtools output

    Returns:

    """
    genome = df[df[GenCovCol.Chrom] == "genome"]
    genome_len = max(genome[GenCovCol.ChromLength])
    mean_cov = (
        sum(genome[GenCovCol.Coverage] * genome[GenCovCol.BasesAtCoverage])
        / genome_len
    )
    return mean_cov


def coverage_uniformity_genomecov(df: DataFrame, mean_cov=None) -> float:
    """
    Calculate coverage uniformity from `betools genomecov` call

    Args:
        df: DataFrame of bedtools output
        mean_cov: Mean coverage of input DataFrame. If None, will be calculated

    Returns: Coverage uniformity is fraction of bases greater than 0.2 * mean coverage

    """
    genome = df[df[GenCovCol.Chrom] == "genome"]
    genome_len = max(genome[GenCovCol.ChromLength])

    if mean_cov is None:
        mean_cov = mean_coverage_genomecov(genome)

    uniformity = (
        sum(
            genome[genome[GenCovCol.Coverage] > 0.2 * mean_cov][
                GenCovCol.BasesAtCoverage
            ]
        )
        / genome_len
    )
    return uniformity


def genomecov_coverage_and_uniformity(
    df, coverage_name="Mean Coverage", uniformity_name="Coverage Uniformity"
) -> DataFrame:
    """
    Calculates mean genome coverage and coverage uniformity from the
    `bedtools genomecov` cache.

    Args:
        df: DataFrame with the IUS columns
        coverage_name: Name of the coverage column
        uniformity_name: Name of the uniformity column

    Returns: New DataFrame with the IUS columns and calculated coverage and uniformity
        column

    """
    results = []
    genome = df[df[GenCovCol.Chrom] == "genome"]

    for ius, df in genome.groupby(
        [GenCovCol.Barcodes, GenCovCol.Lane, GenCovCol.Run, GenCovCol.FileSWID]
    ):
        mean_cov = mean_coverage_genomecov(df)
        uniformity = coverage_uniformity_genomecov(df, mean_cov)
        results.append(list(ius) + [mean_cov, uniformity])

    return pandas.DataFrame.from_records(
        results,
        columns=[
            GenCovCol.Barcodes,
            GenCovCol.Lane,
            GenCovCol.Run,
            GenCovCol.FileSWID,
            coverage_name,
            uniformity_name,
        ],
    )
