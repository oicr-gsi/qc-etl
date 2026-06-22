import json
import logging
from typing import Dict, Tuple, Any
import numpy as np
import math

import pandas as pd
from pandas import DataFrame

from qcetl.column import (
    UmiQcColumn,
    UmiQcFamilyColumn,
    UmiQcExtractionColumn,
)
from qcetl.bamqc4.parse import parse_record as parse_bamQC

logger = logging.getLogger(__name__)


def create_family_size_distribution(input_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extracts the umiCountsPerPosition json file which has a int count for each umi at each postion before and after deduplication

    Args:
        input_df: The loaded umi_cumiCountsPerPosition Dataframe

    Returns: The DataFrame of reads family and reads count in every families

    """
    total_families = input_df.shape[0]
    total_umi_count = sum(input_df["instances_post"])
    input_df.rename(
        columns={
            "counts": UmiQcFamilyColumn.FamilySize,
            "instances_pre": UmiQcFamilyColumn.PreDedupUmiCounts,
            "instances_post": UmiQcFamilyColumn.PostDedupUmiCounts,
        },
        inplace=True,
    )
    return {
        "family_size_distribution": input_df,
        "total_families": total_families,
        "total_umi_count": total_umi_count,
    }


def parse_extraction_metrics(input_data: Dict[str, Any]) -> DataFrame:
    result = {}
    for column in [
        UmiQcExtractionColumn.TotalReadsPairs,
        UmiQcExtractionColumn.ReadsPairsWithMatchingPattern,
        UmiQcExtractionColumn.DiscardedReadsPairs,
        UmiQcExtractionColumn.DiscardedReadsPairsDueToUnknownUMI,
        UmiQcExtractionColumn.umiListFile,
        UmiQcExtractionColumn.pattern1,
        UmiQcExtractionColumn.pattern2,
    ]:
        result[column] = input_data[column]
    return DataFrame(result, index=[0])


def create_umiQC_metrics(
    pre_bamQC_json: Dict[str, Any], post_bamQC_json: Dict[str, Any]
) -> DataFrame:
    cov_hist = {
        int(k): int(v) for k, v in pre_bamQC_json["coverage histogram"].items()
    }
    PreDedupMeanDepth = round(
        np.average(list(cov_hist.keys()), weights=list(cov_hist.values())), 6
    )
    variance = np.average(
        (list(cov_hist.keys()) - PreDedupMeanDepth) ** 2,
        weights=list(cov_hist.values()),
    )
    PreDedupDepthSD = math.sqrt(variance)
    cov_hist = {
        int(k): int(v) for k, v in post_bamQC_json["coverage histogram"].items()
    }
    PostDedupMeanDepth = round(
        np.average(list(cov_hist.keys()), weights=list(cov_hist.values())), 6
    )
    variance = np.average(
        (list(cov_hist.keys()) - PostDedupMeanDepth) ** 2,
        weights=list(cov_hist.values()),
    )
    PostDedupDepthSD = math.sqrt(variance)
    PreDedupTotalReads = pre_bamQC_json["total reads"]
    PreDedupMappedReads = pre_bamQC_json["mapped reads"]
    PostDedupTotalReads = post_bamQC_json["total reads"]
    PostDedupMappedReads = post_bamQC_json["mapped reads"]

    return DataFrame(
        {
            UmiQcColumn.PreDedupMeanDepth: PreDedupMeanDepth,
            UmiQcColumn.PostDedupMeanDepth: PostDedupMeanDepth,
            UmiQcColumn.PreDedupTotalReads: PreDedupTotalReads,
            UmiQcColumn.PreDedupMappedReads: PreDedupMappedReads,
            UmiQcColumn.PostDedupTotalReads: PostDedupTotalReads,
            UmiQcColumn.PostDedupMappedReads: PostDedupMappedReads,
            UmiQcColumn.PreDedupDepthSD: PreDedupDepthSD,
            UmiQcColumn.PostDedupDepthSD: PostDedupDepthSD,
        },
        index=[0],
    )


def parse_record(
    umiCountsPerPosition_path: str,
    pre_dedup_bam_metrics_path: str,
    post_dedup_bam_metrics_path: str,
    extraction_metrics_path: str,
) -> Tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame]:

    with open(umiCountsPerPosition_path, "r") as f:
        umiCountsPerPosition_df = pd.read_csv(f, sep="\t", header=0)

    family_size_distribution = create_family_size_distribution(
        umiCountsPerPosition_df
    )
    family_size_distribution_df = family_size_distribution[
        "family_size_distribution"
    ]

    with open(extraction_metrics_path, "r") as f:
        extraction_metrics_input = json.load(f)
    extraction_metrics_df = parse_extraction_metrics(extraction_metrics_input)

    with open(pre_dedup_bam_metrics_path, "r") as f:
        PreDedup_bamMetrics = json.load(f)
        bamqc_version = [
            int(x) for x in PreDedup_bamMetrics["workflow version"].split(".")
        ]
    pre_dedup_bam_metrics_df = parse_bamQC(
        pre_dedup_bam_metrics_path, bamqc_version
    )

    with open(post_dedup_bam_metrics_path, "r") as f:
        PostDedup_bamMetrics = json.load(f)
        bamqc_version = [
            int(x) for x in PostDedup_bamMetrics["workflow version"].split(".")
        ]
    post_dedup_bam_metrics_df = parse_bamQC(
        post_dedup_bam_metrics_path, bamqc_version
    )

    umiqc_metrics_df = create_umiQC_metrics(
        PreDedup_bamMetrics, PostDedup_bamMetrics
    )
    (
        umiqc_metrics_df[UmiQcColumn.TotalFamilies],
        umiqc_metrics_df[UmiQcColumn.TotalUmiCount],
    ) = (
        family_size_distribution["total_families"],
        family_size_distribution["total_umi_count"],
    )

    return (
        umiqc_metrics_df,
        pre_dedup_bam_metrics_df,
        post_dedup_bam_metrics_df,
        extraction_metrics_df,
        family_size_distribution_df,
    )
