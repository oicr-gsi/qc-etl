import json
import logging
import os
import sqlalchemy
from typing import Callable, List, Union, Tuple, Optional

import qcetl.analysis_delly
import qcetl.analysis_mutect2
import qcetl.analysis_rsem
import qcetl.analysis_purple
import qcetl.analysis_mrd
import qcetl.analysis_sequenza
import qcetl.analysis_starfusion
import qcetl.bamqc3
import qcetl.bamqc4
import qcetl.bamqclite
import qcetl.bcl2barcode
import qcetl.bcl2barcodecaller
import qcetl.bedtools
import qcetl.biomodalqc
import qcetl.bwamem
import qcetl.cfmedipqc
import qcetl.common
import qcetl.common.canary
import qcetl.crosscheckfingerprint_caller
import qcetl.dnaseqqc
import qcetl.emseqqc
import qcetl.fastqc
import qcetl.picard.calculatecontamination
import qcetl.picard.crosscheckfingerprints
import qcetl.picard.hsmetrics
import qcetl.picard.hsmetrics_consensus_cruncher
import qcetl.icametrics
import qcetl.ichorcna
import qcetl.ichorcna2
import qcetl.kraken2
import qcetl.metagenomicreport
import qcetl.mutectcallability
import qcetl.purityqc_purple
import qcetl.purityqc_sequenza
import qcetl.rnaseqqc2
import qcetl.runscanner.illumina
import qcetl.samtools
import qcetl.sequenza
import qcetl.picard.umiconsensus
import qcetl.umiqc
import qcetl.xenoclassify

from qcetl.common import (
    CacheFile,
    Cache,
    MultiCacheFromVersion,
    MultiCacheSource,
    ColumnStore,
)

formats = (
    qcetl.analysis_delly.AnalysisDellyCache(),
    qcetl.analysis_mutect2.AnalysisMutect2Cache(),
    qcetl.analysis_rsem.AnalysisRSEMCache(),
    qcetl.analysis_purple.AnalysisPurpleCache(),
    qcetl.analysis_mrd.AnalysisMrdCache(),
    qcetl.analysis_sequenza.AnalysisSequenzaCache(),
    qcetl.analysis_starfusion.AnalysisStarFusionCache(),
    qcetl.bamqc3.BamQc3Cache(),
    qcetl.bamqc3.BamQc3MergedCache(),
    qcetl.bamqc4.BamQc4Cache(),
    qcetl.bamqc4.BamQc4MergedCache(),
    qcetl.bamqclite.BamQcLiteCache(),
    qcetl.bamqclite.BamQcLiteMergedCache(),
    qcetl.bcl2barcode.Bcl2BarcodeCache(),
    qcetl.bcl2barcodecaller.Bcl2BarcodeCallerCache(),
    qcetl.bedtools.BedToolsSarsCov2Cache(),
    qcetl.biomodalqc.BiomodalQcCache(),
    qcetl.biomodalqc.BiomodalQcMergedCache(),
    qcetl.bwamem.BwaMemCache(),
    qcetl.cfmedipqc.CfMeDipQcCache(),
    qcetl.common.canary.QcEtlCanary(),
    qcetl.crosscheckfingerprint_caller.CrosscheckFingerprintCaller(),
    qcetl.crosscheckfingerprint_caller.CrosscheckFingerprintCallerAutoVerification(),
    qcetl.dnaseqqc.DnaSeqQcCache(),
    qcetl.emseqqc.EmSeqQcCache(),
    qcetl.fastqc.FastQcCache(),
    qcetl.icametrics.ICAMetricsCache(),
    qcetl.ichorcna.IchorCnaCache(),
    qcetl.ichorcna.IchorCnaMergedCache(),
    qcetl.ichorcna2.IchorCna2Cache(),
    qcetl.ichorcna2.IchorCna2MergedCache(),
    qcetl.kraken2.Kraken2Cache(),
    qcetl.metagenomicreport.MetagenomicReportCache(),
    qcetl.mutectcallability.MutectCallabilityCache(),
    qcetl.picard.calculatecontamination.CalculateContaminationCallReady(),
    qcetl.picard.calculatecontamination.CalculateContaminationLaneLevel(),
    qcetl.picard.crosscheckfingerprints.CrosscheckFingerprintsCache(),
    qcetl.picard.hsmetrics.HsMetricsCache(),
    qcetl.picard.hsmetrics_consensus_cruncher.HsMetricsConsensusCruncherCache(),
    qcetl.purityqc_purple.PurityQcPurpleCache(),
    qcetl.purityqc_sequenza.PurityQcSequenzaCache(),
    qcetl.rnaseqqc2.RnaSeqQc2Cache(),
    qcetl.rnaseqqc2.RnaSeqQc2MergedCache(),
    qcetl.runscanner.illumina.RunScannerIlluminaCache(),
    qcetl.samtools.SamtoolsStatsCov2Cache(),
    qcetl.sequenza.SequenzaCache(),
    qcetl.picard.umiconsensus.HsMetricsUmiConsensusCache(),
    qcetl.umiqc.umiQcCache(),
    qcetl.xenoclassify.XenoclassifyCache(),
)


