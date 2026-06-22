# QC Extract Transform Load (ETL) Project

## Purpose
To parse and store data from QC workflows in a consistent, typed, and versioned format. This allows the user to access QC data without having to find and parse files, cleanup data, or deal with changing output formats. The ETL library and API can be accessed via Python or CLI. ETL output files can be dumped in CSV format for import into other applications.

## Usage
```
qc-etl --help
usage: qc-etl [-h] {list,versions,tables,schema,dump,refill-config,build,build-postgres,count,input} ...

positional arguments:
  {list,versions,tables,schema,dump,refill-config,build,build-postgres,count,input}
                        sub-command help
    list                List all known formats
    versions            List all known versions for a format
    tables              List all known tables for a format
    schema              Display the schema for a table
    dump                Convert a table to a CSV file
    refill-config       Create a Shesmu-compatible definition to rebuild this format
    build               Build a cache and store it in a SQLite backend
    build-postgres      Build a cache and store it in a Postgres backend
    count               Count records. Filter by run, lane, and barcode
    input               Information on Shesmu input.

options:
  -h, --help            show this help message and exit
```

### Examples:
To find available formats (caches):

`qc-etl list`

By default, all commands will return the latest cache version. To list all versions:

`qc-etl versions bamqc4`

Each cache stores one or more tables. To list them:

`qc-etl tables bamqc4`

To get the columns and types of a table:

`qc-etl schema bamqc4 bamqc4`

To download a SQLite cache, its location is specified with the -d flag or set via the QC_ETL_ROOT_DIRECTORY environmental variable. The below are equivalent:

```
qc-etl dump bamqc4 bamqc4
qc-etl dump bamqc4 bamqc4 -d $QC_ETL_ROOT_DIRECTORY
```

If using a Postgres database, add a `config.json` file to the `-d` directory.
```
{"backend": "postgres", "url_file": "/path/to/file/with/url"}
```

To generate the Shesmu refiller command (allows for optional incremental cache)

```
qc-etl refill-config \
    bamqc4 \
    --incremental-cache latest \  # If absent, refiller command doesn't use incremental caching
    --directory /root/cache/directory \  # If absent, use the QC_ETL_ROOT_DIRECTORY environmental variable
    --bin /usr/bin/qc-etl \  # If absent, binary used for this call
    --name bamqc4_cache_v5 \  # If absent, refiller is not given a name
```
To build a cache, it is necessary to pipe the Shesmu refiller output to the `build` command.

```
qc-etl input bamqc4 shesmu > refiller.json
cat refiller.json | qc-etl build bamqc4 -d /save/dir -c cache_file_name
```

The root directory flag `-d` is optional. It can also be supplied via the `QC_ETL_ROOT_DIRECTORY` environmental
variable or via the refiller (each record must have the key `qcetl_root_dir` with the same value).



## Production Installation
Requires `uv >= 0.11.7`

```bash
git clone https://github.com/oicr-gsi/qc-etl.git
cd qc-etl/

# this will install qc-etl into ~/.local/bin/
uv tool install .
```

### Development Setup, Installation and Maintenance
Code conventions, as set by `black` and `flake8`, need to be followed. A pre-commit hook has been written to make this automated

```
git clone https://github.com/oicr-gsi/qc-etl.git
cd qc-etl/

# Install a development version
uv sync --frozen

# Required for git hook, see .pre-commit-config.yaml
uv run pre-commit install

# To update all dependencies:
uv sync --upgrade && uv run pytest
```

For parser development guidance, see the [QC ETL Developer Guide](DEVELOPER_GUIDE.md).

