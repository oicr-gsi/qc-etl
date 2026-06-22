# QC ETL Developer Guide

This guide explains how to create, test, build, and verify a QC ETL parser.
QC ETL parser development can be done locally with source files, metadata, and
tests.

You can create and run a parser with:

- workflow output files
- metadata from MISO, Pinery, or a hand-written JSON file
- local tests
- a local SQLite cache build

## Requirements

- `uv` (see https://github.com/astral-sh/uv/releases)
- Git
- a local clone of the `qc-etl` repository

## What QC ETL Needs

A QC ETL parser needs:

- parsing code
- a cache class
- declared columns
- declared input fields
- tests
- fixture files

At build time, QC ETL only needs a list of input records. Each input record is
a dictionary.

That input can come from:

- MISO
- Pinery
- a helper script
- a manually created `input.json`

## Helpful `qc-etl` Commands

These are the commands that are most useful during parser development:

- `qc-etl --help`
- `qc-etl list` : shows registered parsers
- `qc-etl versions [format]` : shows schema versions for a parser
- `qc-etl tables [format]` : shows tables in a parser
- `qc-etl schema [format] [table]` : shows column names and types
- `qc-etl dump [format] [table] -d [cache-root]` : exports built cache data to CSV
- `qc-etl build [format] -d [cache-root] -c [checksum]` : builds a SQLite cache from JSON read from stdin
- `qc-etl build-postgres [format] -d [cache-root] -c [checksum]` : builds a Postgres-backed cache
- `qc-etl count [format] [table] -d [cache-root]` : counts rows in a built cache
- `qc-etl input [format] shesmu -d [cache-root]` : shows the last input JSON used by the cache
- `qc-etl input [format] failed -d [cache-root]` : shows records that failed during build


## Development Setup

`git clone [repo]`

`cd qc-etl`

`uv sync --frozen`

`uv run pre-commit install`

Useful commands to confirm the environment:

`uv run qc-etl --help`

`uv run pytest`

## Where Parser Code Goes

Files for a new parser:

- `qcetl/[parser_name]/parse.py`
- `qcetl/[parser_name]/__init__.py`
- `qcetl/column.py`
- `qcetl/api.py`
- `test/test_[parser_name].py`
- `test/files/...`

Purpose of each:

- `parse.py`: read source files and parse metrics
- `__init__.py`: define the cache class and parser contract
- `column.py`: define named column constants
- `api.py`: register the parser with QC ETL
- `test/test_[parser_name].py`: parser test
- `test/files/`: source fixtures and expected output files

Each parser lives in its own directory under `qcetl/`.
The parser directory name and cache name should be chosen carefully and kept
consistent.

Each parser directory contains:

- `parse.py`: parsing and transformation code
- `__init__.py`: cache definitions, schema, columns, and metadata mapping

The cache columns are declared in `__init__.py`.
Each cache is one or more tables with predefined columns that contain:

- identifying information
- metrics

Because parsers run with limited memory, avoid reading very large files into a
single pandas DataFrame when that is not necessary. If a source file is large,
prefer reading it incrementally, for example with pandas `chunksize`.

## How To Create a Parser

### 1. Decide the parser contract

Before writing code, decide:

- parser name
- source file types
- metadata fields required
- output table names
- primary keys
- initial schema version

Each cache class is a subclass of `Cache` from
`qcetl/common/__init__.py`.
That class is the best local reference for expected behavior, typing, and
brief code comments.

### 2. Add columns in `qcetl/column.py`

Do not hard-code raw column strings throughout the parser. Create a
`BaseColumn` subclass.

Example shape:

```python
from qcetl.column import BaseColumn, ColumnNames


class ExampleColumn(BaseColumn):
    FileSWID = ColumnNames.FileSWID
    Run = ColumnNames.Run
    Lane = ColumnNames.Lane
    MetricA = "Metric A"
```

### 3. Create `parse.py`

The parsing code should:

- open the workflow output files
- extract values
- normalize types
- return parsed pandas data

Keep metadata lookup separate from file parsing when possible.

### 4. Create the cache class in `__init__.py`

The cache class inherits from `qcetl.common.Cache`.

Each parser define:

- `name`
- `schema_versions`
- `columns`
- `input_format`
- `primary_key`
- `input_key`

Each parser implement:

- `parse_single_record`
- `add_shesmu_metadata`

The method name `add_shesmu_metadata` is historical. It simply adds metadata
from the input record into the parsed table.

The cache class will include:

- `self.name`: cache name
- `self.schema_versions`: tables and their stored columns
- `self.input_format`: fields expected from the input record
- `self.primary_key`: unique key for each table

`parse_single_record` is mandatory.
It accepts one input record matching `self.input_format` and returns
DataFrames matching the cache tables defined in `self.schema_versions`.

`add_shesmu_metadata` defines which metadata from the input record should be
stored in each table.

Some caches also customize load-time behavior through `load_fixer_function`
when data needs cleanup or special handling during loading.

### 5. Register the parser in `qcetl/api.py`

If the parser is not registered there, QC ETL CLI and API will not know it
exists.

Confirm registration with:

`qc-etl list`


## How To Create `input.json`

Create a file named `input.json` containing a JSON list of input records.

Example:

```json
[
  {
    "path": "test/files/TEST_0001_lane_level.bamQClite_results.json",
    "pinery_lims_id": "ID1",
    "swid": "SWID",
    "workflow_version": [4, 0, 0],
    "barcode": "ATCTAGCCGGCC",
    "lane": 2,
    "run": "180406_E00389_0179_BHKVJ7CCXY",
    "reference": "hg38"
  }
]
```

Rules for `input.json`:

- top level must be a JSON list
- each element must be one input record
- keys must match the parser `input_format`
- file paths must exist

Where these values can come from:

- MISO
- Pinery
- manual development input
- a local helper script

## How To Build a Parser by hand

Once `input.json` exists, you can build the cache manually:

`mkdir -p local-cache`

`cat input.json | qc-etl build bamqclite -d local-cache -c bamqclite-dev-001`

Meaning:

- `cat input.json`: sends the JSON to stdin
- `qc-etl build bamqclite`: runs the `bamqclite` parser
- `-d local-cache`: chooses the cache root directory
- `-c bamqclite-dev-001`: gives the build a unique checksum or build name

This is the most important manual development flow.

## Build From `refiller.json`

If you already have a `refiller.json` file, you can build a cache directly from
it.

`cat refiller.json | qc-etl build [cache] -d [save-dir] -c [cache-file-name]`

This creates a folder under `[save-dir]` containing the SQLite cache.
If you rebuild from a different `refiller.json`, use a different
`[cache-file-name]` so the new build does not overwrite the old one by name.

This flow is useful when:

- you want to test parser and upstream input generation together
- you already downloaded real build input

## What the Build Produces

After a successful build, QC ETL writes files under the parser cache
directory.

Example:

`ls -la local-cache/bamqclite`

Files include:

- `bamqclite-dev-001.sqlite`
- `bamqclite-dev-001.json`
- `latest`
- `lastinput.json`
- `failedinputs.json`
- `stdout.log`
- `stderr.log`

Meaning:

- `.sqlite`: built SQLite cache
- `.json`: input payload associated with the build
- `latest`: symlink to the latest cache
- `lastinput.json`: last build input
- `failedinputs.json`: failed records
- log files: build logs

## How To Confirm the SQLite Build Is Correct

Do not assume the build is correct just because it completed. Validate it.

### 1. Confirm the parser exists

`qc-etl list`

Make sure `bamqclite` appears.

### 2. Confirm the tables

`qc-etl tables bamqclite`

This shows which tables were created in the cache.

### 3. Confirm the schema

`qc-etl schema bamqclite bamqclite`

Check that the table and column names match what you expect.

### 4. Dump the data to CSV

`qc-etl dump bamqclite bamqclite -d local-cache`

This is the easiest correctness check. Inspect the dumped CSV and confirm:

- expected rows exist
- metadata columns are populated
- parsed metric values look correct
- no obvious null or type issues exist

### 5. Count rows

`qc-etl count bamqclite bamqclite -d local-cache`

This helps confirm the number of rows is what you expected.

### 6. Confirm the stored input JSON

`qc-etl input bamqclite shesmu -d local-cache`

Even though the command name says `shesmu`, it is still useful for manual
development because it shows the last input JSON used for the build. Here,
`shesmu` is simply the CLI keyword for the saved latest-input file.

### 7. Check failed records

`qc-etl input bamqclite failed -d local-cache`

If records appear there, inspect why they failed.

### 8. Compare with golden output

If the parser already has golden CSV data in `test/files/`, compare the dumped
output with the expected golden file.

That is the best confirmation that the built SQLite cache is correct.

### 9. Optional direct SQLite inspection

If you want to inspect the SQLite file directly:

`sqlite3 local-cache/bamqclite/bamqclite-dev-001.sqlite '.tables'`

You can also inspect row counts directly in SQLite if needed. This is optional,
but it can be useful when debugging a build.

## How Incremental Cache Works

Incremental cache means QC ETL starts from an existing cache file instead of
starting from an empty SQLite database.

This helps when:

- most records are unchanged
- only a few records are new
- you already have a previous cache file

QC ETL then:

- keeps existing records that are still valid
- parses only new input records
- removes stale records unless archive mode is used

Incremental cache is optional. You can always do a full build instead.

## How To Build With Incremental Cache

Suppose you already have:

- `local-cache/bamqclite/bamqclite-dev-001.sqlite`

Then build a new version like this:

`cat input.json | qc-etl build bamqclite -d local-cache -c bamqclite-dev-002 -i bamqclite-dev-001.sqlite`

Meaning of `-i`:

- it points to an existing cache file name inside the parser cache directory
- QC ETL copies that file and updates it instead of starting from empty

## What Happens During Incremental Build

If the incremental cache exists and `--force` is not used:

- QC ETL copies the old SQLite cache
- QC ETL checks which input records are new
- only new records are parsed and inserted
- records that are no longer in the input are removed

If the named incremental cache does not exist:

- QC ETL logs that fact
- QC ETL falls back to a full build

If `--force` is used:

- incremental cache is ignored
- QC ETL performs a full rebuild

Force rebuild example:

`cat input.json | qc-etl build bamqclite -d local-cache -c bamqclite-dev-003 --force`

## When To Use Incremental Cache

Use it when:

- parser logic is stable
- schema version is unchanged
- previous cache is trustworthy
- you want faster rebuilds

## How To Run Tests

Run all tests:

`uv run pytest`

Run the BamQcLite tests:

`uv run pytest test/test_bamqclite.py`

During parser development, running the single parser test file is the
fastest feedback loop.

## How To Add `test/files`

Add parser fixtures under `test/files/[parser_name]`.

There are two categories:

- source fixture files that the parser reads
- golden CSV files that represent expected parsed output

Examples already present for `bamqclite`:

- `test/files/bamqclite/TEST_0001_lane_level.bamQClite_results.json`
- `test/files/bamqclite/TEST_0001_lane_level.bamQClite_results.csv`
- `test/files/bamqclite/bamqclite_callready_TEST_0001.json`
- `test/files/bamqclite/bamqclite_callready_TEST_0001.csv`

Recommended process:

1. *ensure all identifiers and internal details are redacted from test data*
2. add the source file to `test/files/[parser_name]`
3. write a parser test that points to it
4. run the test
5. if the golden CSV does not exist, the test helper can generate it
6. inspect the generated CSV carefully
7. commit it once it is confirmed correct

The output CSV files are created by running `uv run pytest`.

## What Input Data Means in a Test

In a QC ETL parser test, input data is the list of dictionaries passed to
`test.cachechecker.check(...)`.

Example:

```python
[
    {
        "path": "test/files/TEST_0001_lane_level.bamQClite_results.json",
        "pinery_lims_id": "ID1",
        "swid": "SWID",
        "workflow_version": [4, 0, 0],
        "barcode": "ATCTAGCCGGCC",
        "lane": 2,
        "run": "180406_E00389_0179_BHKVJ7CCXY",
    }
]
```

This input data is:

- not the parsed table
- not the golden output
- the mock build payload passed into the parser

It represents what QC ETL receives before parsing.

## What Golden Data Means in a Test

Golden data is the expected parsed output.

In the test, it is the mapping from output table name to expected CSV file.

Example:

```python
{
    "bamqclite": "test/files/TEST_0001_lane_level.bamQClite_results.csv"
}
```

This means:

- the parser should produce a table named `bamqclite`
- the expected output rows are stored in that CSV file

The test helper builds the cache, loads it back, and compares the built table
with the golden CSV.

## BamQcLite Test Example

```python
import qcetl.bamqclite
import test.cachechecker


def tests_bamqc_lite():
    test.cachechecker.check(
        qcetl.bamqclite.BamQcLiteCache(),
        [
            {
                "path": "test/files/TEST_0001_lane_level.bamQClite_results.json",
                "pinery_lims_id": "ID1",
                "swid": "SWID",
                "workflow_version": [4, 0, 0],
                "barcode": "ATCTAGCCGGCC",
                "lane": 2,
                "run": "180406_E00389_0179_BHKVJ7CCXY",
            }
        ],
        {
            "bamqclite": "test/files/TEST_0001_lane_level.bamQClite_results.csv"
        },
    )
```

## What the Test Actually Checks

The test helper checks:

- parser is registered
- cache attributes are valid
- input fields match `input_format`
- tables and columns match schema
- primary keys are valid
- built output matches the golden CSV

This is why parser tests are the best first validation step.

## Input Sources

Parsers can be developed and validated locally using:

- local fixture files
- hand-written `input.json`
- downloaded `refiller.json`
- metadata gathered from MISO and Pinery

## Suggested Parser Development Workflow

A good order for new parser work is:

1. add source fixture files under `test/files/`
2. write parsing logic in `parse.py`
3. add columns in `column.py`
4. define the cache class in `__init__.py`
5. register the parser in `qcetl/api.py`
6. write `test/test_[parser_name].py`
7. run `pytest test/test_[parser_name].py`
8. inspect generated or updated golden CSV files
9. create `input.json`
10. run `cat input.json | qc-etl build [parser] -d [dir] -c [checksum]`
11. verify with `tables`, `schema`, `dump`, `count`, and `input`

If you already have real refiller output, an equally valid step 10 is:

`cat refiller.json | qc-etl build [parser] -d [dir] -c [checksum]`

## Final Takeaways

- you can create a QC ETL parser locally
- you can create `input.json` by hand
- `cat input.json | qc-etl build ...` is the core manual build flow
- incremental cache is optional and can speed up rebuilds
- correctness should be checked with tests, `dump`, `count`, `input`, and golden CSV output
- `test/files/` should contain both parser input fixtures and expected output
  CSV files
