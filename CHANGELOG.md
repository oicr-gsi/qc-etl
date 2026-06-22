# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Changed
* Update to `uv` as qc-etl's package manager
* Move OICR internal release scripts to https://bitbucket.oicr.on.ca/projects/GSI/repos/infrastructure/browse/qc-etl

## [1.47] - 2026-04-01
### Fixed
* The usual BamQC cleaning rules were not applied to the BamQC tables of IchorCna2 and IchorCna2Merged

## [1.46] - 2026-03-16
### Changed
* The central build function returns more info
* Fixed timeout bug, where previously caches would short circuit timeout
* Fixed tests that were not detecting function exit status

### Added
* Failed and stale records are stored for each cache

## [1.45] - 2026-02-25
### Changed
* Updated to Python 3.13
* Fixed up formatting from missing pre-commit calls
* Fixed up missing key errors in bamqclite

### Added
* Timeout parameter for SQLite cache building

## [1.44] - 2026-02-04
### Changes
* Fixed error with NoneType for analysis_mutect2

## [1.43] - 2026-01-28
### Changes
* Updated analysis_mutect2 parser to support both vcf and tsv file formats

## [1.42] - 2026-01-16
### Added
* crosscheckfingerprint_caller_autoverification cache

## [1.41] - 2025-11-07
### Changes
* Updated for Pinery 3.2.1

## [1.40] - 2025-11-04
### Changes
* Deal with Pandas 3 future runtime warning
### Added
* bamqclite and bamqclitemerged caches added

## [1.39] - 2025-10-09
### Added
* crosscheck_fingerprint_caller utility function to deal with multiple rows for each lims id (due to grouping)

## [1.38] - 2025-08-18
* analysis_mrd cache version changed from 1 to 2 to fix type error [int -> float]

## [1.37] - 2025-08-06
### Added
* biomodalqc cache
* analysis_mrd cache

## [1.36] - 2025-05-29
### Changed
* Readme improvements
* analysis_purple cache version changed from 1 to 2 to fix refiller error.
* analysis_purple cache updated to include PGA calculations, QC metrics and TmbStatus and version changed from 2 to 3.
* Removed print statements from parse.py for analysis_purple cache.

## [1.35] - 2025-05-20
### Added
* Explicit method to check if database connection is valid

## [1.34] - 2025-05-07
### Added
* qcetl_canary cache. Minimal cache that can be cheaply run during integration testing
* crosscheckfingerprint_caller cache

## [1.33] - 2024-12-04
### Changes
* Update dependencies to current versions
* Expanded dependency range to include the major version
* Fixed reference test files (golden data) to account for rounding/sorting differences
* SQLAlchemy and Numpy syntax fixes
* Stripped timezone from RunScanner, as that has been added to the datetime type
* Ran formatter on all fixes, catching lots of drift over the years

## [1.32] - 2024-09-10
* Deleted purityqc cache
* Added purityqc_purple cache
* Added purityqc_sequenza cache

## [1.31] - 2024-08-22
* 2024-07-31 Created purityqc cache

## [1.30] - 2024-03-19
* 2024-03-18 Make MIN_TARGET_COVERAGE column optional in hsmetrics_consensus_cruncher

## [1.29] - 2024-01-15
* 2024-01-12 created umiconsensus cache

## [1.28] - 2023-10-30

### Changes
* Updated default Pinery version to v8
* Deleted parser in hsmetrics_consensus_cruncher, this cache will use parser in hsmetrics
* Removed `crosscheckfingerprints` table from the cache of the same name
* Removed `provenance` module

## [1.27] - 2023-09-06
### Changes
* Updates to release to deal with loss of spb-seqware-production repo being split up
* Remove rnaseqqc2 V2 cache
* Removed inheritance design from calculatecontamination cache
* Shortened calculatecontamination table name as it was too long for postgres
* Fixed invalid index columns (cannot be nested) for ichorcna2
* Fixed invalid index column annotation for sarscov2

### Added
* Test to ensure database table names aren't too long
* Test to ensure primary key columns are not list type (breaks postgres)
* Parser support for crosscheckfingerprints v2 (input coming from
crosscheckfingerprintsCollector)

