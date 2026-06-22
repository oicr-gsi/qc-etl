from typing import Dict, Type, KeysView, ValuesView


class BaseColumn:
    """
    Inherited by all Column classes that specify names of columns as class
    variables.
    """

    @classmethod
    def asdict(cls) -> Dict[str, str]:
        """
        The keys of the returned dictionary are the name of the class variable.
        The values of the returned dictionary are the string values of the
        Pandas DataFrame.

        Returns:

        """
        result = {}
        for c in cls.mro():
            if c != BaseColumn:
                for x in vars(c):
                    if not x.startswith("__"):
                        result[x] = vars(c)[x]
        return result

    @classmethod
    def keys(cls) -> KeysView[str]:
        """
        The names of the class variables

        Returns:

        """
        return cls.asdict().keys()

    @classmethod
    def values(cls) -> ValuesView[str]:
        """
        The string names of the Pandas DataFrame columns

        Returns:

        """
        return cls.asdict().values()


class ColumnStore:
    """
    Holds all columns for a given cache and allows for `getattr` access
    """

    def __init__(self, columns: Dict[str, Type[BaseColumn]]):
        self.columns = columns

    def __getattr__(self, name: str) -> Type[BaseColumn]:
        return self.columns[name]


class ColumnNames:
    """
    Column names shared between modules
    """

    Barcodes = "Barcodes"
    Donor = "Donor"
    FileSWID = "File SWID"
    GroupID = "Group ID"
    Lane = "Lane Number"
    LibraryDesign = "Library Design"
    MergedPineryLimsID = "Merged Pinery Lims ID"
    PineryLimsID = "Pinery Lims ID"
    Project = "Project"
    Reference = "Reference"
    Run = "Run Alias"
    TissueOrigin = "Tissue Origin"
    TissueType = "Tissue Type"
    WorkflowRunSWID = "Workflow Run SWID"


class AnalysisMrdColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    SampleName = "sampleName"
    SampleCoverage = "sample_coverage"
    MedianVAF = "median_vaf"
    SampleSNPs = "sample_candidate_SNPs"
    SitesDetected = "sites_detected"
    MeanNoise = "mean_noise"
    DetectionRate = "detection_rate"
    TumourFractionEstimate = "tumour_fraction_estimate"
    TumourFractionAdjusted = "tumour_fraction_adjusted"
    ZScore = "zscore"
    PValue = "pvalue"
    DatasetDetectionCutoff = "dataset_detection_cutoff"
    FalsePositiveRate = "false_positive_rate"
    CancerDetected = "cancer_detected"


class AnalysisPurpleColumn(BaseColumn):
    Donor = "donor"
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    Score = "score"
    Purity = "purity"
    MinPurity = "minPurity"
    MaxPurity = "maxPurity"
    Ploidy = "ploidy"
    MinPloidy = "minPloidy"
    MaxPloidy = "maxPloidy"
    DiploidProportion = "diploidProportion"
    MinDiploidProportion = "minDiploidProportion"
    MaxDiploidProportion = "maxDiploidProportion"
    PolyclonalProportion = "polyclonalProportion"
    Status = "status"
    WholeGenomeDuplication = "wholeGenomeDuplication"
    msStatus = "msStatus"
    Tml = "tml"
    TmlStatus = "tmlStatus"
    TmbPerMb = "tmbPerMb"
    TmbStatus = "tmbStatus"
    Pga = "PGA"
    QCStatus = "QCStatus"
    CopyNumberSegments = "CopyNumberSegments"
    Contamination = "Contamination"


class AnalysisDellyColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    NumCalls = "num_calls"
    NumPASS = "num_PASS"
    NumBND = "num_BND"
    NumDEL = "num_DEL"
    NumDUP = "num_DUP"
    NumINS = "num_INS"
    NumINV = "num_INV"


