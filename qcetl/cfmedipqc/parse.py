"""
CfMeDipQC parsing module.

Parse individual CfMeDipQC records and combine them into master data table. Cache
master data tables for quick retrieval.
"""

import json
import logging
from typing import Dict

import numpy
import pandas
from pandas import DataFrame

from qcetl.column import CfMeDipQcColumn as Column
from qcetl.column import (
    InsertSizeMetricsColumn as InsertColumn,
    InsertSizeMetricsHistogramColumn as HistColumn,
)
import qcetl.common.utility
import qcetl.picard.insertsizemetrics.parse

logger = logging.getLogger(__name__)


def parse_record(path: str, insert_path: str) -> Dict[str, DataFrame]:
    """
    Convert CfMeDipQC JSON to DataFrame.

    Args:
        path: File path to CfMeDipQC JSON file
        insert_path: File path to CfMeDipQC Picard InsertSizeMetrics
    Returns:
        Single row DataFrame
    """

    with open(path, "r") as f:
        medip_json = json.load(f)
    df = pandas.json_normalize(
        {
            Column.ATDropout: float(medip_json["AT_DROPOUT"]),
            Column.AccumulationLevel: medip_json["ACCUMULATION_LEVEL"],
            Column.CInRegions: int(medip_json["regions.C"]),
            Column.Category: medip_json["CATEGORY"],
            Column.CpGInRegions: int(medip_json["regions.CG"]),
            Column.CpGsInReference: int(
                float(medip_json["genome.CG"])
            ),  # float deals with string scientific notation
            Column.CsInReference: int(
                float(medip_json["genome.C"])
            ),  # float deals with string scientific notation
            Column.EstimatedLibrarySize: (
                int(medip_json["ESTIMATED_LIBRARY_SIZE"])
                if medip_json["ESTIMATED_LIBRARY_SIZE"]
                else numpy.nan
            ),
            Column.GCDropout: float(medip_json["GC_DROPOUT"]),
            Column.GInRegions: int(medip_json["regions.G"]),
            Column.GsInReference: int(
                float(medip_json["genome.G"])
            ),  # float deals with string scientific notation
            Column.MeanReadLength: float(medip_json["MEAN_READ_LENGTH"]),
            Column.MethylationBeta: float(medip_json["THALIANA_BETA"]),
            Column.NormalizedCoverageQ1: float(medip_json["GC_NC_0_19"]),
            Column.NormalizedCoverageQ2: float(medip_json["GC_NC_20_39"]),
            Column.NormalizedCoverageQ3: float(medip_json["GC_NC_40_59"]),
            Column.NormalizedCoverageQ4: float(medip_json["GC_NC_60_79"]),
            Column.NormalizedCoverageQ5: float(medip_json["GC_NC_80_100"]),
            Column.NumAlignedReads: int(medip_json["ALIGNED_READS"]),
            Column.NumAthalianaMethylReads: int(medip_json["methyl"]),
            Column.NumAthalianaUnmethylReads: int(medip_json["unmeth"]),
            Column.NumBadCycles: int(medip_json["BAD_CYCLES"]),
            Column.NumDuplicatePairs: int(medip_json["READ_PAIR_DUPLICATES"]),
            Column.NumNonPrimaryReads: int(
                medip_json["SECONDARY_OR_SUPPLEMENTARY_RDS"]
            ),
            Column.NumNonPrimaryReadsExamined: int(
                medip_json["READ_PAIRS_EXAMINED"]
            ),
            Column.NumOpticalDuplicatePairs: int(
                medip_json["READ_PAIR_OPTICAL_DUPLICATES"]
            ),
            Column.NumReadsAfterDuplicateMarking: int(medip_json["total"]),
            Column.NumReadsAlignedInPairs: int(
                medip_json["READS_ALIGNED_IN_PAIRS"]
            ),
            Column.NumReadsWithCpG: int(medip_json["numberReadsCG"]),
            Column.NumReadsWithoutCpG: int(medip_json["numberReadsWOCG"]),
            Column.NumUnmappedReads: int(medip_json["UNMAPPED_READS"]),
            Column.NumUnmappedReadsAfterDuplicateMarking: int(
                medip_json["unmap"]
            ),
            Column.NumUnpairedDuplicateReads: int(
                medip_json["UNPAIRED_READ_DUPLICATES"]
            ),
            Column.NumUnpairedReadsExamined: int(
                medip_json["UNPAIRED_READS_EXAMINED"]
            ),
            Column.NumWindowsWith0Reads: int(
                float(medip_json["count0"])
            ),  # float deals with string scientific notation
            Column.NumWindowsWith100Reads: int(medip_json["count100"]),
            Column.NumWindowsWith10Reads: int(medip_json["count10"]),
            Column.NumWindowsWith1Reads: int(medip_json["count1"]),
            Column.NumWindowsWith50Reads: int(medip_json["count50"]),
            Column.ObservedToExpectedEnrichment: float(
                medip_json["enrichment.score.GoGe"]
            ),
            Column.ObservedToExpectedInReference: float(
                medip_json["genome.GoGe"]
            ),
            Column.ObservedToExpectedInRegions: float(
                medip_json["regions.GoGe"]
            ),
            Column.PassedFilterAlignedBases: int(
                medip_json["PF_ALIGNED_BASES"]
            ),
            Column.PassedFilterAlignedReads: int(
                medip_json["PF_READS_ALIGNED"]
            ),
            Column.PassedFilterHQAlignedQ20Bases: int(
                medip_json["PF_HQ_ALIGNED_Q20_BASES"]
            ),
            Column.PassedFilterHQAlignedBases: int(
                medip_json["PF_HQ_ALIGNED_BASES"]
            ),
            Column.PassedFilterHQAlignedReads: int(
                medip_json["PF_HQ_ALIGNED_READS"]
            ),
            Column.PassedFilterHQErrorFraction: float(
                medip_json["PF_HQ_ERROR_RATE"]
            ),
            Column.PassedFilterHQMedianMismatches: float(
                medip_json["PF_HQ_MEDIAN_MISMATCHES"]
            ),
            Column.PassedFilterIndelFraction: float(
                medip_json["PF_INDEL_RATE"]
            ),
            Column.PassedFilterMismatchFraction: float(
                medip_json["PF_MISMATCH_RATE"]
            ),
            Column.PassedFilterNoiseReads: int(medip_json["PF_NOISE_READS"]),
            Column.PassedFilterReads: int(medip_json["PF_READS"]),
            Column.PercentChimeras: float(medip_json["PCT_CHIMERAS"]),
            Column.PercentDuplication: float(medip_json["PERCENT_DUPLICATION"])
            * 100,
            Column.PercentPassedFilterAlignedReads: float(
                medip_json["PCT_PF_READS_ALIGNED"]
            ),
            Column.PercentPassedFilterReads: float(medip_json["PCT_PF_READS"]),
            Column.PercentReadsAlignedInPairs: float(
                medip_json["PCT_READS_ALIGNED_IN_PAIRS"]
            ),
            Column.PercentageAthaliana: float(medip_json["PCT_THALIANA"]),
            Column.RelativeCpGFreqInReference: float(medip_json["genome.relH"]),
            Column.RelativeCpGFreqInRegions: float(medip_json["regions.relH"]),
            Column.RelativeCpGFrequencyEnrichment: float(
                medip_json["enrichment.score.relH"]
            ),
            Column.SaturationAnalysisDoubledPearsonCorrelation: float(
                medip_json["maxEstCor"]
            ),
            Column.SaturationAnalysisDoubledReads: int(
                medip_json["maxEstCorReads"]
            ),
            Column.SaturationAnalysisTruePearsonCorrelation: float(
                medip_json["maxTruCor"]
            ),
            Column.SaturationAnalysisTrueReads: float(
                medip_json["maxTruCorReads"]
            ),
            Column.StrandBalance: float(medip_json["STRAND_BALANCE"]),
            Column.TotalClusters: int(medip_json["TOTAL_CLUSTERS"]),
            Column.TotalReads: int(medip_json["TOTAL_READS"]),
            Column.WindowSize: int(medip_json["WINDOW_SIZE"]),
        }
    )

    insert_df, hist = qcetl.picard.insertsizemetrics.parse.parse_record(
        insert_path
    )
    qcetl.common.utility.add_custom_column(
        insert_df,
        InsertColumn.InsertMedian90Percentile,
        qcetl.common.utility.quantile_from_frequency_table(
            hist, 0.9, value_col=HistColumn.InsertSize
        ),
    )
    qcetl.common.utility.add_custom_column(
        insert_df,
        InsertColumn.InsertMedian10Percentile,
        qcetl.common.utility.quantile_from_frequency_table(
            hist, 0.1, value_col=HistColumn.InsertSize
        ),
    )

    return {"cfmedipqc": df, "insert_metrics": insert_df}