def get_cache_class(name: Union[str, Cache]) -> Cache:
    """
    Get the cache class instance associated with name

    Args:
        name: Cache name to retrieve

    Returns:

    """
    if isinstance(name, str):
        cache_class = [x for x in formats if x.name == name]

        if len(cache_class) != 1:
            raise KeyError("Unknown cache name: {}".format(name))
        else:
            return cache_class[0]
    elif isinstance(name, Cache):
        return name
    else:
        raise TypeError(
            "Unsupported type %s as argument to cache file" % type(name)
        )


class QCETLCache:
    """
    Map a directory of QC-ETL data in the standard layout as an object
    """

    LATEST_FILE_NAME = "latest"  # File name of the latest cache
    SHESMU_INPUT_FILE = "lastinput.json"  # Last shesmu input for cache
    FAILED_INPUT_FILE = (
        "failedinputs.json"  # Shesmu records with unexpected errors
    )
    CONFIG_FILE = "config.json"

    def __init__(self, root_dir: str = None):
        """
        Initialize with a given root directory where all caches are located.
        The expected structure is
        `root_dir/{cache_name}_{schema_version}/filename`

        Args:
            root_dir: Can be set to a default with the QC_ETL_ROOT_DIRECTORY
        """
        if root_dir is not None:
            self.root_dir = root_dir
        else:
            self.root_dir = os.getenv("QC_ETL_ROOT_DIRECTORY")

            if self.root_dir is None:
                raise TypeError(
                    "Missing 1 required positional argument: 'root_dir'. Set "
                    "QC_ETL_ROOT_DIRECTORY environmental variable with "
                    "default"
                )

        # If there is no config file, the backend is SQLite (as that only depends on the disk content)
        config_path = os.path.join(self.root_dir, self.CONFIG_FILE)
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                self.backend = config.get("backend")
                with open(config.get("url_file"), "r") as fi:
                    self.url = fi.readline().strip()
        else:
            self.backend = None

        self.caches = {}

    def __getattr__(self, name: Union[str, Cache]) -> CacheFile:
        """
        Return the cache with the following defaults:
        * latest version
        * All invalid rows are dealt with
        * Validation columns are removed
        * The latest cache is returned

        The loaded cache is stored within the class, so getattr can be called
        repeatedly

        Args:
            name: Name of the cache to load

        Returns: The loaded cache

        """
        cache_class = get_cache_class(name)
        cache_dir = cache_class.cache_folder_name()

        if cache_dir in self.caches:
            return self.caches[cache_dir]

        path = self.path_generator(cache_class, self.LATEST_FILE_NAME)

        if self.backend is None or self.backend == "sqlite":
            loaded_cache = cache_class.load(
                cache_class.latest_version(),
                path,
                qcetl.common.CleaningRules(),
                lambda x: None,
            )
        else:
            if self.backend == "postgres":
                loaded_cache = cache_class.load_postgres(
                    cache_class.latest_version(),
                    self.root_dir,
                    self.url,
                    qcetl.common.CleaningRules(),
                    lambda x: None,
                )
            else:
                raise KeyError(f"Unknown backend: {self.backend}")
        self.caches[cache_dir] = loaded_cache
        return loaded_cache

    def load(
        self,
        cache_name: Union[str, Cache],
        schema_version: int,
        cleaning_rules: qcetl.common.CleaningRules = qcetl.common.CleaningRules(),
        log_creator: Callable[
            [str], Union[logging.Logger, None]
        ] = lambda x: None,
        file_name: str = None,
    ) -> CacheFile:
        """
        Load cache, allowing for full customization of cache loading

        Args:
            cache_name: Which cache to load
            schema_version: The version of the cache to return
            cleaning_rules: How invalid rows and validation colums are dealt
                with. By default, remove all invalid rows.
            log_creator: The logger that will log validation functions. By default, no logging.
            file_name: Which file name to return (by default latest)

        Returns: The loaded cache

        """
        file_name = self.LATEST_FILE_NAME if file_name is None else file_name
        cache_class = get_cache_class(cache_name)
        path = self.path_generator(cache_class, file_name)

        if self.backend is None or self.backend == "sqlite":
            return cache_class.load(
                schema_version, path, cleaning_rules, log_creator
            )
        elif self.backend == "postgres":
            return cache_class.load_postgres(
                schema_version,
                self.root_dir,
                self.url,
                cleaning_rules,
                log_creator,
            )
        else:
            raise KeyError(f"Unknown backend: {self.backend}")

    def path_generator(self, cache: Union[str, Cache], file_name: str) -> str:
        """
        Generate path for the saved file

        Args:
            cache: Cache to load
            file_name: Name of the file

        Returns: The absolute file path

        """
        cache = get_cache_class(cache)
        return os.path.join(self.root_dir, cache.cache_folder_name(), file_name)

    def path_failed_input(self, cache: Union[str, Cache]) -> str:
        """
        The path to JSON of Shesmu inputs that caused unexpected errors

        Args:
            cache: Which cache to get the input for

        Returns:

        """
        return self.path_generator(cache, self.FAILED_INPUT_FILE)

    def path_latest_input(self, cache: Union[str, Cache]) -> str:
        """
        The path to the JSON file of the latest input from Shesmu

        Args:
            cache: Which cache to get the input for

        Returns:

        """
        return self.path_generator(cache, self.SHESMU_INPUT_FILE)

    def test_connection(self) -> bool:
        """
        Is there something there to load caches from?

        It may be ambiguous why a specific table isn't being loaded. Table doesn't exist, the cache doesn't exist,
        there is no connection to a database to load from. This explicitly checks for the last scenario.

        Returns:

        """
        if self.backend is None or self.backend == "sqlite":
            return os.path.isdir(self.root_dir)
        elif self.backend == "postgres":
            engine = sqlalchemy.create_engine(
                "postgresql+psycopg2://" + self.url
            )
            try:
                # it's safe to keep calling `connect()` as long as they are dropped
                with engine.connect() as _:
                    return True
            except sqlalchemy.exc.OperationalError:
                return False
        else:
            raise KeyError(f"Unknown backend: {self.backend}")

    def versions(self, caches: List[Union[str, Cache]]) -> str:
        """
        Generate a version number for specific caches
        Args:
            caches: the caches to include

        Returns:
            A formatted composite version number
        """
        return ", ".join(
            sorted(
                {
                    "%s-%s"
                    % (
                        cache.name if isinstance(cache, Cache) else cache,
                        getattr(self, cache).version(),
                    )
                    for cache in caches
                }
            )
        )

    @classmethod
    def caches(cls) -> Tuple[Cache, ...]:
        return formats