Type hinting should be used on function and class declarations. This allows for type checking using PyCharm editor or [mypy](http://www.mypy-lang.org/).

Documentation should follow the [Google style guide](http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) and respect the line width of the code (80)

#### Olives and Refillers
Olives and refiller development is done on a dedicated Shesmu instance. The instance creation is waiting for the Vidarr migration to complete.

### Release Procedure

1. Ensure the [CHANGELOG](CHANGELOG.md) is complete and run `release.sh`.
1. Submit the pull request that `release.sh` created, request reviews, and merge to complete the release.

### Environment variables

The following environment variables can be used in QC ETL. If they are not set, the URL values may have to be provided when accessing data or building caches:

| Variable                   | Required?                     | Notes                                                           |
|----------------------------|-------------------------------|-----------------------------------------------------------------|
| `QC_ETL_RUNSCANNER_MASTER_URL` | For building runscanner cache | URL to JSON containing all runscanner runs (/runs/all API call) |
| `QC_ETL_ROOT_DIRECTORY`    | No                            | Root directory of caches                                        |
| `MONGO_URL`                | No                            | URL for MongoDB Pinery source                                   |
| `PINERY_URL`               | No                            | URL for Pinery                                                  |

## Create Cache
Use the `build` method for the desired data source.

Providing the path to an existing cache will turn on incremental caching. Only records that are not present in the existing cache will be parsed and appended, which should speed up caching. Records that are present in the existing cache, but no longer in the input data, will be removed.

```python
# bcl2fastq example

from qcetl.bcl2barcode import Bcl2BarcodeCache
from sqlalchemy import create_engine

# Create database connection (sqlite in memory is convenient for experimenting)
engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
Bcl2BarcodeCache().build(
    [
        {
            "lane": 1,
            "run": "2020-04-20_RUN_ALIAS",
            "path": "/path/to/workflow/output",
            "swid": "12345",
        }
    ],
    engine
)
```

## Access Cache Data
`QCETLCache` provides stable convenience functions for loading caches. The root directory of all the caches needs to be provided to the cache load function, or can be set with the `QC_ETL_ROOT_DIRECTORY` environmental variable.

Note that the call to `QCETLCache()` returns an object that has access to the available caches. Calling `QCETLCache().specific_cache` returns an object containing metadata about the `specific_cache` cache. To access the cache itself, call `QCETLCache().specific_cache.name_of_cache`.

```python
from qcetl import QCETLCache, QCETLColumns

# Stop if the cache doesn't exist
assert QCETLCache('/path/to/root/dir').test_connection()

# Get clusters info for a run
# Loading is done with default parameters, use QCETLCache.load for full control

run_info = QCETLCache('/path/to/root/dir').bcl2barcode.run_summary

# If the QC_ETL_ROOT_DIRECTORY environment variable were set,
# this shorter form could be used to get indices info:
index_info = QCETLCache().bcl2barcode.bcl2barcode

# Loading valid columns does not require path to cache
cols = QCETLColumns().bcl2fastq.run_summary

# Use `keys()` to get names of class variables that are available. `values()`
# returns the string columns of the DataFrame. `asdict()` shows the
# relationship between the two
cols.keys()

# Get runs that have more than 1 billion clusters
print(run_info.loc[run_info[cols.TotalClusters] > 200000000, cols.Index1])
```

In the example above, `bcl2fastq` contains two caches: `known` and `unknown`. A cache item containing only a single cache, like `rnaseqqc` would be accessed like so:

```python
from qcetl import QCETLCache

rnaseqqc = QCETLCache().rnaseqqc2.rnaseqqc2
```

Loading examples can be seen in the [Dashi](https://github.com/oicr-gsi/dashi) project.

### Loading From Multiple Sources

Caches may be stored in multiple independent locations. The `QCETLMultiCache` class can be used to laod the raw list of DataFrames or collapse them.

```python
from qcetl import QCETLMultiCache

caches = QCETLMultiCache(["/path/cache/root1", "/home/cache/root2"])

# Stop if any of the caches are missing
assert all(caches.test_connection())

# If you want all data for one schema version (uses latest version by default)
ver = caches.load_same_version("fastqc")

# A list of all DataFrames (in case all data is required)
all_df = ver.fastqc

# Collapsing drops duplicates based on cache unique keys, keeping the record from the source path first specified
# The "fastqc" string refers to the table being loaded
collapsed_df = ver.unique("fastqc")

# If you want to ignore missing tables from any of the sources
callapsed_df_safe = ver.remove_missing("fastqc").unique("fastqc")
```


## Design Decisions

### Input
File locations and metadata are provided when building the cache (in our case, they are provided by [Shesmu Refillers (dnaSeqQC example)](https://bitbucket.oicr.on.ca/projects/GSI/repos/analysis-config/browse/shesmu/pipedata/etl-dnaseqqc.shesmu)). The input is a list of dictionaries
```python
from_shesmu = [{"swid": 1234, "path": "/path/to/file"}, {"swid": 5678, "path": "/path/to/file2"}]
```

qc-etl deals with refiller changes fairly painlessly. Adding additional refiller fields is fine (qc-etl won't look at fields it does not expect). Removing existing refiller fields is a little more involved, but can be done serially. Code is added to tell the parser how to deal with the value if it's missing (null, "Missing", completely ignore, etc) before the refiller is changed to remove that field.

### Parsing
Each parser is its own independent module containing parsing and caching code. Other optional modules are:

* `validate` module that adds validity columns to the parsed data table. The
* `utility` module that provides convenience functions that act on the parsed data table

Any shared functionality/variables across parsers is in the `common` module. The most import shared functionality is the `Cache` class, which must be implemented by all parsers. The best way to understand `Cache` is to look at the parsers that implement it. Below is an introductory summary.

A new class must provide the following class attributes:
* `name`: A unique name not shared by any other parser. As it will be used to access data created by this parser, make the name clear (no `crs_prs` please)
* `schema_versions`: A parser can have multiple versions of the same data. This allows the parsers to be improved and changed without breaking guarantees. Each column is typed using the [Shesmu types](https://github.com/oicr-gsi/shesmu/blob/master/language.md).
```python
schema_example = {
    1: { # schema version
        "first_table": { # Inputs can lead to more than one table
            "Column1": "i" # Column name and type
        }
    }
}
```
* `columns`: Pandas column names are strings, but raw column strings should not be used directly in the code. Rather, the cache column should be defined as a child class which inherits from `BaseColumn`.

```python
from qcetl.column import BaseColumn


# A table with two columns
class TableColumn(BaseColumn):
    FirstColumn = "first column"
    SecondColumn = "second_column"  # Alas, there is little consistency is column names


# Link `first_table` to the columns it has
columns = {1: {"first_table": TableColumn}}
```
* `input_format`: The key names and types of the values that Shesmu is providing.
```python
input_format = {"file": "p", "swid": "s"}
# Given this input format, an example of valid Shesmu input would be
from_shesmu = [{"swid": 1234, "file": "/path/to/file"}, {"swid": 5678, "file": "/path/to/file2"}]
```
* `primary_key`: What combination of columns make a unique key. This needs to be specified for each version of the schema and for each table.
```python
primary_key = {
    1: { # Primary keys may differ between versions
        "first_table": ["column_name_1", "column_name_2"] # Two columns as primary key
    }
}
```
* `input_key`: Links which table row comes from which Shesmu input. This allows the parser to determine which Shesmu input has already been parsed, which is new, and which needs to be deleted. `{1: (shesmu_key_name, parsed_table_column_name)}` means that for schema version 1, the value for Shesmu key `shesmu_key_name` is stored in the cache column `parsed_table_column_name`

The main function to implement is `parse_single_record` which returns a `DataFrame` for a single Shesmu input.

The `add_shesmu_metadata` function returns which Shesmu input data will be inserted into the DataFrame when `build` is called. This is most commonly used to add the File SWID value to parsed tables to uniquely linked parsed data to Shesmu input. Returning `{}` from this function means nothing is inserted.

#### Parsing Errors
Exceptions in parsing will not abort building of a cache. The failed input record will be logged (if logger is provided) and the failed Shesmu input will be returned by the `build` function.

### Loading
The `load` function determines how a stored cache is loaded. The default implementation is to return the stored data. One of the design principles is that parsed data is not modified during storage. It is sometimes the case that stored data is known to be wrong or needs to be fixed. The `load` function accepts the ` CleaningRules` object, which allows the function to know if data needs to be cleaned/fixed before being returned. The `load_fixer_function` can be overloaded when DataFrames need to be fixed/filtered based on the `CleaningRules`.

### Storage
The `build` command dumps data into a SQLAlchemy `Engine` object, which abstracts storing data in various popular SQL databases. In other words, qc-etl is provided a database connection, but does not care what that database is. The cache schemas are simple enough that all common databases should be able to store them.

### Versioning
A cache is always versioned. Specifying a version for any parser guarantees table names, column names, and column types consistency.

### Testing
Each parser is tested using files stored in this repositories `test` folder. Testing is done via the `test.cachechecker` interface

```python
import test.cachechecker
import qcetl.bcl2barcode


def tests_bcl2barcode():
    test.cachechecker.check(
        qcetl.bcl2barcode.Bcl2BarcodeCache(),  # The parser to test
        [  # Mock Shesmu input
            {
                "run": "181109_A00469_0016_AHGC37DMXX",
                "lane": 1,
                "path": "test/files/bcl2barcode.counts.gz",
                "swid": "SWID",
            }
        ],
        {  # Table names of produced caches and the golden files to test them against
            "bcl2barcode": "test/files/bcl2barcode.csv",
            "run_summary": "test/files/bcl2barcode_run_summary.csv",
        },
    )
```

If the golden files do not exist, they are automatically generated when the test is first run. It's up to the human to open up the automatically generated golden file and ensure it matches human expectations.

### Nested Source Data
Nested source data must be flattened. Various approaches are used:
* Edit column names and/or create new columns
* Split data into multiple tables
* Use [long](http://jonathansoma.com/tutorials/d3/wide-vs-long-data/) data table format

### Validity
Records can be invalid for many reasons:
* Nonsensical (runs that have been running for years)
* Known to be wrong (RNASeQC using TopHat aligner)

Cached data is never altered*. Rather, validity columns are added to the cached DataFrame. When the cache is loaded, data known to be nonsensical is set to `NaN` and a warning message is logged. The user can disable this to return the original data

\* Data is altered when it prevents proper type assignment: `str('56%')` is converted to `int(56)`

## Automatic Documentation
To generate automatic documentation:


    sudo apt-get install python3-sphinx python3-sphinx-rtd-theme
    make -C docs html
    xdg-open docs/_build/html/index.html