class AnalysisMutect2Column(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    NumCalls = "num_calls"
    NumPASS = "num_PASS"
    # the following stats are just for PASS calls
    PASSNumSNPs = "num_SNPs"
    PASSNumMultiSNPs = "num_multi_SNPs"
    PASSNumIndels = "num_indels"
    TITVRatio = "titv_ratio"
    PASSNumMNPs = "num_MNPs"
    PctTI = "pct_ti"
    PctTV = "pct_tv"


class AnalysisRSEMColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    TotalNumTranscripts = "total"
    PctNonZeroTranscripts = "pct_non_zero"
    Q0 = "Q0"
    Q0_05 = "Q0.05"
    Q0_1 = "Q0.1"
    Q0_25 = "Q0.25"
    Q0_5 = "Q0.5"
    Q0_75 = "Q0.75"
    Q0_9 = "Q0.9"
    Q0_95 = "Q0.95"
    Q1 = "Q1"


class AnalysisSequenzaAlternativeSolutionsColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    Index = "index"
    Cellularity = "cellularity"
    Ploidy = "ploidy"
    SLPP = "SLPP"
    Gamma = "gamma"


class AnalysisSequenzaGamma500FGAColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    FGA = "fga"
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID


class AnalysisStarFusionColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    WorkflowRunSWID = ColumnNames.WorkflowRunSWID
    NumRecords = "num_records"


class BaseBamQcColumn3AndUp(BaseColumn):
    """
    Shared column names for BamQC version >= 3
    """

    AlignedReference = "alignment reference"
    AverageReadLength = "average read length"
    BasesMapped = "bases mapped"
    Coverage = "coverage"
    CoverageDeduplicated = "coverage deduplicated"
    DeletedBases = "deleted bases"
    FileSWID = ColumnNames.FileSWID
    HardClipBases = "hard clip bases"
    InsertMax = "insert max"
    InsertMean = "insert size average"
    InsertMedian = "insert size median"
    InsertSD = "insert size standard deviation"
    InsertCount = "inserted bases"
    Insert10Percentile = "insert size 10 percentile"
    Insert90Percentile = "insert size 90 percentile"
    Instrument = "instrument"
    Library = "library"
    MappedReads = "mapped reads"
    MarkDuplicates_ESTIMATED_LIBRARY_SIZE = (
        "mark duplicates_ESTIMATED_LIBRARY_SIZE"
    )
    MarkDuplicates_LIBRARY = "mark duplicates_LIBRARY"
    MarkDuplicates_PERCENT_DUPLICATION = "mark duplicates_PERCENT_DUPLICATION"
    MarkDuplicates_READ_PAIR_DUPLICATES = "mark duplicates_READ_PAIR_DUPLICATES"
    MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES = (
        "mark duplicates_READ_PAIR_OPTICAL_DUPLICATES"
    )
    MarkDuplicates_READ_PAIRS_EXAMINED = "mark duplicates_READ_PAIRS_EXAMINED"
    MarkDuplicates_UNMAPPED_READS = "mark duplicates_UNMAPPED_READS"
    MarkDuplicates_UNPAIRED_READ_DUPLICATES = (
        "mark duplicates_UNPAIRED_READ_DUPLICATES"
    )
    MarkDuplicates_UNPAIRED_READS_EXAMINED = (
        "mark duplicates_UNPAIRED_READS_EXAMINED"
    )
    MismatchBases = "mismatched bases"
    NonPrimaryReads = "non primary reads"
    NumberOfTargets = "number of targets"
    PackageVersion = "package version"
    PairedEnd = "paired end"
    PairedReads = "paired reads"
    PairsMappedAbnormallyFar = "pairsMappedAbnormallyFar"
    PairsMappedToDifferentChr = "pairsMappedToDifferentChr"
    ProperlyPairedReads = "properly paired reads"
    QualityCutoff = "qual cut"
    QualityFailedReads = "qual fail reads"
    Read1AverageLength = "read 1 average length"
    Read2AverageLength = "read 2 average length"
    ReadsMappedAndPaired = "reads mapped and paired"
    ReadsOnTarget = "reads on target"
    ReadsPerStartPoint = "reads per start point"
    ReadsMissingMDTags = "readsMissingMDtags"
    Reference = ColumnNames.Reference
    Sample = "sample"
    SampleLevel = "sample level"
    SoftClipBases = "soft clip bases"
    TargetFile = "target file"
    TotalBasesOnTarget = "total bases on target"
    TotalClusters = "total clusters"
    TotalReads = "total reads"
    TotalTargetSize = "total target size"
    UnmappedReads = "unmapped reads"
    WorkflowVersion = "workflow version"


class BaseBamQc3Column(BaseBamQcColumn3AndUp):
    """
    The column names of a BamQC3 record.
    """

    SampleTotal = "sample total"


class BamQc3Column(BaseBamQc3Column):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    Run = ColumnNames.Run


class BamQc3IntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Barcodes = ColumnNames.Barcodes
    Count = "count"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    Name = "name"
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    Value = "value"


class BamQc3MergedColumn(BaseBamQc3Column):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Project = ColumnNames.Project
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class BamQc3MergedIntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Count = "count"
    Donor = ColumnNames.Donor
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Name = "name"
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    Value = "value"


class BaseBamQc4Column(BaseBamQcColumn3AndUp):
    """
    The column names of a BamQC4 record.
    """

    CoverageMedian = "coverage median"
    CoverageMedian10Percentile = "coverage median 10 percentile"
    CoverageMedian90Percentile = "coverage median 90 percentile"
    DownsampledTotal = "downsampled total"
    LowQualityReadsMeta = "low-quality reads meta"
    NonPrimaryReadsMeta = "non-primary reads meta"
    TotalInputReadsMeta = "total input reads meta"
    UnmappedReadsMeta = "unmapped reads meta"


class BamQc4Column(BaseBamQc4Column):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class BamQc4MergedColumn(BaseBamQc4Column):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class BamQc4IntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Barcodes = ColumnNames.Barcodes
    Count = "count"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    Name = "name"
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    Value = "value"


class BamQc4MergedIntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Count = "count"
    Donor = ColumnNames.Donor
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Name = "name"
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    Value = "value"


class BaseBamQcLiteColumn(BaseColumn):
    """
    Shared column names for BamQCLite
    """

    AlignedReference = "alignment reference"
    AverageReadLength = "average read length"
    BasesMapped = "bases mapped"
    Coverage = "coverage"
    CoverageDeduplicated = "coverage deduplicated"
    DeletedBases = "deleted bases"
    FileSWID = ColumnNames.FileSWID
    DownsampledTotal = "downsampled total"
    HardClipBases = "hard clip bases"
    InsertMax = "insert max"
    InsertMean = "insert size average"
    InsertMedian = "insert size median"
    InsertSD = "insert size standard deviation"
    InsertCount = "inserted bases"
    Insert10Percentile = "insert size 10 percentile"
    Insert90Percentile = "insert size 90 percentile"
    CoverageMedian = "coverage median"
    CoverageMedian10Percentile = "coverage median 10 percentile"
    CoverageMedian90Percentile = "coverage median 90 percentile"
    Instrument = "instrument"
    Library = "library"
    MappedReads = "mapped reads"
    MarkDuplicates_PERCENT_DUPLICATION = "mark duplicates_PERCENT_DUPLICATION"
    MarkDuplicates_READ_PAIR_DUPLICATES = "mark duplicates_READ_PAIR_DUPLICATES"
    MarkDuplicates_READ_PAIRS_EXAMINED = "mark duplicates_READ_PAIRS_EXAMINED"
    MarkDuplicates_UNPAIRED_READ_DUPLICATES = (
        "mark duplicates_UNPAIRED_READ_DUPLICATES"
    )
    MarkDuplicates_UNPAIRED_READS_EXAMINED = (
        "mark duplicates_UNPAIRED_READS_EXAMINED"
    )
    MismatchBases = "mismatched bases"
    NonPrimaryReads = "non primary reads"
    NumberOfTargets = "number of targets"
    PackageVersion = "package version"
    PairedEnd = "paired end"
    PairedReads = "paired reads"
    PairsMappedAbnormallyFar = "pairsMappedAbnormallyFar"
    PairsMappedToDifferentChr = "pairsMappedToDifferentChr"
    ProperlyPairedReads = "properly paired reads"
    Read1AverageLength = "read 1 average length"
    Read2AverageLength = "read 2 average length"
    ReadsMappedAndPaired = "reads mapped and paired"
    ReadsOnTarget = "reads on target"
    ReadsPerStartPoint = "reads per start point"
    ReadsMissingMDTags = "readsMissingMDtags"
    Reference = ColumnNames.Reference
    Sample = "sample"
    SoftClipBases = "soft clip bases"
    TargetFile = "target file"
    TotalBasesOnTarget = "total bases on target"
    TotalClusters = "total clusters"
    TotalReads = "total reads"
    TotalTargetSize = "total target size"
    UnmappedReads = "unmapped reads"
    WorkflowVersion = "workflow version"


class BamQcLiteColumn(BaseBamQcLiteColumn):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class BamQcLiteMergedColumn(BaseBamQcLiteColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class BamQcLiteIntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Barcodes = ColumnNames.Barcodes
    Count = "count"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    Name = "name"
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    Value = "value"


class BamQcLiteMergedIntHistColumn(BaseColumn):
    """
    The histograms that have counts of integers (such as coverage, insert size)
    """

    Count = "count"
    Donor = ColumnNames.Donor
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    Name = "name"
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    Value = "value"


class Bcl2BarcodeColumn(BaseColumn):
    """
    The column names of a bcl2barcode record.
    """

    Barcodes = ColumnNames.Barcodes
    Count = "count"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class Bcl2BarcodeRunSummaryColumn(BaseColumn):
    """
    The column names of a bcl2barcode run summary.
    """

    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run
    TotalClusters = "total clusters"


class Bcl2BarcodeCallerKnownColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Count = "count"
    LibraryAlias = "library alias"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class Bcl2BarcodeCallerUnknownColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Count = "count"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class Bcl2BarcodeCallerSummaryColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run
    TotalClusters = "total clusters"
    ExcludedClusters = "excluded clusters"
    KnownClusters = "known clusters"
    UnknownClusters = "unknown clusters"


class Bcl2FastqKnownColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    FileSWID = "StatsFileSWID"
    FlowCell = "FlowCell"
    Index1 = "Index1"
    Index1Length = "Index1Length"
    Index2Length = "Index2Length"
    Index2 = "Index2"
    LaneClusterPF = "LaneClusterPF"
    LaneClusterRaw = "LaneClusterRaw"
    Lane = ColumnNames.Lane
    LaneYield = "LaneYield"
    QualityScoreSum = "QualityScoreSum"
    ReadNumber = "ReadNumber"
    Read1Length = "Read1Length"
    Read2Length = "Read2Length"
    ReadCount = "ReadCount"
    ReadYield = "ReadYield"
    ReadYieldQ30 = "ReadYieldQ30"
    Run = ColumnNames.Run
    RunNumber = "RunNumber"
    SampleID = "SampleID"
    SampleYield = "SampleYield"
    TimeStamp = "Timestamp"
    TrimmedBases = "TrimmedBases"

    # NaN status of SampleID and index did not match
    ETLValidateIndexSampleID = "ETLValidateIndexSampleID"


class Bcl2FastqUnknownColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Count = "Count"
    FileSWID = Bcl2FastqKnownColumn.FileSWID
    Lane = ColumnNames.Lane
    Index1 = Bcl2FastqKnownColumn.Index1
    Index2 = Bcl2FastqKnownColumn.Index2
    Run = ColumnNames.Run
    TimeStamp = Bcl2FastqKnownColumn.TimeStamp


class BaseCalculateContaminationColumn(BaseColumn):
    Contamination = "contamination"
    Error = "error"
    Sample = "sample"


class BiomodalQcMergedColumn(BaseColumn):
    DuplicationRate = "duplication rate"
    LambdaMethylationModC = "lambda methylation of modified c"
    PUC19MethylationModC = "puc19 methylation of modified C"
    Sq2hmcMethylation5mC = "sq2hmc methylation of 5mC"
    Sq2hmcMethylation5hmC = "sq2hmc methylation of 5hmC"
    TotalClusters = "total clusters (passed filter)"
    FileSWID = ColumnNames.FileSWID
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class BiomodalQcColumn(BaseColumn):
    DuplicationRate = "duplication rate"
    LambdaMethylationModC = "lambda methylation of modified c"
    PUC19MethylationModC = "puc19 methylation of modified C"
    Sq2hmcMethylation5mC = "sq2hmc methylation of 5mC"
    Sq2hmcMethylation5hmC = "sq2hmc methylation of 5hmC"
    TotalClusters = "total clusters (passed filter)"
    Donor = ColumnNames.Donor
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class CalculateContaminationCallReadyColumn(BaseCalculateContaminationColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    FileSWID = ColumnNames.FileSWID


class CalculateContaminationLaneLevelColumn(BaseCalculateContaminationColumn):
    Donor = ColumnNames.Donor
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class CfMeDipQcColumn(BaseColumn):
    ATDropout = "AT Dropout"
    AccumulationLevel = "Accumulation Level"
    Barcodes = ColumnNames.Barcodes
    CInRegions = "Cs in Regions"
    Category = "Category"
    CpGInRegions = "CpGs in Regions"
    CpGsInReference = "CpGs in Reference"
    CsInReference = "Cs in Reference"
    EstimatedLibrarySize = "Estimated Library Size"
    FileSWID = ColumnNames.FileSWID
    GCDropout = "GC Dropout"
    GInRegions = "Gs in Regions"
    GsInReference = "Gs in Reference"
    Lane = ColumnNames.Lane
    MeanReadLength = "Mead Read Length"
    MethylationBeta = "Methylation beta"
    NormalizedCoverageQ1 = "Normalized Coverage 1st Quintile"
    NormalizedCoverageQ2 = "Normalized Coverage 2nd Quintile"
    NormalizedCoverageQ3 = "Normalized Coverage 3rd Quintile"
    NormalizedCoverageQ4 = "Normalized Coverage 4th Quintile"
    NormalizedCoverageQ5 = "Normalized Coverage 5th Quintile"
    NumAlignedReads = "Number of Aligned Reads"
    NumAthalianaMethylReads = (
        "Number of Reads Aligning to Methylated A. thaliana F19K16"
    )
    NumAthalianaUnmethylReads = (
        "Number of Reads Aligning to Unmethylated A. thaliana F24B22"
    )
    NumBadCycles = "Number of Bad Cycles"
    NumDuplicatePairs = "Number of Duplicate Pairs"
    NumNonPrimaryReads = "Number of Non-primary Reads"
    NumNonPrimaryReadsExamined = "Number of Non-primary Reads Examined"
    NumOpticalDuplicatePairs = "Number of Optical Duplicate Pairs"
    NumReadsAfterDuplicateMarking = (
        "Number of Reads in the duplicate marked BAM file"
    )
    NumReadsAlignedInPairs = "Number of Reads in Aligned Pairs"
    NumReadsWithCpG = "Number of reads with CpGs"
    NumReadsWithoutCpG = "Number of reads without CpGs"
    NumUnmappedReads = "Number of Unmapped Reads"
    NumUnmappedReadsAfterDuplicateMarking = (
        "Number of Unmapped Reads in the duplicate marked BAM file"
    )
    NumUnpairedDuplicateReads = "Number of Unpaired Duplicate Reads"
    NumUnpairedReadsExamined = "Number of Unpaired Reads Examined"
    NumWindowsWith0Reads = "Number of Windows with 0 Reads"
    NumWindowsWith100Reads = "Number of Windows with 100 Reads"
    NumWindowsWith10Reads = "Number of Windows with 10 Reads"
    NumWindowsWith1Reads = "Number of Windows with 1 Reads"
    NumWindowsWith50Reads = "Number of Windows with 50 Reads"
    ObservedToExpectedEnrichment = (
        "Observed to Expected CpGs Ratio in Regions vs Reference"
    )
    ObservedToExpectedInReference = (
        "Observed to Expected CpGs Ratio in Reference"
    )
    ObservedToExpectedInRegions = "Observed to Expected CpGs Ratio in Regions"
    PassedFilterAlignedBases = "Passed Filter Aligned Bases"
    PassedFilterAlignedReads = "Passed Filter Aligned Reads"
    PassedFilterHQAlignedBases = "Passed Filter HQ Aligned Bases"
    PassedFilterHQAlignedQ20Bases = "Passed Filter HQ Aligned Q20 Bases"
    PassedFilterHQAlignedReads = "Passed Filter HQ Aligned Reads"
    PassedFilterHQErrorFraction = "Passed Filter HQ Error Fraction"
    PassedFilterHQMedianMismatches = "Passed Filter HQ Median Mismatches"
    PassedFilterIndelFraction = "Passed Filter Indel Fraction"
    PassedFilterMismatchFraction = "Passed Filter Mismatched Fraction"
    PassedFilterNoiseReads = "Passed Filter Noise Reads"
    PassedFilterReads = "Passed Filter Reads"
    PercentChimeras = "Percentage of Chimeras"
    PercentDuplication = "Percent Duplication"
    PercentPassedFilterAlignedReads = "Percent Passed Filter Aligned Reads"
    PercentPassedFilterReads = "Percent Passed Filter Reads"
    PercentReadsAlignedInPairs = "Percentage of Reads Aligned in Pairs"
    PercentageAthaliana = "Percentage of Reads Mapping to A. thaliana"
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    RelativeCpGFreqInReference = "Relative CpG Frequency in Reference"
    RelativeCpGFreqInRegions = "Relative CpG Frequency in Regions"
    RelativeCpGFrequencyEnrichment = (
        "Relative CpG Frequency in Regions vs Reference"
    )
    Run = ColumnNames.Run
    SaturationAnalysisDoubledPearsonCorrelation = (
        "Best Pearson Correlation in Doubled Saturation Curve"
    )
    SaturationAnalysisDoubledReads = (
        "Number of Reads used in Doubled Saturation Curve"
    )
    SaturationAnalysisTruePearsonCorrelation = (
        "Best Pearson Correlation in True Saturation Curve"
    )
    SaturationAnalysisTrueReads = (
        "Number of Reads used in True Saturation Curve"
    )
    StrandBalance = "Strange Balance"
    TotalReads = "Total Reads"
    TotalClusters = "Total Clusters"
    WindowSize = "Window Size"


class BedFormatColumn(BaseColumn):
    """
    The official bed format: https://genome.ucsc.edu/FAQ/FAQformat.html#format1
    The format does not have column names, so the order of the below values must
    not be changed. The first three columns are mandatory
    """

    Chrom = "chrom"
    ChromStart = "chromStart"
    ChromEnd = "chromEnd"
    Name = "name"
    Score = "score"
    Strand = "strand"
    ThickStart = "thickStart"
    ThickEnd = "thickEnd"
    ItemRgb = "itemRgb"
    BlockCount = "blockCount"
    BlockSize = "blockSize"
    BlockStarts = "blockStarts"


class BedToolsCoverageHistColumn(BedFormatColumn):
    Barcodes = ColumnNames.Barcodes
    BasesAtCoverage = "basesAtCoverage"
    Coverage = "coverage"
    FeatureLength = "featureLength"
    FractionAtCoverage = "fractionAtCoverage"
    Lane = ColumnNames.Lane
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class BedToolsGenomeCovColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    BasesAtCoverage = "basesAtCoverage"
    Chrom = "chrom"
    Coverage = "coverage"
    ChromLength = "chromLength"
    FractionAtCoverage = "fractionAtCoverage"
    Lane = ColumnNames.Lane
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class BedToolsGenomeCovCalculationsColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Coverage10Percentile = "Coverage 10 Percentile"
    Coverage90Percentile = "Coverage 90 Percentile"
    MeanCoverage = "Mean Coverage"
    MedianCoverage = "Median Coverage"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    CoverageUniformity = "Coverage Uniformity"
    Run = ColumnNames.Run
    PineryLimsID = ColumnNames.PineryLimsID


class BedToolsGenomeCovCoveragePercentileColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Coverage = "Coverage"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    PercentGenomeCovered = "Percent Genome Covered"
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class BwaMemCutAdaptColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    TotalReadPairsProcessed = "Total read pairs processed"
    Read1WithAdapter = "Read 1 with adapter"
    Read1WithAdapterPercentage = "Read 1 with adapter percentage"
    Read2WithAdapter = "Read 2 with adapter"
    Read2WithAdapterPercentage = "Read 2 with adapter percentage"
    PairsThatWereTooShort = "Pairs that were too short"
    PairsThatWereTooShortPercentage = "Pairs that were too short percentage"
    PairsWrittenPassingFilters = "Pairs written (passing filters)"
    PairsWrittenPassingFiltersPercentage = (
        "Pairs written (passing filters) percentage"
    )
    TotalBasepairsProcessed = "Total basepairs processed"
    TotalBasepairsProcessedRead1 = "Total basepairs processed Read 1"
    TotalBasepairsProcessedRead2 = "Total basepairs processed Read 2"
    QualityTrimmed = "Quality-trimmed"
    QualityTrimmedPercentage = "Quality-trimmed percentage"
    QualityTrimmedRead1 = "Quality-trimmed Read 1"
    QualityTrimmedRead2 = "Quality-trimmed Read 2"
    TotalWrittenFiltered = "Total written (filtered)"
    TotalWrittenFilteredPercentage = "Total written (filtered) percentage"
    TotalWrittenFilteredRead1 = "Total written (filtered) Read 1"
    TotalWrittenFilteredRead2 = "Total written (filtered) Read 2"


class BedToolsGenomeCovPerBaseColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Chrom = "chrom"
    Coverage = "coverage"
    Lane = ColumnNames.Lane
    Position = "position"
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class CrosscheckFingerprintsColumn(BaseColumn):
    BarcodeLeft = "LEFT_MOLECULAR_BARCODE_SEQUENCE"
    BarcodeRight = "RIGHT_MOLECULAR_BARCODE_SEQUENCE"
    DataType = "DATA_TYPE"
    FileLeft = "LEFT_FILE"
    FileRight = "RIGHT_FILE"
    FileSWID = ColumnNames.FileSWID
    GroupValueLeft = "LEFT_GROUP_VALUE"
    GroupValueRight = "RIGHT_GROUP_VALUE"
    LaneLeft = "LEFT_LANE"
    LaneRight = "RIGHT_LANE"
    LibraryLeft = "LEFT_LIBRARY"
    LibraryRight = "RIGHT_LIBRARY"
    LODScore = "LOD_SCORE"
    LODScoreTumorNormal = "LOD_SCORE_TUMOR_NORMAL"
    LODScoreNormalTumor = "LOD_SCORE_NORMAL_TUMOR"
    Result = "RESULT"
    RunLeft = "LEFT_RUN_BARCODE"
    RunRight = "RIGHT_RUN_BARCODE"
    SampleLeft = "LEFT_SAMPLE"
    SampleRight = "RIGHT_SAMPLE"


class CrosscheckFingerprintsCallSwapColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    QueryLibrary = "QUERY_LIBRARY"
    QueryBarcode = "QUERY_BARCODE"
    QueryLane = "QUERY_LANE"
    QueryRun = "QUERY_RUN"
    MatchLibrary = "MATCH_LIBRARY"
    MatchBarcode = "MATCH_BARCODE"
    MatchLane = "MATCH_LANE"
    MatchRun = "MATCH_RUN"
    LODScore = "LOD_SCORE"
    ClosestLibrariesCount = "CLOSEST_LIBRARIES_COUNT"
    SameIdentity = "SAME_IDENTITY"


class CrosscheckFingerprintCallerCallsColumn(BaseColumn):
    Barcode = "barcode"
    Batches = "batches"
    Donor = "donor"
    ExternalDonor = "external_donor_id"
    FileSWID = ColumnNames.FileSWID
    Grouping = "grouping"
    GroupingName = "grouping_name"
    Lane = "lane"
    LibraryDesign = "library_design"
    LibraryName = "library_name"
    PineryLimsID = "lims_id"
    Project = "project"
    Run = "run"
    SwapCall = "swap_call"
    TissueOrigin = "tissue_origin"
    TissueType = "tissue_type"


class CrosscheckFingerprintCallerDetailedColumn(BaseColumn):
    Barcode = "barcode"
    BarcodeMatch = "barcode_match"
    Batches = "batches"
    BatchesMatched = "batches_match"
    Donor = "donor"
    DonorMatch = "donor_match"
    ExternalDonor = "external_donor_id"
    ExternalDonorMatch = "external_donor_id_match"
    FileSWID = ColumnNames.FileSWID
    Grouping = "grouping"
    GroupingName = "grouping_name"
    Lane = "lane"
    LaneMatch = "lane_match"
    LibraryDesign = "library_design"
    LibraryDesignMatch = "library_design_match"
    LibraryName = "library_name"
    LibraryNameMatch = "library_name_match"
    LODScore = "LOD_SCORE"
    MatchCalled = "match_called"
    OverlapBatch = "overlap_batch"
    PairwiseSwap = "pairwise_swap"
    PineryLimsID = "lims_id"
    PineryLimsIDMatch = "lims_id_match"
    Project = "project"
    ProjectMatch = "project_match"
    Run = "run"
    RunMatch = "run_match"
    SameBatch = "same_batch"
    SwapCall = "swap_call"
    TissueOrigin = "tissue_origin"
    TissueOriginMatch = "tissue_origin_match"
    TissueType = "tissue_type"
    TissueTypeMatch = "tissue_type_match"


class DnaSeqQCColumn(BamQc4Column):
    pass


class EmSeqMethylationColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    FileSWID = ColumnNames.FileSWID
    Genome = "Genome"
    Lambda = "Lambda"
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Puc19 = "pUC19"
    Run = ColumnNames.Run


# Can't use BamQc4 class because reference wasn't included in emseqqc
class EmSeqBamQcColumn(BaseColumn):
    AlignedReference = "alignment reference"
    AverageReadLength = "average read length"
    BasesMapped = "bases mapped"
    Coverage = "coverage"
    CoverageDeduplicated = "coverage deduplicated"
    CoverageMedian = "coverage median"
    CoverageMedian10Percentile = "coverage median 10 percentile"
    CoverageMedian90Percentile = "coverage median 90 percentile"
    DeletedBases = "deleted bases"
    DownsampledTotal = "downsampled total"
    FileSWID = ColumnNames.FileSWID
    HardClipBases = "hard clip bases"
    InsertMax = "insert max"
    InsertMean = "insert size average"
    InsertMedian = "insert size median"
    InsertSD = "insert size standard deviation"
    InsertCount = "inserted bases"
    Insert10Percentile = "insert size 10 percentile"
    Insert90Percentile = "insert size 90 percentile"
    Instrument = "instrument"
    Library = "library"
    LowQualityReadsMeta = "low-quality reads meta"
    MappedReads = "mapped reads"
    MarkDuplicates_ESTIMATED_LIBRARY_SIZE = (
        "mark duplicates_ESTIMATED_LIBRARY_SIZE"
    )
    MarkDuplicates_LIBRARY = "mark duplicates_LIBRARY"
    MarkDuplicates_PERCENT_DUPLICATION = "mark duplicates_PERCENT_DUPLICATION"
    MarkDuplicates_READ_PAIR_DUPLICATES = "mark duplicates_READ_PAIR_DUPLICATES"
    MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES = (
        "mark duplicates_READ_PAIR_OPTICAL_DUPLICATES"
    )
    MarkDuplicates_READ_PAIRS_EXAMINED = "mark duplicates_READ_PAIRS_EXAMINED"
    MarkDuplicates_UNMAPPED_READS = "mark duplicates_UNMAPPED_READS"
    MarkDuplicates_UNPAIRED_READ_DUPLICATES = (
        "mark duplicates_UNPAIRED_READ_DUPLICATES"
    )
    MarkDuplicates_UNPAIRED_READS_EXAMINED = (
        "mark duplicates_UNPAIRED_READS_EXAMINED"
    )
    MismatchBases = "mismatched bases"
    NonPrimaryReads = "non primary reads"
    NonPrimaryReadsMeta = "non-primary reads meta"
    NumberOfTargets = "number of targets"
    PackageVersion = "package version"
    PairedEnd = "paired end"
    PairedReads = "paired reads"
    PairsMappedAbnormallyFar = "pairsMappedAbnormallyFar"
    PairsMappedToDifferentChr = "pairsMappedToDifferentChr"
    ProperlyPairedReads = "properly paired reads"
    QualityCutoff = "qual cut"
    QualityFailedReads = "qual fail reads"
    Read1AverageLength = "read 1 average length"
    Read2AverageLength = "read 2 average length"
    ReadsMappedAndPaired = "reads mapped and paired"
    ReadsOnTarget = "reads on target"
    ReadsPerStartPoint = "reads per start point"
    ReadsMissingMDTags = "readsMissingMDtags"
    Sample = "sample"
    SampleLevel = "sample level"
    SoftClipBases = "soft clip bases"
    TargetFile = "target file"
    TotalBasesOnTarget = "total bases on target"
    TotalClusters = "total clusters"
    TotalInputReadsMeta = "total input reads meta"
    TotalReads = "total reads"
    TotalTargetSize = "total target size"
    UnmappedReads = "unmapped reads"
    UnmappedReadsMeta = "unmapped reads meta"
    WorkflowVersion = "workflow version"
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class FastqcColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Encoding = "Encoding"
    FileSWID = "FileSWID"
    FileType = "File type"
    FilteredSequences = "Filtered Sequences"
    Lane = ColumnNames.Lane
    PercentGC = "%GC"
    PineryLimsID = ColumnNames.PineryLimsID
    ReadNumber = "Read Number"
    Run = ColumnNames.Run
    SequenceLength = "Sequence length"
    # SequenceLength is a range in rare circumstances
    SequenceLengthMax = "Sequence length max"
    SequencesFlaggedPoorQuality = "Sequences flagged as poor quality"
    StatusBasicStatistics = "Status Basic Statistics"
    StatusKmerContent = "Status Kmer Content"
    StatusOverrepresentedSequences = "Status Overrepresented sequences"
    StatusPerBaseGCContent = "Status Per base GC content"
    StatusPerBaseNContent = "Status Per base N content"
    StatusPerBaseSequenceContent = "Status Per base sequence content"
    StatusPerBaseSequenceQuality = "Status Per base sequence quality"
    StatusPerSequenceGCContent = "Status Per sequence GC content"
    StatusPerSequenceQualityScores = "Status Per sequence quality scores"
    StatusSequenceDuplicationLevels = "Status Sequence Duplication Levels"
    StatusSequenceLengthDistribution = "Status Sequence Length Distribution"
    TotalSequences = "Total Sequences"
    Version = "version"


class HsMetricsColumn(BaseColumn):
    AtDropout = "AT_DROPOUT"
    BaitdesignEfficiency = "BAIT_DESIGN_EFFICIENCY"
    BaitSet = "BAIT_SET"
    BaitTerritory = "BAIT_TERRITORY"
    Donor = ColumnNames.Donor
    FileSWID = ColumnNames.FileSWID
    Fold80BasePenalty = "FOLD_80_BASE_PENALTY"
    FoldEnrichment = "FOLD_ENRICHMENT"
    GCDropout = "GC_DROPOUT"
    GenomeSize = "GENOME_SIZE"
    GroupID = ColumnNames.GroupID
    HetSnpQ = "HET_SNP_Q"
    HetSnpSensitivity = "HET_SNP_SENSITIVITY"
    HsLibrarySize = "HS_LIBRARY_SIZE"
    HsPenalty100x = "HS_PENALTY_100X"
    HsPenalty10x = "HS_PENALTY_10X"
    HsPenalty20x = "HS_PENALTY_20X"
    HsPenalty30x = "HS_PENALTY_30X"
    HsPenalty40x = "HS_PENALTY_40X"
    HsPenalty50x = "HS_PENALTY_50X"
    Library = "LIBRARY"
    LibraryDesign = ColumnNames.LibraryDesign
    MaxTargetCoverage = "MAX_TARGET_COVERAGE"
    MeanBaitCoverage = "MEAN_BAIT_COVERAGE"
    MeanTargetCoverage = "MEAN_TARGET_COVERAGE"
    MedianTargetCoverage = "MEDIAN_TARGET_COVERAGE"
    NearBaitBases = "NEAR_BAIT_BASES"
    OffBaitBases = "OFF_BAIT_BASES"
    OnBaitBases = "ON_BAIT_BASES"
    OnBaitVsSelected = "ON_BAIT_VS_SELECTED"
    OnTargetBases = "ON_TARGET_BASES"
    PctExcAdapter = "PCT_EXC_ADAPTER"
    PctExcBaseq = "PCT_EXC_BASEQ"
    PctExcDupe = "PCT_EXC_DUPE"
    PctExcMapq = "PCT_EXC_MAPQ"
    PctExcOffTarget = "PCT_EXC_OFF_TARGET"
    PctExcOverlap = "PCT_EXC_OVERLAP"
    PctOffBait = "PCT_OFF_BAIT"
    PctPfReads = "PCT_PF_READS"
    PctPfUqReads = "PCT_PF_UQ_READS"
    PctPfUqReadsAligned = "PCT_PF_UQ_READS_ALIGNED"
    PctSelectedBases = "PCT_SELECTED_BASES"
    PctTargetBases100x = "PCT_TARGET_BASES_100X"
    PctTargetBases10x = "PCT_TARGET_BASES_10X"
    PctTargetBases1x = "PCT_TARGET_BASES_1X"
    PctTargetBases20x = "PCT_TARGET_BASES_20X"
    PctTargetBases2x = "PCT_TARGET_BASES_2X"
    PctTargetBases30x = "PCT_TARGET_BASES_30X"
    PctTargetBases40x = "PCT_TARGET_BASES_40X"
    PctTargetBases50x = "PCT_TARGET_BASES_50X"
    PctUsableBasesOnBait = "PCT_USABLE_BASES_ON_BAIT"
    PctUsableBasesOnTarget = "PCT_USABLE_BASES_ON_TARGET"
    PfBases = "PF_BASES"
    PfBasesAligned = "PF_BASES_ALIGNED"
    PfReads = "PF_READS"
    PfUniqueReads = "PF_UNIQUE_READS"
    PfUqBasesAligned = "PF_UQ_BASES_ALIGNED"
    PfUqReadsAligned = "PF_UQ_READS_ALIGNED"
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    ReadGroup = "READ_GROUP"
    Reference = ColumnNames.Reference
    Sample = "SAMPLE"
    TargetTerritory = "TARGET_TERRITORY"
    TotalReads = "TOTAL_READS"
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    ZeroCvgTargetsPct = "ZERO_CVG_TARGETS_PCT"


class HsMetricsConsensusCruncherColumn(HsMetricsColumn):
    MinTargetCoverage = "MIN_TARGET_COVERAGE"


class InsertSizeMetricsColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    Run = ColumnNames.Run
    Reference = ColumnNames.Reference
    FileSWID = ColumnNames.FileSWID
    MedianInsertSize = "MEDIAN_INSERT_SIZE"
    ModeInsertSize = "MODE_INSERT_SIZE"
    MedianAbsoluteDeviation = "MEDIAN_ABSOLUTE_DEVIATION"
    MinInsertSize = "MIN_INSERT_SIZE"
    MaxInsertSize = "MAX_INSERT_SIZE"
    MeanInsertSize = "MEAN_INSERT_SIZE"
    StandardDeviation = "STANDARD_DEVIATION"
    ReadPairs = "READ_PAIRS"
    PairOrientation = "PAIR_ORIENTATION"
    PineryLimsID = ColumnNames.PineryLimsID
    WidthOf10Percent = "WIDTH_OF_10_PERCENT"
    WidthOf20Percent = "WIDTH_OF_20_PERCENT"
    WidthOf30Percent = "WIDTH_OF_30_PERCENT"
    WidthOf40Percent = "WIDTH_OF_40_PERCENT"
    WidthOf50Percent = "WIDTH_OF_50_PERCENT"
    WidthOf60Percent = "WIDTH_OF_60_PERCENT"
    WidthOf70Percent = "WIDTH_OF_70_PERCENT"
    WidthOf80Percent = "WIDTH_OF_80_PERCENT"
    WidthOf90Percent = "WIDTH_OF_90_PERCENT"
    WidthOf95Percent = "WIDTH_OF_95_PERCENT"
    WidthOf99Percent = "WIDTH_OF_99_PERCENT"
    # InsertMedianXXPercentile are added during parsing
    InsertMedian10Percentile = "insert size median 10 percentile"
    InsertMedian90Percentile = "insert size median 90 percentile"
    Sample = "SAMPLE"
    Library = "LIBRARY"
    ReadGroup = "READ_GROUP"


class InsertSizeMetricsHistogramColumn(BaseColumn):
    Count = "count"
    FRCount = "All_Reads.fr_count"
    InsertSize = "insert_size"
    RFCount = "All_Reads.rf_count"
    TandemCount = "All_Reads.tandem_count"


class Kraken2Column(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    # Number of fragments assigned directly to this taxon
    Count = "Count"
    # Number of fragments covered by the clade rooted at this taxon
    CountAtClade = "Count at Clade"
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    # Indented scientific name
    Name = "Name"
    Parent = "Parent"
    # Percentage of fragments covered by the clade rooted at this taxon
    PineryLimsID = ColumnNames.PineryLimsID
    PercentAtClade = "Percent at Clade"
    # A rank code, indicating (U)nclassified, (R)oot, (D)omain, (K)ingdom,
    # (P)hylum, (C)lass, (O)rder, (F)amily, (G)enus, or (S)pecies.
    # Taxa that are not at any of these 10 ranks have a rank code that is,
    # formed by using the rank code of the closest ancestor rank with
    # a number indicating the distance from that rank.  E.g., "G2" is a
    # rank code indicating a taxon is between genus and species and the
    # grandparent taxon is at the genus rank.
    Rank = "Rank"
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    # NCBI taxonomic ID number
    TaxonomicID = "Taxonomic ID"


class BaseIchorCnaColumn(BaseColumn):
    ChrXMedianLogRation = "ChrX median log ratio"
    ChrYCoverageFraction = "ChrY coverage fraction"
    Coverage = "Coverage"
    FractionCnaSubclonal = "Fraction CNA Subclonal"
    FractionGenomeSubclonal = "Fraction Genome Subclonal"
    GCMapCorrectionMAD = "GC-Map correction MAD"
    GammaRateInit = "Gamma Rate Init"
    Gender = "Gender"
    Ploidy = "Ploidy"
    SubcloneFraction = "Subclone Fraction"
    TumorFraction = "Tumor Fraction"


class IchorCnaColumn(BaseIchorCnaColumn):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID


class IchorCnaMergedColumn(BaseIchorCnaColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    FileSWID = ColumnNames.FileSWID


class IchorCna2MainColumn(BaseIchorCnaColumn):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID
    TumorFractionBestSolution = "Tumor Fraction"
    PloidyBestSolution = "Ploidy"


class IchorCna2SolutionColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID
    Init = "init"
    TumorFractionPerSolution = "Tumor Fraction per Solution"
    PloidyPerSolution = "Ploidy per Solution"
    NEst = "n_est"
    PhiEst = "phi_est"
    Bic = "BIC"
    FractionGenomeSubclonalPerSolution = "Frac_genome_subclonal"
    FractionCnaSubclonalPerSolution = "Frac_CNA_subclonal"
    LogLikPerSolution = "loglik"


class IchorCna2BamqcColumn(BaseBamQc4Column):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run
    FileSWID = ColumnNames.FileSWID
    Instrument = "instrument"
    Library = "library"


class IchorCna2MergedMainColumn(BaseIchorCnaColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    FileSWID = ColumnNames.FileSWID
    TumorFractionBestSolution = "Tumor Fraction"
    PloidyBestSolution = "Ploidy"


class IchorCna2MergedSolutionColumn(BaseColumn):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    FileSWID = ColumnNames.FileSWID
    Init = "init"
    TumorFractionPerSolution = "Tumor Fraction per Solution"
    PloidyPerSolution = "Ploidy per Solution"
    NEst = "n_est"
    PhiEst = "phi_est"
    Bic = "BIC"
    FractionGenomeSubclonalPerSolution = "Frac_genome_subclonal"
    FractionCnaSubclonalPerSolution = "Frac_CNA_subclonal"
    LogLikPerSolution = "loglik"


class IchorCna2MergedBamqcColumn(BaseBamQc4Column):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    FileSWID = ColumnNames.FileSWID
    Instrument = "instrument"
    Library = "library"


class MetagenomicReportColumn(BaseColumn):
    AddedReads = "added_reads"
    AssignedReads = "kraken_assigned_reads"
    Barcodes = ColumnNames.Barcodes
    FileSWID = ColumnNames.FileSWID
    Lane = ColumnNames.Lane
    Name = "name"
    NewEstimatedReads = "new_est_reads"
    Run = ColumnNames.Run
    TaxonomyId = "taxonomy_id"
    TaxonomyLevel = "taxonomy_lvl"
    FractionTotalReads = "fraction_total_reads"


class MutetctCallabilityColumn(BaseColumn):
    Callability = "callability"
    Donor = ColumnNames.Donor
    Fail = "fail"
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    NormalMinCoverage = "normal_min_coverage"
    Project = ColumnNames.Project
    Pass = "pass"
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Reference = ColumnNames.Reference
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    TumorMinCoverage = "tumor_min_coverage"


class PurityQcSequenzaColumn(BaseColumn):
    defaultGamma = "default_gamma"
    defaultPurity = "default_purity"
    defaultPloidy = "default_ploidy"
    minPurity = "min_purity"
    maxPurity = "max_purity"
    minPloidy = "min_ploidy"
    maxPloidy = "max_ploidy"
    Donor = "donor"
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class PurityQcPurpleColumn(BaseColumn):
    Purity = "purity"
    Ploidy = "ploidy"
    Donor = "donor"
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType
    NormFactor = "normFactor"
    Score = "score"
    DiploidProportion = "diploidProportion"
    PolyclonalProportion = "polyclonalProportion"
    MinPurity = "minPurity"
    MaxPurity = "maxPurity"
    MinPloidy = "minPloidy"
    MaxPloidy = "maxPloidy"
    MinDiploidProportion = "minDiploidProportion"
    MaxDiploidProportion = "maxDiploidProportion"
    SomaticPenalty = "somaticPenalty"


class BaseRnaSeqQc2Column(BaseColumn):
    AlignedReference = "alignment reference"
    AverageReadLength = "average read length"
    BasesMapped = "bases mapped"
    DeletedBases = "deleted bases"
    FileSWID = ColumnNames.FileSWID
    InsertCount = "inserted bases"
    InsertMax = "insert max"
    InsertMean = "insert size average"
    InsertMedian = "insert size median"
    InsertMedian10Percentile = "insert size median 10 percentile"
    InsertMedian90Percentile = "insert size median 90 percentile"
    InsertSD = "insert size standard deviation"
    MappedReads = "mapped reads"
    MetricsIntronicBases = "INTRONIC_BASES"
    MetricsCorrectStrandReads = "CORRECT_STRAND_READS"
    MetricsIgnoredReads = "IGNORED_READS"
    MetricsIncorrectStrandReads = "INCORRECT_STRAND_READS"
    MetricsIntergenicBases = "INTERGENIC_BASES"
    MetricsMedian5PrimeTo3PrimeBias = "MEDIAN_5PRIME_TO_3PRIME_BIAS"
    MetricsMedian3PrimeBias = "MEDIAN_3PRIME_BIAS"
    MetricsMedian5PrimeBias = "MEDIAN_5PRIME_BIAS"
    MetricsMedianCVCoverage = "MEDIAN_CV_COVERAGE"
    MetricsNumRead1TranscriptStrandReads = "NUM_R1_TRANSCRIPT_STRAND_READS"
    MetricsNumRead2TranscriptStrandReads = "NUM_R2_TRANSCRIPT_STRAND_READS"
    MetricsNumUnexplainedReads = "NUM_UNEXPLAINED_READS"
    MetricsPassedFilterAlignedBases = "PF_ALIGNED_BASES"
    MetricsPassedFilterBases = "PF_BASES"
    MetricsPercentCodingBases = "PCT_CODING_BASES"
    MetricsPercentCorrectStrandReads = "PCT_CORRECT_STRAND_READS"
    MetricsPercentIntergenicBases = "PCT_INTERGENIC_BASES"
    MetricsPercentIntronicBases = "PCT_INTRONIC_BASES"
    MetricsPercentMRnaBases = "PCT_MRNA_BASES"
    MetricsPercentRead1TranscriptStrandReads = "PCT_R1_TRANSCRIPT_STRAND_READS"
    MetricsPercentRead2TranscriptStrandReads = "PCT_R2_TRANSCRIPT_STRAND_READS"
    MetricsPercentRibosomalBases = "PCT_RIBOSOMAL_BASES"
    MetricsPercentUTRBases = "PCT_UTR_BASES"
    MetricsPercentUsableBases = "PCT_USABLE_BASES"
    MetricsRibosomalBases = "RIBOSOMAL_BASES"
    MetricsUTRBases = "UTR_BASES"
    MismatchBases = "mismatched bases"
    NonPrimaryReads = "non primary reads"
    PackageVersion = "package version"
    PairedEnd = "paired end"
    PairedReads = "paired reads"
    PairsMappedAbnormallyFar = "pairsMappedAbnormallyFar"
    PairsMappedToDifferentChr = "pairsMappedToDifferentChr"
    ProperlyPairedReads = "properly paired reads"
    Reference = ColumnNames.Reference
    RRnaContaminationDuplicates = "rrna contamination duplicates"
    RRnaContaminationInTotal = (
        "rrna contamination in total (QC-passed reads + QC-failed reads)"
    )
    RRnaContaminationMapped = "rrna contamination mapped"
    RRnaContaminationPairedInSequencing = (
        "rrna contamination paired in sequencing"
    )
    RRnaContaminationProperlyPaired = "rrna contamination properly paired"
    RRnaContaminationRead1 = "rrna contamination read1"
    RRnaContaminationRead2 = "rrna contamination read2"
    RRnaContaminationSecondary = "rrna contamination secondary"
    RRnaContaminationSingletons = "rrna contamination singletons"
    RRnaContaminationSupplementary = "rrna contamination supplementary"
    RRnaContaminationWithMateMappedToDifferentChr = (
        "rrna contamination with mate mapped to a different chr"
    )
    RRnaContaminationWithMateMappedToDifferentChrAndGoodMapQ = (
        "rrna contamination with mate mapped to a different chr mapQ>=5"
    )
    RRnaContaminationWithSelfAndMateMapped = (
        "rrna contamination with itself and mate mapped"
    )
    Read1AverageLength = "read 1 average length"
    Read2AverageLength = "read 2 average length"
    ReadsMappedAndPaired = "reads mapped and paired"
    TotalClusters = "total clusters"
    TotalReads = "total reads"
    UniqueReads = "unique_reads"
    UnmappedReads = "unmapped reads"


class RnaSeqQc2Column(BaseRnaSeqQc2Column):
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


class RnaSeqQc2MergedColumn(BaseRnaSeqQc2Column):
    Donor = ColumnNames.Donor
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    Project = ColumnNames.Project
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class RunReportColumn(BaseColumn):
    """
    The column names of a runreport record.
    """

    Barcodes = ColumnNames.Barcodes
    Coverage = "Coverage (collapsed)"
    EstYield = "Estimated Yield (collapsed)"
    ExternalName = "External Name"
    GroupID = "Group ID"
    InsertMean = "Insert Mean"
    InsertSD = "Insert Stddev"
    Lane = ColumnNames.Lane
    Library = "Library"
    MapPercent = "Map Percent"
    NumberOfTargets = "Number of Targets"
    PerOnTarget = "Percent Mapped on Target"
    PFReads = "PF Reads"
    PFYield = "PF Yield"
    R1IndelPercent = "R1 Indel Percent"
    R1Length = "R1 Read Length"
    R1MismatchPercent = "R1 Mismatch Percent"
    R1SoftClipPercent = "R1 Soft Clip Percent"
    R2IndelPercent = "R2 Indel Percent"
    R2Length = "R2 Read Length"
    R2MismatchPercent = "R2 Mismatch Percent"
    R2SoftClipPercent = "R2 Soft Clip Percent"
    ReadsPerStartPoint = "Reads/SP"
    Run = ColumnNames.Run
    TargetFile = "Target File"
    TargetSize = "Target Size (bp)"
    TSVPath = "TSV Path"

    # Run, Lane, Library need to be unique
    ETLValidateDuplicateRunLaneLib = "ETLValidateDuplicateRunLaneLib"


class RunScannerFlowcellColumn(BaseColumn):
    PercentAboveQ30 = "% > Q30"
    BaseMask = "Base Mask"
    BclCount = "bclCount"
    CallCycle = "callCycle"
    Chemistry = "chemistry"
    Clusters = "Clusters"
    ClustersPF = "Clusters PF"
    CompletionDate = "completionDate"
    ContainerModel = "containerModel"
    ContainerSerialNumber = "containerSerialNumber"
    Cycles = "Cycles"
    Ends = "Ends"
    HealthType = "healthType"
    ImgCycle = "imgCycle"
    IndexLengths = "indexLengths"
    IndexSequencing = "indexSequencing"
    LaneCount = "laneCount"
    NumberCycles = "numCycles"
    NumberReads = "numReads"
    #: Added by ETL
    MISOHealthType = "MISOhealthType"
    PairedEndRun = "pairedEndRun"
    Platform = "platform"
    ProjectedYieldIndex1 = "Projected Yield (Index 1)"
    ProjectedYieldIndex2 = "Projected Yield (Index 2)"
    ProjectedYieldRead1 = "Projected Yield (Read 1)"
    ProjectedYieldRead2 = "Projected Yield (Read 2)"
    #: Added by ETL
    Read1Length = "read1Length"
    #: Added by ETL
    Read2Length = "read2Length"
    Run = ColumnNames.Run
    RunBaseMask = "runBasesMask"
    ScoreCycle = "scoreCycle"
    SequencerFolderPath = "sequencerFolderPath"
    SequencerName = "sequencerName"
    SequencerPosition = "sequencerPosition"
    SequencingKit = "sequencingKit"
    Software = "software"
    StartDate = "startDate"
    WorkflowType = "workflowType"
    YieldIndex1 = "Yield (Index 1)"
    YieldIndex2 = "Yield (Index 2)"
    YieldRead1 = "Yield (Read 1)"
    YieldRead2 = "Yield (Read 2)"


class RunScannerValidationColumn:
    # Flow Cell Cluster measures are valid numbers
    ETLValidateClusters = "ETLValidateClusters"

    # Flow Cell Cluster measures are valid numbers
    ETLValidateClustersPF = "ETLValidateClustersPF"

    # Health Status of run is not stuck on Running
    ETLValidateHeathStatus = "ETLValidateHealthStatus"


class RunScannerLaneColumn(BaseColumn):
    AlignedRead1 = "Aligned (Read 1)"
    AlignedRead1StandardDeviation = "Aligned (Read 1) Standard Deviation"
    AlignedRead2 = "Aligned (Read 2)"
    AlignedRead2StandardDeviation = "Aligned (Read 2) Standard Deviation"
    ClusterDensity = "Density (K clusters/mm²)"
    ClusterDensityStandardDeviation = (
        "Density (K clusters/mm²) Standard Deviation"
    )
    Clusters = "Clusters"
    ClustersPF = "Clusters PF"
    DensityPercentage = "Density %"
    DensityPF = "Density PF"
    DensityPFStandardDeviation = "Density PF Standard Deviation"
    LaneNumber = ColumnNames.Lane
    PercentAboveQ30Index1 = "% > Q30 (Index 1)"
    PercentAboveQ30Index2 = "% > Q30 (Index 2)"
    PercentAboveQ30Read1 = "% > Q30 (Read 1)"
    PercentAboveQ30Read2 = "% > Q30 (Read 2)"
    Pool = "Pool"
    Q30 = "q30"
    Run = ColumnNames.Run


class SamtoolsStatsColumn(BaseColumn):

    RawTotalSequences = "raw total sequences"
    FilteredSequences = "filtered sequences"
    Sequences = "sequences"
    IsSorted = "is sorted"
    FirstFragments = "1st fragments"
    LastFragments = "last fragments"
    ReadsMapped = "reads mapped"
    ReadsMappedAndPaired = "reads mapped and paired"
    ReadsUnmapped = "reads unmapped"
    ReadsProperlyPaired = "reads properly paired"
    ReadsPaired = "reads paired"
    ReadsDuplicated = "reads duplicated"
    ReadsmQ0 = "reads MQ0"
    ReadsQCFailed = "reads QC failed"
    NonPrimaryAlignments = "non-primary alignments"
    TotalLength = "total length"
    TotalFirstFragmentLength = "total first fragment length"
    TotalLastFragmentLength = "total last fragment length"
    BasesMapped = "bases mapped"
    BasesMappedCigar = "bases mapped (cigar)"
    BasesTrimmed = "bases trimmed"
    BasesDuplicated = "bases duplicated"
    Mismatches = "mismatches"
    ErrorRate = "error rate"
    AverageLength = "average length"
    AverageFirstFragmentLength = "average first fragment length"
    AverageLastFragmentLength = "average last fragment length"
    MaximumLength = "maximum length"
    MaximumFirstFragmentLength = "maximum first fragment length"
    MaximumLastFragmentLength = "maximum last fragment length"
    AverageQuality = "average quality"
    InsertSizeAverage = "insert size average"
    InsertSizeStandardDeviation = "insert size standard deviation"
    InwardOrientedPairs = "inward oriented pairs"
    OutwardOrientedPairs = "outward oriented pairs"
    PairsWithOtherOrientation = "pairs with other orientation"
    PairsOnDifferentChromosomes = "pairs on different chromosomes"
    PercentageOfProperlyPairedReads = "percentage of properly paired reads (%)"
    FileSWID = ColumnNames.FileSWID
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    PineryLimsID = ColumnNames.PineryLimsID
    Run = ColumnNames.Run


# Samtools V1.12 added additional fields
class SamtoolsStatsV112Column(SamtoolsStatsColumn):
    BasesInsideTheTarget = "bases inside the target"
    PercentageTargetsWithCoverage = (
        "percentage of target genome with coverage > 0 (%)"
    )
    SupplementaryAligments = "supplementary alignments"


class SequenzaColumn(BaseColumn):
    Cellularity = "cellularity"
    Gamma = "gamma"
    Ploidy = "ploidy"
    SLPP = "SLPP"
    Donor = ColumnNames.Donor
    FileSWID = ColumnNames.FileSWID
    GroupID = ColumnNames.GroupID
    LibraryDesign = ColumnNames.LibraryDesign
    MergedPineryLimsID = ColumnNames.MergedPineryLimsID
    TissueOrigin = ColumnNames.TissueOrigin
    TissueType = ColumnNames.TissueType


class UmiQcColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    Run = ColumnNames.Run
    Lane = ColumnNames.Lane
    Barcodes = ColumnNames.Barcodes
    TotalFamilies = "total families"
    TotalUmiCount = "total umi count"
    PreDedupTotalReads = "PreDedup total reads"
    PostDedupTotalReads = "PostDedup total reads"
    PreDedupMappedReads = "PreDedup mapped reads"
    PostDedupMappedReads = "PostDedup mapped reads"
    PreDedupMeanDepth = "PreDedup mean depth"
    PostDedupMeanDepth = "PostDedup mean depth"
    PreDedupDepthSD = "PreDedup depth standard deviation"
    PostDedupDepthSD = "PostDedup depth standard deviation"


class UmiQcExtractionColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    Run = ColumnNames.Run
    Lane = ColumnNames.Lane
    Barcodes = ColumnNames.Barcodes
    DiscardedReadsPairs = "discarded reads/pairs"
    DiscardedReadsPairsDueToUnknownUMI = (
        "discarded reads/pairs due to unknown UMI"
    )
    pattern1 = "pattern1"
    pattern2 = "pattern2"
    ReadsPairsWithMatchingPattern = "reads/pairs with matching pattern"
    TotalReadsPairs = "total reads/pairs"
    umiListFile = "umi-list file"


class UmiQcFamilyColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    Run = ColumnNames.Run
    Lane = ColumnNames.Lane
    Barcodes = ColumnNames.Barcodes
    FamilySize = "family size"
    PreDedupUmiCounts = "preDedup umi counts"
    PostDedupUmiCounts = "postDedup umi counts"


# Can't use BamQc4 class because lims id wasn't included in umiqc
class UmiQcBamQcColumn(BaseColumn):
    AlignedReference = "alignment reference"
    AverageReadLength = "average read length"
    BasesMapped = "bases mapped"
    Coverage = "coverage"
    CoverageDeduplicated = "coverage deduplicated"
    CoverageMedian = "coverage median"
    CoverageMedian10Percentile = "coverage median 10 percentile"
    CoverageMedian90Percentile = "coverage median 90 percentile"
    DeletedBases = "deleted bases"
    DownsampledTotal = "downsampled total"
    FileSWID = ColumnNames.FileSWID
    HardClipBases = "hard clip bases"
    InsertMax = "insert max"
    InsertMean = "insert size average"
    InsertMedian = "insert size median"
    InsertSD = "insert size standard deviation"
    InsertCount = "inserted bases"
    Insert10Percentile = "insert size 10 percentile"
    Insert90Percentile = "insert size 90 percentile"
    Instrument = "instrument"
    Library = "library"
    LowQualityReadsMeta = "low-quality reads meta"
    MappedReads = "mapped reads"
    MarkDuplicates_ESTIMATED_LIBRARY_SIZE = (
        "mark duplicates_ESTIMATED_LIBRARY_SIZE"
    )
    MarkDuplicates_LIBRARY = "mark duplicates_LIBRARY"
    MarkDuplicates_PERCENT_DUPLICATION = "mark duplicates_PERCENT_DUPLICATION"
    MarkDuplicates_READ_PAIR_DUPLICATES = "mark duplicates_READ_PAIR_DUPLICATES"
    MarkDuplicates_READ_PAIR_OPTICAL_DUPLICATES = (
        "mark duplicates_READ_PAIR_OPTICAL_DUPLICATES"
    )
    MarkDuplicates_READ_PAIRS_EXAMINED = "mark duplicates_READ_PAIRS_EXAMINED"
    MarkDuplicates_UNMAPPED_READS = "mark duplicates_UNMAPPED_READS"
    MarkDuplicates_UNPAIRED_READ_DUPLICATES = (
        "mark duplicates_UNPAIRED_READ_DUPLICATES"
    )
    MarkDuplicates_UNPAIRED_READS_EXAMINED = (
        "mark duplicates_UNPAIRED_READS_EXAMINED"
    )
    MismatchBases = "mismatched bases"
    NonPrimaryReads = "non primary reads"
    NonPrimaryReadsMeta = "non-primary reads meta"
    NumberOfTargets = "number of targets"
    PackageVersion = "package version"
    PairedEnd = "paired end"
    PairedReads = "paired reads"
    PairsMappedAbnormallyFar = "pairsMappedAbnormallyFar"
    PairsMappedToDifferentChr = "pairsMappedToDifferentChr"
    ProperlyPairedReads = "properly paired reads"
    QualityCutoff = "qual cut"
    QualityFailedReads = "qual fail reads"
    Read1AverageLength = "read 1 average length"
    Read2AverageLength = "read 2 average length"
    ReadsMappedAndPaired = "reads mapped and paired"
    ReadsOnTarget = "reads on target"
    ReadsPerStartPoint = "reads per start point"
    ReadsMissingMDTags = "readsMissingMDtags"
    Sample = "sample"
    SampleLevel = "sample level"
    SoftClipBases = "soft clip bases"
    TargetFile = "target file"
    TotalBasesOnTarget = "total bases on target"
    TotalClusters = "total clusters"
    TotalInputReadsMeta = "total input reads meta"
    TotalReads = "total reads"
    TotalTargetSize = "total target size"
    UnmappedReads = "unmapped reads"
    UnmappedReadsMeta = "unmapped reads meta"
    WorkflowVersion = "workflow version"
    Barcodes = ColumnNames.Barcodes
    Lane = ColumnNames.Lane
    Reference = ColumnNames.Reference
    Run = ColumnNames.Run


class XenoclassifyColumn(BaseColumn):
    Barcodes = ColumnNames.Barcodes
    BothReads = "both_reads"
    FileSWID = ColumnNames.FileSWID
    GraftReads = "graft_reads"
    HostReads = "host_reads"
    Lane = ColumnNames.Lane
    NeitherReads = "neither_reads"
    Run = ColumnNames.Run
