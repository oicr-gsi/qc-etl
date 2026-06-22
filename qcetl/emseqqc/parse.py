import gzip
import numpy
import pandas

from qcetl.column import EmSeqMethylationColumn


def parse_methyl_dackel(path: str) -> pandas.DataFrame:
    """
    Calculates the ratio of methylated sites for the lambda and pUC19 controls,
    as well as the rest of the genome.

    Args:
        path: Path to zipped MethylDackel output

    Returns:

    """
    with gzip.open(path, "rt") as f:
        next(f)  # Skip header
        g_methyl = 0
        g_total = 0
        lambda_methyl = 0
        lambda_total = 0
        puc_methyl = 0
        puc_total = 0
        for line in f:
            line = line.split("\t")
            name = line[0]
            total = int(line[4]) + int(line[5])
            methylated = int(line[4])
            if name == "lambda":
                lambda_total += total
                lambda_methyl += methylated
            elif name == "pUC19":
                puc_total += total
                puc_methyl += methylated
            else:
                g_total += total
                g_methyl += methylated

        if puc_total > 0:
            puc_ratio = puc_methyl / puc_total
        else:
            puc_ratio = numpy.nan

        if lambda_total > 0:
            lambda_ratio = lambda_methyl / lambda_total
        else:
            lambda_ratio = numpy.nan

        if g_total > 0:
            genome_ratio = g_methyl / g_total
        else:
            genome_ratio = numpy.nan
    result = pandas.DataFrame(
        {
            EmSeqMethylationColumn.Genome: genome_ratio,
            EmSeqMethylationColumn.Lambda: lambda_ratio,
            EmSeqMethylationColumn.Puc19: puc_ratio,
        },
        index=[0],
    )
    return result