class QCETLMultiCache:
    """
    Loading caches from multiple cache locations.
    """

    def __init__(self, root_dirs: List[str]):
        if len(root_dirs) < 1:
            raise ValueError("Must supply at least one root directory")
        self.caches = [QCETLCache(d) for d in root_dirs]

    def load_same_version(
        self,
        cache: Union[str, Cache],
        version: Optional[int] = None,
        cleaning_rules: qcetl.common.CleaningRules = qcetl.common.CleaningRules(),
        log_creator: Callable[
            [str], Union[logging.Logger, None]
        ] = lambda x: None,
    ) -> MultiCacheSource:
        """
        Load the same cache version from multiple sources. The collapsed DataFrame drops duplicates
        based on the unique key specified in the cache keeping the record from the source path first specified.

        Args:
            cache: Which cache to load
            version: The version to load. Latest by default
            cleaning_rules: Clean up returned cache. On by default.
            log_creator: If supplied, logs any cleaning done to the data as specified by `cleaning_rules`

        Returns: A loaded cache

        """
        cache_class = get_cache_class(cache)
        version = cache_class.latest_version() if version is None else version
        multi = [
            c.load(cache, version, cleaning_rules, log_creator)
            for c in self.caches
        ]
        dedup = cache_class.primary_key[version]
        return MultiCacheFromVersion(multi, dedup)

    def test_connection(self) -> List[bool]:
        """
        Test if each cache has a valid database connection behind it.

        Returns: The same order as the paths specified during initialization.

        """
        return [c.test_connection() for c in self.caches]

    def versions(self, caches: List[Union[str, Cache]]) -> str:
        """
        Generate a version number for specific caches

        Args:
            caches: the caches to include

        Returns:
            A formatted composite version number
        """
        return ",".join([x.versions(caches) for x in self.caches])


class QCETLColumns:
    """
    Common access points for Columns associated with DataFrames
    """

    def __getattr__(self, name: str) -> ColumnStore:
        return get_cache_class(name).get_columns()

    @staticmethod
    def load(name: str, schema_version: int) -> ColumnStore:
        return get_cache_class(name).get_columns(schema_version)