## [1.26] - 2023-08-21
### Changes
* Bump crimson to 1.1.1 to move dependency of PyYAML from version 5 to 6 (due to critical
version 5 bug https://github.com/yaml/pyyaml/pull/726#issuecomment-1640397938 )
* Add `hsmetrics_consensus_cruncher` cache


## [1.25] - 2023-06-29
### Changes
* Added bamqc4 loader fixes to emseqqc

## [1.24] - 2023-05-25
### Changes
* Add bcl2barcodecaller cache
* Increase crimson version to 1.1

## [1.23] - 2023-04-26
### Changes
* Created ichorcna2
* Fix `version()` not displaying the correct cache time
* Update `.gitignore` to not use the correct folder to exclude

## [1.22] - 2023-04-18
### Changes
* Loading from multiple sources can deal with missing caches (`remove_missing`)
* Reverting to a previous cache doesn't cause crash when schema has changed

## [1.21] - 2023-04-05
### Changes
* Fixed an old TODO to validate cache columns (got to it because of a Dashi outage)
* Removed `emseqqc` `Reference` column annotation as it wasn't there
* Removed validation column annotation from `runscanner` as they aren't in the output
* `umiqc` needed a lot of love because column annotations were inherited/reused
* Made `load` function easier to use by supplying defaults
* Made it impossible to have a `QCETLMultiCache` with no root directories
* Removal of dead comment in testing
* Fix wrong default in `QCETLMultiCache.load_same_version`
* Add versions string to `QCETLMultiCache`
* Missing metadata files don't affect `PostgresCacheFile`

## [1.20] - 2023-03-30
### Changes
* Fixed API bug when root directory was supplied by env variable
* For reasons beyond me, cli tests started rightfully failing. Fixed the tests.

## [1.19] - 2023-03-28
### Changes
* Use pre-built `psycopg2-binary` to that no compiling is necessary during qcetl install

## [1.18] - 2023-03-23
### Changes
* Test to enforce column names being less than 64 characters because of postgres requirement
* New rnaseqqc2 cache that passes the new column name check
* Removed redundant `--force` flag from `build postgres` CLI

## [1.17] - 2023-03-13
### Changes
* Fix bug in Postgres loading
* Fix `emseqqc` lambda table not loading with `__getattr__` approach

### Added
* Loading caches from multiple sources

## [1.16] - 2023-02-28
### Added
* Postgres support
* Archive mode. When enabled in the CLI, records won't be deleted.

### Changes
* `Cache.load` now has a default implementation that shouldn't be overridden

## [1.15] - 2023-02-07
### Added
* emSeqQc parser

### Changes
* bamqc parse function no longer requires a workflow version parameter. If not supplied, takes it from the version
embedded in the JSON output
* samtools stats parser deals with the extra fields added with samtools v1.12

## [1.14] - 2023-01-16
### Changes
* cfmedipqc parser deals with metrics that are strings and scientific notation

## [1.13] - 2023-01-03
### Changes
* cache building logs how many records will be removed

## [1.12] - 2022-11-25
### Changes
* Better logging when building links to existing caches
* Temp cache files aren't left hanging around when uncaught exceptions occur
* refactored AnalysisDelly parser split csv read into chunks
* added empty file handling for AnalysisMutect2 parser
* Updated umiqc parser make primary key unique_
* `stdout` to Shesmu is flushed
* `refill-config` CLI command produces valid refillers
* Updated all Analysis caches to take merged_pinery_lims_ids
* The CLI `build` command accepts root dir from the refiller
* Fixed `refill-config` CLI output (bug caught because of CLI testing)

### Added
* CLI testing

## [1.11] - 2022-11-14
### Added
* AnalysisSequenza Cache, used in Analysis Reports
* AnalysisDelly Cache, used in Analysis Reports
* AnalysisRSEM Cache, used in Analysis Reports
* AnalysisStarFusion, used in Analysis Reports

### Changes
* bamqc/dnaseqqc parsers don't depend on workflow embedded metadata
* refactored AnalysisMutect2 parser to avoid shell call, split csv read into chunk
* `add_shesmu_metadata` no longer required the parsed DataFrame. This was a bad design decision due to the original
bamqc parser
* Remove deprecated pandas function from runscanner parser
* sezuenza parser takes call ready metadata and parses the zip file

## [1.10] - 2022-10-26
### Added
* AnalysisMutect2 Cache, used in Analysis Reports
* Forced re-caching can now be done through CLI

### Changes
* Release procedure keeps all previous versions in modulator

## [1.9] - 2022-10-11
### Changes
* New umiqc paper
* Relax Pandas requirements

## [1.8] - 2022-09-21
### Changes
* mutectcallability fix to switch Pinery LIMS from single lane (wrong) to call ready

## [1.7] - 2022-09-14
### Changes
* Reverted cache version numbers to keep qc-gate-etl happy

## [1.6] - 2022-09-12
### Changes
* Add xenoclassify parser and test cases
* Add Pinery Lims ids to caches for use by dim sum
* Add tests to confirm that Shesmu input format is valid and matches tests

## [1.5] - 2022-08-09
### Changed
* Updated to Python 3.10 and numpy 1.23.1

## [1.4] - 2022-07-20
### Changes
* Prune down and store the CrosscheckFingerprints cache in a new table. This is currently done by Dashi, which is the major cause of the long startup times.
* Fix the release process to properly commit files.
* Add `pytest.ini` file to display logger output during testing.
* Add metagenomicReport parser

## [1.3] - 2022-06-22
### Changed
* Release script updates cron scripts that call qc-etl
* Proper unique keys for the `calculatecontamination` workflow

## [1.2] - 2022-06-10
### Changed
* All Shesmu inputs are stored for each cache. Previously, only the last input was stored.
* Added cache for Picard calculateContamination
* Prevented release script mangling dependency versions when package version was being updated
* `requirements.txt` matches `setup.py`

## [1.1] - 2022-05-09
### Changed
* Expanded README
* Added loader function for the dumped pinery DB
* New `cfmedipqc` cache version (request for column renames)
* SQLAlchemy test failures gave obscure error messages. Added test to catch those errors
earlier with clearer error messages.
* Removed `devprodmixed` release procedure. There are no more qc-etl olives there and
new ones should live there just long enough to be moved to stage.

## [1.0] - 2022-04-20
### Changed
* Removed HDF5 backend (`tables` package) in favor of a SQL database backend
(`sqlalchemy` package)
* Retained file based caches by using SQLite

## [0.59.0] - 2022-03-07
### Added
* A smaller CrosscheckFingerprint cache, where unused columns aren't present.

## [0.58.0] - 2022-02-28
### Added
* DnaSeqQc cache (new version of BamQC4)

## [0.57.0] - 2022-01-12
### Changed
* Pegged dependency versions. `tables` 3.7 breaks on the cluster due to enforcing Python
version naming on C libraries (hdf5).
* Enforce UTF-8 encoding for Mongo DB CSV dump

## [0.56.0] - 2022-01-12
### Changed
* Added CLI for dumping Provenance Mongo DB

## [0.55.0] - 2021-10-20
### Changed
* Runscanner parser no longer crashes on flow cells without a run alias

## [0.54.0] - 2021-09-22
### Added
* HsMetrics Consensus Cruncher parser

### Changed
* CLI consistency and documentation improvements
* README updated to reflect state of ETL

## [0.53.0] - 2021-03-26
### Removed
* `picard.hsmetrics` histogram table (resulted in large cache causing numpy crashes)

## [0.52.0] - 2021-03-03
### Removed
* `bamqc4` v4 cache

### Changed
* `bamqc3` and `bamqc4` down-sampling normalization is properly rounded
* Bug fixes in `crosscheckfingerprints.utility.generate_matrix`

## [0.51.0] - 2021-02-23
### Changed
* Removed `MinTargetCoverage` column from HS Metrics as it does not exist

### Added
* Picard crosscheckFingerprints parser

## [0.50.0] - 2021-02-18
### Changed
* Fixed column types to match reality

### Removed
* `bamqc` parser as the workflow is deprecated

## [0.49.0] - 2021-02-16
### Changed
* Annotated cache column types are now enforced
* bamqc lane column is int type instead of str
* Fixed invalid type values ("mapped reads") in bamqc3 and bamqc4

## [0.48.0] - 2021-01-19
### Changed
* Don't allow Pandas 1.2, as it breaks runscanner parser and does not support Python 3.6
* Moved cache formats to the api class and centralized file names in the api
* QCETLCache class now always accepts both string name or `Cache`object in function
calls

### Added
* CLI call to summarize and filter Shesmu input data and Shesmu input that failed to
parse
* QCETLCache exposes path to Shesmu input JSON and parse failure JSON files

## [0.47.0] - 2021-01-04
### Changed
* Unexpected errors in individual record parsing do not cause parsing process to halt
* `Cache.build` returns a list of failed Shesmu input data
* `Cache.get_data_frames` now has a default implementation that safely combines
individually parsed records
* Moved exceptions into their own module due to circular import errors
* Module level parse function signatures are now as simple as possible

### Added
* `Cache.parse_single_record` and `Cache.metadata_to_add`, which need to be implemented
by each parser based on `Cache`
* `qcetl.build` returns non-0 status if parsing failed unexpectedly (returns number
of records that failed)
* `qcetl.build` creates `failedinputs.json` file containing Shesmu input that failed
to parse

### Removed
* `bcl2fastq` and `rnaseqqc` support (workflows no longer used)

## [0.46.0] - 2020-11-18
### Changed
* cfmedipqc PassedFilterHQMedianMismatches needs to be a float

## [0.45.0] - 2020-11-17
### Removed
* Deprecated BamQC4 version 2 schema (was failing tests)

### Added
* Count option to the CLI

### Changed
* Picard InsertSizeMetrics `?` is converted to NaN

## [0.44.2] - 2020-10-29
### Fixed
* Prevent BamQC4 version 2 from causing memory issues

## [0.44.1] - 2020-10-28
### Added
* BamQC4 version 4 schema (without histogram data table)

### Removed
* BamQC4 version 3 schema (histogram is huge and causes memory issues)

## [0.44.0] - 2020-10-27
### Fixed
* Rebuilding existing cache no longer invalidates it during rebuild
* BamQC4 takes the incorrectly named `coverage_histogram` field

### Added
* BamQC4 version 3 schema

### Removed
* Deprecated cache versions: bamqc3, bamqc4, cfmedip, rnaseqqc2

## [0.43.2] - 2020-10-20
### Fixed
* Crash if optional incremental file is not provided

## [0.43.1] - 2020-10-19
### Fixed
* Stream logging output goes to stderr only, as stdout is reserved for Shesmu

## [0.43.0] - 2020-10-14
### Fixed
* Caching will now always occur when version schema is changed. Previously, stale input
would prevent caching, even when schema version had changed.
* Median calculations were wrong due to sorting assumption being wrong (function
assumed DataFrame was sorted, when it was not)
* Cache versions with different outputs can be properly tested

### Removed
* v1 cfmedip cache (deprecated by v2)

### Added
* v2 cache for bamqc3, bamqc4, and rnaseqqc2 as median was fixed
* v3 cache for cfmedip (includes 10 and 90 percentile median inserts)

## [0.42.0] - 2020-10-06
### Fixed
* Incremental caching works correctly with new and multiple schema versions
* `cachechecker` takes into account multiple schema versions

### Added
* v2 cache for cfmedip (which has the Picard InsertSizeMetrics data)

### Removed
* Bedtools tables that were not used by Dashi and were large and causing refiller memory
issues

## [0.41.0] - 2020-09-23
### Added
* Total Clusters column for BamQC3 and BamQC4
* Total Clusters column for RNASeqQC2
* Median (10/90 percentiles) column for RNASeqQC2

## [0.40.0] - 2020-08-27
### Removed
* The `coverage_hist` table from the `BedToolsSarsCov2Cache`. It was not used and
causing memory errors with Shesmu refiller.

## [0.39.0] - 2020-08-24
### Fixed
* Release script failed to remove temp files

### Changed
* Updated release procedure to check development instance of Dashi

### Removed
* Caches are no longer saved in folders with names that include cache version
(`cachename_1`)

### Added
* `bwamem` parser for the cutadapt output

## [0.38.0] - 2020-08-06
### Added
* Normal/tumor cutoffs for `mutectcallability`. NOTE: Cache version stayed the same as
Dashi would become out of date until Dashi release. ETL design change is required to
allow for more than one cache version to co-exist.

### Changed
* Uncaught exceptions are logged
* Logs also go to stdout/stderr (for refiller logging)
* Cache save folder is now just the name of the cache (bamqc4), rather than
name_version (bamqc4_1). This will make it easier to handle caches with multiple
versions, as all of them will now be loaded from one file

### Fixed
* Several parser would crash if file did not exist
* Incremental building would crash if empty cache was encountered

## [0.37.1] - 2020-07-27
### Fixed
* Release scripts errors

## [0.37.0] - 2020-07-10
### Changed
* Split up release process

### Added
* `bcl2barcode` loading corrects for flow cells with merged lanes

## [0.36.2] - 2020-06-22
### Added
* Comment to inform users that `print` statements are for Shesmu
* Restore `QCETLCache.versions` function

## [0.36.1] - 2020-06-19
### Fixed
* Added back a buffer flush that was was necessary for Shesmu compatibility

## [0.36.0] - 2020-06-18
### Changed
* The `Cache` class is retrieved in one spot in the CLI
* Logging has replaced redirects for the CLI `build` command

### Added
* `run_summary` cache to bcl2count that contains total clusters

## [0.35.0] - 2020-06-15
### Added
* Base `Cache` class can specify save folder name

### Fixed
* No crash occurs if incremental file is missing. Full rebuild occurs.
* `Cache.__getattr__` can now store a cache with more than one version

### Changed
* Command line interface now determines the root save folder, with the specified
cache determining the name of the folder were all cache files are saved. This ensures
that different cache versions will be in different folders.

### Removed
* `Cache.versions`: dead function

## [0.34.0] - 2020-06-12
### Changed
* `force` file in cache directory now skips incremental cache
* bamQC4 calculates median coverage and percentiles only for 4.0.3 and above
* Shesmu workflow version overwrites embedded JSON field

### Removed
* bamQC3 no longer calculates median coverage and percentiles

## [0.33.0] - 2020-06-05
### Added
* INFO logging to `Cache.build` call
* Test if empty input causes crash

### Fixed
* Empty DataFrames no longer crash parsing calls

### Changed
* Abstracted `Cache.build` call so it can be shared by classes that inherit `Cache`.
Now, the easier to implement `get_data_frames` needs to be provided.

## [0.32.0] - 2020-05-13
### Added
* Utility function to load JSON with `numpy.nan` instead of `None`

### Fixed
* `null` values in merged RnaSeqQC2 Picard output do not cause a crash

## [0.31.0] - 2020-05-08
### Fixed
* Median and quantile functions don't crash with empty DataFrames

## [0.30.0] - 2020-05-06
### Added
* Coverage Median and 10/90 Percentile BamQC3 and BamQC4

### Fixed
* Insert Size median and ranges was being calculated for the whole DataFrame
rather then buy IUS

## [0.29.0] - 2020-05-04
### Added
* Utility function to combine workflows from different versions

## [0.28.0] - 2020-05-04

### Added
* BamQC3 and BamQC4 parses histograms
* Insert Size Median and 10/90 Percentile BamQC3 and BamQC4
* Utility functions to calculate median and quantiles from BamQC histograms

### Changed
* BamQC3 and BamQC4 get File SWID from `copy_identifier`
* Changed BamQC3/4 parsing to allow for cleaner histogram parsing

## [0.27.0] - 2020-04-14

### Added
* Add sequencing control type to Pinery
* Median coverage 10th/90th percentile coverage bedtools calculations columns

### Changed
* Fix bug causing many Pinery columns to be missing
* Upgrade default Pinery provider version from v2.2 to v7

## [0.26.0] - 2020-04-14

### Changed
* Bug fixes to SARS BEDtools parser
* Bug fix to cfMeDIP parser

## [0.25.0] - 2020-04-06

### Added
* `bedtools coverage -hist`, `bedtools genomecov`, and `bedtools genomecov -d` parsers
* `bedtools` cache for sarsCoV2Analysis workflow
* `samtools stats` parser and cache for sarsCoV2Analysis workflow

## [0.24.0] - 2020-04-02

### Added
* `kraken2` parser
* `cfmedipqc` parser

## [0.23.0] - 2020-03-26

### Added
* Parsers take new Shesmu `reference` parameter (optional for now to allow deploying
this release before `reference` infrastructure is inplace)

## [0.22.0] - 2020-03-20

### Added
* BamQC4: New cache format, parser and tests

## [0.21.0] - 2020-02-13

### Added
* Incremental caching
* Added `clinical` field to Pinery Projects

### Fixed
* BamQC cache now used File SWID rather than LIMS IUS SWID
* Bcl2fastq bug where cleaning rules were not respected
* Corrected an RNAseqQC2 cache key

### Changed
* Command line interface works with and without incremental caching
* Updated to Pandas 1.0 and NumPy 1.18

## [0.20.0] - 2020-02-07

### Fixed
* Corrected some RNAseqQC2 cache keys
* Fixed FutureWarning in Pinery parser

## [0.19.0] - 2020-02-04

### Fixed
* Missing BamQC3 Total Bases on Target metric is now being parsed

### Added
* Calculated Coverage and Deduplicated Coverage columns to BamQC3

### Changed
* Down sampled BamQC3 metrics are now normalized to original input BAM
upon loading (can be turned off with `CleaningRules`)

## [0.18.0] - 2020-01-30

### Added
 * Add rnaseqqc2 and rnaseqqc2merged cache formats


## [0.17.0] - 2020-01-27

### Added
 * Add bcl2barcode cache format
### Fixed
  * Corrected some values in MutectCallability parser

## [0.16.2] - 2020-01-16

### Changed
 * Add file SWID to HSMetrics cache

### Removed
  * The Run Report cache format

### Fixed
 * Fixed bug in bcl2fastq `is_single_and_dual_index_run`
 * Added ichorCNA merged to cache list

## [0.16.1] - 2020-01-14
 * Fix incorrect HSMetrics input parameter names

## [0.16.0] - 2020-01-14

 * Add merged BamQC3 cache
 * Add merged HSMetrics cache
 * Add merged ichorCNA cache
 * Add Mutect Callability cache
 * bamqc3 `Picard PERCENT_DUPLICATION` fix
 * Add build time and schema version pretty printer

## [0.15.0] - 2019-12-04

### Changed

 * Fix BamQC3 to match correct data format
 * Speed up `PineryClient.get_runs` (by ignoring pools)
 * Exit cleanly with no input data
 * Truncate logs to keep them short

## [0.14.0] - 2019-12-03

### Changed

* Clarify URL endpoint for `QC_ETL_RUNSCANNER_MASTER_URL`
* Update Pinery sorting to avoid warning
* Improve speend of Pinery Samples parsing
* Retain samples from Pinery provenance even if they have some null fields
* Fix ichorCNA column name

## [0.13.0] - 2019-11-29

### Added
* Automatic documentation generation

### Fixed
* Tests
* ichorCNA parser

## [0.12.0] - 2019-11-27

### Fixed
* Typo when dumping `lastinput.json` during cache build

## [0.11.0] - 2019-11-25

### Changed
* Fixes to some Pinery field names
* Improve cache documentation
* Fix cases for keys
* Fix handling of missing BamQC data
* Fix incorrect input key name in RunReport builder
* Dump input data during refill for debugging

## [0.10.0] - 2019-11-26

### Changed
* Make latest symlink relative so that it can be copied to a new location
* Allow disk use when processing large Mongo results
* Store the input file SWID for ichorCNA data

### Added
* Add support for BamQC3

## [0.9.0] - 2019-11-22

### Changed
* Module structure was reorganized to combine small modules together
* `load_json_from_url` returns `None` if 404 code is encountered
* Run Scanner loads one JSON file with all runs (rather than loading one JSON
file for each run)
* Pinery is in own module `pinery`
* Pinery instruments, projects, samples, and sequenceruns are no longer cached,
but downloaded via `PineryClient`
* Provenance is in own module `provenance` and is no longer cached

### Added
* `BaseColumn.asdict()`, `BaseColumn.keys()`,`BaseColumn.values()` to show
the column class variables, the Pandas DataFrame string, and the relationship
between the two
* `ichorcna` module
* Use environmental variable to set default Mongo and Pinery URL
* Use `dotenv` to allow for easy setting of environmental variables in
development environment

### Removed
* `BaseColumn.columns()` function (was confusing)

## [0.8.0] - 2019-11-18

### Changed
* Ensure IUS `(run, lane, sample)` columns for all parsers, with consistent column names
* In `runscanner`, the `flowcell` cache has only `run`; the `lane` cache has only `(run, lane)`
* All other parsers have `(run, lane, sample)`
* Tests check that `(run, lane, sample)` are present and correctly named

### Added
* `__init__.py` added for `sequenza`. Fixes import failure in Shesmu.
* Utility method for renaming columns in a dataframe

## [0.7.0] - 2019-11-12

### Changed
* All caches switch to the `Cache` class
* Shesmu provides metadata instead of Provenance
* Pinery Lane Provenance and Sample Provenance pull from MongoDB instead of
web API

### Added
* `CleaningRules` for fixing/removing invalid values
* `Cache` and `HdfCacheFile` classes for unified caching and cache loading
* Command line interface
* Public Python API (`QCETLCache` and `QCETLColumns`)
* Caching Sequenza data
* Basic testing for all caches

### Removed
* `cache` and `load_cache` functions (in favour of `Cache` class)
* Validation columns dealing with row duplication (excluded upstream by Shesmu)
* Validation column dealing with invalid TopHat aligner (excluded upstream by
Shesmu)

## [0.6.0]

Intentionally skipped

## [0.5.0] - 2019-10-07

### Changed
* Each top level module produces only one hd5 cache file


## [0.4.0] - 2019-10-03

### Changed
* RunScanner `ReadLength` and `ReadLengths` values have been removed in favor of
`Read1Length` and `Read2Length`
* RunScanner flow cell DataFrame contains read and index columns
* RunScanner lane DataFrame contains the standard deviations
* RunScanner long DataFrame no longer contains the validate columns, which have
been moved over to the cached flow cell DataFrame

### Added
* RunScanner flow cell and lane cache

## [0.3.1] - 2019-09-23

### Changed:
* `setup.py` allows for optional installation of development modules
* README installations have been clarified to use `pip` instead of `python
setup.py`
* Code format followed `black` and `flake8` standards

### Added:
* Config files for `black` (pyproject.toml), `flake8` (.flake8), and
`pre-commit` (.pre-commit-config.yaml)


## [0.3.0] - 2019-09-19

### Changed:
* `cache` and `load_cache` functions work with versioned caches
* Changed `Column` Enum to use Class variables (no need to use `.value` all the
time)
* Split constants and column names into their own modules
* Split parsing code and caching code into their own modules
* Fixed bug in `remove_duplicated_keep_last` validity function
* Updated early modules (`pinery.instruments` and `pinery.sequenceruns`) to
conform to current conventions

### Added
* Cache versions: each cache version promises the same schema (column names and
types)
* RNASeq-QC JSON parsing (cache has v1 (zip file only) and v2 (zip file and JSON
file with bam stat information))
* Utility functions `get_column_names` (to extract the `Column` names) and
`get_schema` to retrieve the DataFrame schema
* Complete Column names of all caches
* `load` module that server as public API for cache loading

### Removed
* Dead code from the early stages of development


## [0.2.2] - 2019-09-10

### Changed
* Warning and error logger output has been reduced as much of the previously
logged information is stored in Validation columns

## [0.2.1] - 2019-08-30

### Changed
* Fixed parent finding function in `pinery.samples.utility` to increase speed


## [0.2.0] - 2019-08-28

### Removed
* All sanity functions that edited the parsed DataFrame upstream of caching

### Added
* Validation modules for `bamqc`, `bcl2fastq`, `fastqc`, `rnaseqc`, `runreport`,
and `runscanner.illumina` parsers

### Changed
* `cache` function now add Validity columns to DataFrame
* `load_cache` function options to remove/edit values that failed validation


## [0.1.0] - 2019-08-15
Belated start of a Changelog

### Added
* Parsers for the following GSI workflows have been written:
    * bamqc
    * bcl2fastq (CASAVA)
    * fastqc
    * Pinery (Instruments, Sample Provenance, Samples, and Sequence Runs)
    * Provenance
    * rnaseqc
    * runreport
    * runscanner (Illumina machines)
