from dataclasses import dataclass
import datetime
import logging
from typing import Dict, Type, List, Callable, Union, Tuple, Set, Any, Optional

import numpy
import os
import pandas
from pandas import DataFrame
import traceback
import sqlalchemy
import sqlalchemy.exc

from qcetl.column import ColumnStore, BaseColumn
from qcetl.common.utility import (
    safe_pandas_concat,
    add_custom_column,
    TimeOut,
)
from qcetl.common.exceptions import InvalidRecordError


class CacheFile:
    """
    Interface for accessing caches
    """

    def __getattr__(self, name) -> DataFrame:
        """
        Get a cache by name. Use the normal dot accessor to get a table

        Args:
            name: the name of the table

        Returns: a dataframe for this table
        """
        raise NotImplementedError

    def exists(self, name) -> bool:
        """
        Does the table exist

        Args:
            name:  Name of the table

        Returns: If the table exist

        """
        raise NotImplementedError

    def version(self) -> str:
        """
        Get a version for this file. It includes both a schema version and data version.
        Returns: a version string

        """
        raise NotImplementedError

    def build_time(self) -> Optional[datetime.datetime]:
        """
        Get the build time of this cache.
        Returns: a date
        """
        raise NotImplementedError

    def schema_version(self) -> int:
        """
        Which schema version is being loaded

        Returns: A int version

        """
        raise NotImplementedError


class MultiCacheSource:
    """
    Interface for interacting with a cache that collated from multiple sources.

    There is no one way to collapse caches coming from multiple locations. That becomes doubly true if
    schema versions don't match between them. The most explicit solution is to return a list of the
    DataFrames from the specified sources.

    The `collapse` function returns one DataFrame and needs to be extended for each approach.
    """

    _caches: List[CacheFile]

    def __getattr__(self, name) -> List[DataFrame]:
        """
        Get caches by name. Use the normal dot accessor to get a table.
        No collapsing is done on these DataFrames

        Args:
            name: the name of the table.

        Returns: a list of DataFrames for this table in the same order as the specified sources
        """
        return [getattr(c, name) for c in self._caches]

    def versions(self) -> List[str]:
        """
        Get a version for this file. It includes both a schema version and data version.
        Returns: a list of versions for this cache in the same order as the specified sources

        """
        return [c.version() for c in self._caches]

    def schema_versions(self) -> List[int]:
        """
        Which schema version is being loaded

        Returns: a list of schema versions for this cache in the same order as the specified sources
        """
        return [c.schema_version() for c in self._caches]

    def build_times(self) -> List[datetime.datetime]:
        """
        Get the build time of this cache.
        Returns: a list of dates for this cache in the same order as the specified sources
        """
        return [c.build_time() for c in self._caches]

    def unique(self, name: str) -> DataFrame:
        """
        Collapse the multiple sources into one DataFrame without duplicates.
        Each implementation will have its own approach.

        Args:
            name: The name of the table

        Returns: A single DataFrame

        """
        raise NotImplementedError


LoggerCreator = Callable[[str], Union[logging.Logger, None]]


class CleaningRules:
    """
    Attributes:
        collapse_bcl2barcode_merged_flowcell (bool): bcl2barcode produces duplicated
            lane info when the flowcell lanes are merged. Remove them.
        fix_picard_duplicate_percentage (bool): Picard's PERCENT_DUPLICATION
            column is actually a fraction. Multiply this column by 100.
        mark_invalid_cluster_nan (bool): Invalid flow cell Cluster values will
            be converted to NaN
        mark_invalid_cluster_pf_nan (bool): Invalid flow cell Cluster PF values
            will be converted to NaN
        mark_invalid_healthstatus_failed (bool): Invalid flow cell health status
            will be set to failed
        remove_duplicate_runlanelib (bool): Remove record with duplicated
            run, lane, library combination, keeping the last modified one
        remove_validate_columns (bool): Should the metadata columns
            containing validation information be removed
        normalize_downsampling (bool):
    """

    def __init__(self, default: bool = True):
        """
        Args:
            default: By default, sets all cleaning options to on (True)
        """
        self.collapse_bcl2barcode_merged_flowcell = default
        self.fix_picard_duplicate_percentage = default
        self.mark_invalid_cluster_nan = default
        self.mark_invalid_cluster_pf_nan = default
        self.mark_invalid_healthstatus_failed = default
        self.remove_duplicate_runlanelib = default
        self.remove_invalid_indexsampleid = default
        self.remove_validate_columns = default
        self.normalize_downsampling = default


@dataclass
class BuildResults:
    """
    Results of a build process
    """

    parsed: int  # How many records were parsed
    failed: List[dict]  # Shesmu entries that failed to build
    stale: Set[str]  # Keys of records that have become stale
    timeout: bool  # Did building time out


class Cache:
    """
    Saving and loading a cache stored in SQLite3.
    """

    # Unique name for the cache
    name: str
    # {version: {table name: {column name: column type}}}
    schema_versions: Dict[int, Dict[str, Dict[str, str]]]
    # Shesmu sends a list of dicts. This states what type (value) each key is
    input_format: Dict[str, str]
    # For each version, link the table to the column enum
    columns: Dict[int, Dict[str, Type[BaseColumn]]]
    # Dict[version, Dict[table name, List[columns to use as primary keys]]]
    primary_key: Dict[int, Dict[str, List[str]]]
    # For each version, which Shesmu key uniquely matches the produced table column
    input_key: Dict[int, Tuple[str, str]]

    def add_shesmu_metadata(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, Dict[str, str]]:
        """
        Returns what metadata columns need to be added to the DataFrames produced
        from a single record

        Args:
            single_input: The metadata from Shesmu
            schema_version: In case different schema versions require different metadata

        Returns: For each DataFrame name, the key is the column name and the value
            is the value of that column

        """
        raise NotImplementedError

    def add_sql_metadata_for_version(
        self, version: int, metadata: sqlalchemy.MetaData
    ):
        """
        For the specified version, populate the SQLAlchemy metadata object with the
        proper tables, columns, and their types.

        Args:
            version: Schema version
            metadata: The metadata table to populate
        """
        schema = self.schema_versions[version]
        types = {
            "as": sqlalchemy.JSON,
            "b": sqlalchemy.Boolean,
            "d": sqlalchemy.DateTime,
            "f": sqlalchemy.Float,
            "i": sqlalchemy.BigInteger,
            "p": sqlalchemy.Text,
            "qf": sqlalchemy.Float,
            "qi": sqlalchemy.Float,
            "qp": sqlalchemy.Text,
            "qs": sqlalchemy.Text,
            "s": sqlalchemy.Text,
        }

        for table in schema:
            name = self.get_table_name(version, table)
            sqltable = sqlalchemy.Table(name, metadata)
            key_list = self.primary_key[version][table]
            for col, col_type in schema[table].items():
                primary = col in key_list
                sqltable.append_column(
                    sqlalchemy.Column(col, types[col_type], primary_key=primary)
                )

    def available_versions(self) -> Set[int]:
        """
        Which schema versions can be used with this cache?

        Returns:
        """
        return set(self.schema_versions)

    def build(
        self,
        input_data: List[dict],
        engine: sqlalchemy.engine.Engine,
        archive_mode: bool = False,
        timeout: Optional[TimeOut] = None,
    ) -> BuildResults:
        """
        Builds the database from the Shesmu input.
        * If input already in database, it is skipped
        * If input is new, parse and insert into database
        * If record in database is no longer in input, remove from database

        Args:
            input_data: Shesmu list of inputs
            engine: The database engine
            archive_mode: If True, no records will be deleted. If False, records will be deleted if they are no longer
                in the Shesmu input or if the schema version has been removed from the cache.
            timeout: When to stop iterating over records and return

        Returns: Records that failed to be inserted into database

        """
        logger = logging.getLogger("qcetl.build")
        logger.info(
            "{}: Preparing to build cache from {} input records".format(
                self.name, len(input_data)
            )
        )
        failed_inputs = []
        missing_file_err = 0
        num_records_parsed = 0
        stale = set()
        timeout_bool = False
        # Save to call, as nothing will happen if database already has tables
        self.create_tables(engine)

        if not archive_mode:
            deleted = self.delete_deprecated_tables(engine)
            if deleted:
                logger.info(
                    "{}: Deprecated tables were deleted: {}".format(
                        self.name, deleted
                    )
                )

        for version in self.schema_versions:
            logger.info(
                "{}: Parsing version {} records".format(self.name, version)
            )
            if timeout is not None and timeout.timeout():
                logger.info(
                    "Skipping schema version {} due to timeout".format(version)
                )
                break

            if not archive_mode:
                to_remove = self.filter_stale_rows(input_data, version, engine)
                stale.update(to_remove)
                if len(to_remove) > 0:
                    logger.info(
                        "{}: {} cached records are stale and will be deleted".format(
                            self.name, len(to_remove)
                        )
                    )
                self.delete_removed_input(input_data, version, engine)

            new_input = self.filter_new_input(input_data, version, engine)

            logger.info(
                "{}: {} input records are new".format(self.name, len(new_input))
            )
            if len(new_input) == 0:
                logger.info(
                    "{}: No new records. Nothing to do".format(self.name)
                )

            for record in new_input:
                if timeout is not None and timeout.timeout():
                    logger.info(
                        "Parsing timed out after {} records".format(
                            num_records_parsed
                        )
                    )
                    timeout_bool = True
                    break

                try:
                    num_records_parsed += 1
                    df = self.parse_single_record(record, version)

                    meta_data = self.add_shesmu_metadata(record, version)
                    for table_name in df:
                        table = df[table_name]
                        table_metadata = meta_data[table_name]
                        for col in table_metadata:
                            value = table_metadata[col]
                            # If Shesmu gives a list, it has to be nested
                            # Pandas thinks each element goes into its own cell, but we want the list to go in one cell
                            if isinstance(value, list):
                                value = [value] * len(table)
                            add_custom_column(table, col, value)
                        table = table.astype(
                            self.get_dtypes(version)[table_name]
                        )
                        df[table_name] = table

                    self.insert_sqlite_record(df, version, engine)
                except (FileNotFoundError, PermissionError) as e:
                    logger.error("File cannot be read: {}".format(e))
                    missing_file_err += 1
                except InvalidRecordError as e:
                    logger.critical(
                        "Record cannot be parsed from input {}: {}".format(
                            record, e
                        )
                    )
                    failed_inputs.append(record)
                except Exception:
                    logger.critical(
                        "Unknown ETL error with input {}. Full trace\n{}".format(
                            record, traceback.format_exc()
                        )
                    )
                    failed_inputs.append(record)

            if missing_file_err > 0:
                logger.warning(
                    "{} file(s) were excluded as they cannot be read.".format(
                        missing_file_err
                    )
                )

            logger.info(
                "Finished parsing records for schema version {}".format(version)
            )

        logger.info("Finished parsing records")
        return BuildResults(
            num_records_parsed, failed_inputs, stale, timeout_bool
        )

    def cache_folder_name(self) -> str:
        """
        The name of the folder where caches are saved by default.

        Returns:

        """
        return self.name

    def create_tables(self, engine: sqlalchemy.engine.Engine):
        """
        Save to call on existing databases, as existing tables/columns won't be
        impacted.

        Args:
            engine: The database connection.

        Returns:

        """
        metadata = self.generate_sql_metadata()
        metadata.create_all(engine)

    def delete_all_tables(self, engine: sqlalchemy.engine.Engine):
        """
        Deletes all tables associated with this cache

        Args:
            engine: The database connection.

        """
        meta = sqlalchemy.MetaData()
        meta.reflect(engine)
        for table in self.get_tables_from_database(meta):
            meta.tables[table].drop(engine)

    def delete_deprecated_tables(
        self, engine: sqlalchemy.engine.Engine
    ) -> List[str]:
        """
        Drops tables from versions that are no longer supported.

        Args:
            engine: The database connection.

        Returns: The deleted tables

        """
        meta = sqlalchemy.MetaData()
        meta.reflect(engine)
        supported = set(self.schema_versions)

        deleted = []
        for table in self.get_tables_from_database(meta):
            if self.get_table_version(table) not in supported:
                deleted.append(table)
                meta.tables[table].drop(engine)

        return deleted

    def delete_removed_input(
        self,
        input_data: List[dict],
        version: int,
        engine: sqlalchemy.engine.Engine,
    ):
        """
        Remove any records that are in the database, but are not in the Shesmu input

        Args:
            input_data: Shesmu input data
            version: Which version to consider
            engine: Database connection

        Returns:

        """
        meta = sqlalchemy.MetaData()
        meta.reflect(engine)
        column = self.input_key[version][1]
        input_key = self.input_key[version][0]
        keep = [x[input_key] for x in input_data]
        with engine.connect() as conn:
            for table in self.get_tables_from_database(meta):
                t = meta.tables[table]
                if self.get_table_version(table) != version:
                    continue
                stm = sqlalchemy.delete(t).where(t.c[column].not_in(keep))
                conn.execute(stm)
            conn.commit()

    def filter_new_input(
        self,
        input_data: List[dict],
        version: int,
        engine: sqlalchemy.engine.Engine,
    ) -> List[dict]:
        """
        Filter for Shesmu input that isn't in the database.

        If at least one table in the database contains data from the input, it is
        marked as not new.

        Args:
            input_data: Shesmu data
            version: Which version to consider
            engine: Database connection

        Returns: Subset of the Shesmu input

        """
        input_key = self.input_key[version][0]
        stored_keys = self.get_stored_input(version, engine)
        return [x for x in input_data if x[input_key] not in stored_keys]

    def filter_stale_rows(
        self,
        input_data: List[dict],
        version: int,
        engine: sqlalchemy.engine.Engine,
    ) -> Set[Any]:
        """
        Filter for cached rows that no longer exist in the Shesmu input

        Args:
            input_data: Shesmu data
            version: Which version to consider
            engine: Database connection

        Returns: The input keys stored in the caches

        """
        input_key = self.input_key[version][0]
        shesmu_inputs = {x[input_key] for x in input_data}
        stored_keys = self.get_stored_input(version, engine)
        return {x for x in stored_keys if x not in shesmu_inputs}

    def generate_sql_metadata(self) -> sqlalchemy.MetaData:
        """
        Create a SQLAlchemy metadata object given the cache shema

        Returns:

        """
        metadata = sqlalchemy.MetaData()
        for version in self.schema_versions:
            self.add_sql_metadata_for_version(version, metadata)
        return metadata

    def get_columns(self, schema_version: int = None) -> ColumnStore:
        """
        Get the column information for a schema version

        Args:
            schema_version:  the version to select; if absent, the latest
                version is used

        Returns: a description of the columns

        """
        if schema_version is None:
            schema_version = self.latest_version()

        return ColumnStore(self.columns[schema_version])

    def get_dtypes(
        self, schema_version: int = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create dictionary for DataFrame type conversation using `pandas.astype`.

        Args:
            schema_version: Schema version (latest by default)

        Returns:

        """
        # object type is used instead of str as it allows mixed types
        # This allows str columns to contain numpy.nan (float)
        types = {
            "as": object,
            "b": bool,
            "d": "datetime64[ns]",
            "f": float,
            "i": int,
            "p": object,
            "qf": float,
            "qi": float,  # Pandas missing value forces cast to float
            "qp": object,
            "qs": object,
            "s": object,
        }

        if schema_version is None:
            schema_version = self.latest_version()

        result = {}
        schema = self.schema_versions[schema_version]
        for name in schema:
            d = {k: types[v] for k, v in schema[name].items()}
            result[name] = d

        return result

    def get_stored_input(
        self,
        version: int,
        engine: sqlalchemy.engine.Engine,
    ) -> Set[Any]:
        """
        Return all input keys currently stored in the cache.

        Used to compare what Shesmu sends over with what's stored.
        If an input key is stored in at least one table, it is returned here.

        Args:
            version: Which version to consider
            engine: Database connection

        Returns: Subset of the Shesmu input

        """
        meta = sqlalchemy.MetaData()
        meta.reflect(engine)
        column = self.input_key[version][1]
        stored_keys = set()
        with engine.connect() as conn:
            for table in self.get_tables_from_database(meta):
                t = meta.tables[table]
                if self.get_table_version(table) != version:
                    continue
                stm = sqlalchemy.select(t.c[column])
                table_keys = [x[0] for x in conn.execute(stm)]
                stored_keys = stored_keys.union(table_keys)

        return stored_keys

    def get_table_name(self, schema_version: int, table: str):
        """
        Generate the name of the table as stored in the database

        Args:
            schema_version: Version
            table: Name of the table as stored in the `Cache` object

        Returns:

        """
        return "_".join([self.name, table, str(schema_version)])

    def get_tables(self, schema_version: int) -> Dict[str, Dict[str, str]]:
        """
        Get the tables for a particular schema version

        Args:
            schema_version: the version to select

        Returns: a dictionary of tables and their columns and column types

        """
        return self.schema_versions.get(schema_version, {})

    def get_tables_from_database(self, meta: sqlalchemy.MetaData) -> Set[str]:
        """
        Pull out the tables for this cache from the database

        Args:
            meta: The metadata object for this database

        Returns: The table names stored for this cache
        """
        result = set()
        for table in meta.tables:
            if table.startswith(self.name):
                result.add(table)
        return result

    @staticmethod
    def get_table_version(table_name: str) -> int:
        return int(table_name.rsplit("_", 1)[-1])

    def latest_version(self):
        """
        Get the latest schema version of the cache
        """
        return max(self.schema_versions.keys())

    @staticmethod
    def load_fixer_function(
        cleaning_rules: CleaningRules, log_creator: LoggerCreator
    ) -> Callable[[DataFrame, str], DataFrame]:
        """
        Cached data is not changed at all (aside from casting it to the correct type). When loading, known errors
        should be fixed by default. The most famous of these is Picard's MarkDuplicates PERCENT_DUPLICATION field
        which is actually a fraction.

        The returned function takes the DataFrame and its table name and using the CleaningRules fixes it. The logger
        can be used to inform user of what has been done.

        By default just returns the DataFrame supplied

        Args:
            cleaning_rules: How to fix the DataFrame
            log_creator: Where to log what has been done

        Returns:

        """
        return lambda df, name: df

    def load(
        self,
        schema_version: int,
        path: str,
        cleaning_rules: CleaningRules,
        log_creator: LoggerCreator,
    ) -> CacheFile:
        """
        Load a cache from disk

        Args:
            schema_version: the schema version
            path: the path on disk to the cache file
            cleaning_rules: any desired behaviour for removing bad data
                from the loaded data
            log_creator: a function which creates a logger for
                cleaning-related output

        Returns: a cache file interface to access the tables

        """
        return SQLiteCacheFile(
            path,
            self.name,
            schema_version,
            self.load_fixer_function(cleaning_rules, log_creator),
        )

    def load_postgres(
        self,
        schema_version: int,
        root_dir: str,
        url: str,
        cleaning_rules: CleaningRules,
        log_creator: LoggerCreator,
    ) -> CacheFile:
        """
        Load a cache from a Postgres database

        Args:
            schema_version: the schema version
            root_dir: the path at which the disk files will be stored
            url: URL of the database
            cleaning_rules: any desired behaviour for removing bad data
                from the loaded data
            log_creator: a function which creates a logger for
                cleaning-related output

        Returns: a cache file interface to access the tables

        """
        return PostgresCacheFile(
            root_dir,
            url,
            self.name,
            schema_version,
            self.load_fixer_function(cleaning_rules, log_creator),
        )

    def insert_sqlite_record(
        self,
        record: Dict[str, DataFrame],
        schema_version: int,
        engine: sqlalchemy.engine.Engine,
    ):
        """
        Assumes the parsed data to be inserted does not exist in the database.

        SQLite is limited to inserting only so many rows * columns (see
        Maximum Number Of Host Parameters In A Single SQL Statement) in one commit.
        This function takes a conservative number of rows to make sure that limit
        isn't reached.

        Args:
            record: The parsed record. One Shesmu input can generate more than one
                DataFrame.
            schema_version: Which schema version is this for.
            engine: Database connection

        Returns:

        """
        max_insert = 500
        with engine.connect() as conn:
            metadata = sqlalchemy.MetaData()
            metadata.reflect(conn)
            rows_inserted = 0
            for table in record:
                name = self.get_table_name(schema_version, table)
                sql_table = metadata.tables[name]
                df = record[table]
                if df.empty:
                    continue
                # No obvious way to iterate over DataFrame in chunks
                for _, chunk in df.groupby(numpy.arange(len(df)) // max_insert):
                    rows_inserted += len(chunk)
                    conn.execute(
                        sqlalchemy.insert(sql_table).values(
                            chunk.to_dict("records")
                        )
                    )
                if rows_inserted >= max_insert:
                    conn.commit()
                    rows_inserted = 0

            conn.commit()

    def match_versions(self, cache_path) -> bool:
        """
        Do the schema versions match between this instance and a stored cache file?

        Args:
            cache_path: The path to the stored cache file

        Returns:

        """
        return self.available_versions() == SQLiteCacheFile.available_versions(
            cache_path
        )

    def parse_single_record(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, DataFrame]:
        """
        Parse a single record into one or more DataFrames

        Args:
            single_input: A single record supplied by Shesmu that matches
                `self.input_format`
            schema_version: Which version to return

        Returns: The key is the name of the DataFrame (from `self.schema_versions`)
            and the associated DataFrame

        """
        raise NotImplementedError


class SQLiteCacheFile(CacheFile):
    """
    A cache file interface backed by an on-disk HDF5 file
    """

    def __init__(self, filename, cache_name, version, filter_function):
        self._engine = sqlalchemy.create_engine("sqlite:///" + filename)
        self._cache_name = cache_name
        last_input = os.path.join(os.path.dirname(filename), "lastinput.json")
        if os.path.exists(last_input):
            self._mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(last_input)
            )
        else:
            self._mtime = None
        self._filter_function = filter_function
        self._version = version

    def __getattr__(self, name) -> DataFrame:
        result = self._filter_function(
            pandas.read_sql_table(self.table_name(name), self._engine), name
        )
        return result

    def exists(self, name) -> bool:
        meta = sqlalchemy.MetaData()
        try:
            meta.reflect(self.engine())
        except sqlalchemy.exc.OperationalError:
            return False
        return self.table_name(name) in meta.tables

    def build_time(self) -> Optional[datetime.datetime]:
        """
        Get the build time of this cache.
        Returns: a date
        """
        return self._mtime

    def engine(self) -> sqlalchemy.engine.Engine:
        return self._engine

    def table_name(self, name) -> str:
        return "{}_{}_{}".format(self._cache_name, name, self._version)

    def version(self) -> str:
        """
        Get a version for this file. It includes both a schema version and data version.
        Returns: a version string

        """
        return "%s (%s)" % (
            self._version,
            self._mtime if self._mtime is not None else "Unknown time",
        )

    def schema_version(self) -> int:
        return self._version

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._engine.dispose()

    @classmethod
    def available_versions(cls, path: str) -> Set[int]:
        """
        Get all available versions at this path.

        Args:
            path: File location of cache file

        Returns:

        """
        engine = sqlalchemy.create_engine("sqlite:///" + path)
        meta = sqlalchemy.MetaData()
        meta.reflect(engine)
        return set(int(x.rstrip("_")[-1]) for x in meta.tables.keys())


class PostgresCacheFile(CacheFile):
    """
    A cache file interface backed by a Postgres database
    """

    def __init__(self, root_dir, url, cache_name, version, filter_function):
        self._engine = sqlalchemy.create_engine("postgresql+psycopg2://" + url)
        self._cache_name = cache_name
        last_input = os.path.join(root_dir, cache_name, "lastinput.json")
        if os.path.exists(last_input):
            self._mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(last_input)
            )
        else:
            self._mtime = None
        self._filter_function = filter_function
        self._version = version

    def __getattr__(self, name) -> DataFrame:
        result = self._filter_function(
            pandas.read_sql_table(self.table_name(name), self._engine), name
        )
        return result

    def exists(self, name) -> bool:
        meta = sqlalchemy.MetaData()
        try:
            meta.reflect(self.engine())
        except sqlalchemy.exc.OperationalError:
            return False
        return self.table_name(name) in meta.tables

    def build_time(self) -> Optional[datetime.datetime]:
        """
        Get the build time of this cache.
        Returns: a date
        """
        return self._mtime

    def engine(self) -> sqlalchemy.engine.Engine:
        return self._engine

    def table_name(self, name) -> str:
        return "{}_{}_{}".format(self._cache_name, name, self._version)

    def version(self) -> str:
        """
        Get a version for this file. It includes both a schema version and data version.
        Returns: a version string

        """
        return "%s (%s)" % (
            self._version,
            self._mtime if self._mtime is not None else "Unknown time",
        )

    def schema_version(self) -> int:
        return self._version

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._engine.dispose()


class MultiCacheFromVersion(MultiCacheSource):
    """
    Get the same cache version from multiple sources. Optionally, drop duplicates.
    """

    def __init__(
        self,
        caches: List[CacheFile],
        deduplicate: Optional[Dict[str, List[str]]] = None,
    ):
        self._caches = caches
        versions = set(self.schema_versions())
        if len(versions) > 1:
            raise ValueError(
                f"all caches must share the same version. got {versions}"
            )
        self.deduplicate = deduplicate

    def unique(self, name: str) -> DataFrame:
        dfs = pandas.concat(getattr(self, name))
        if self.deduplicate is not None:
            return dfs.drop_duplicates(self.deduplicate[name])
        else:
            return dfs

    def remove_missing(self, name: str):
        """
        Removes any caches that are missing the specified table.

        Call this before trying to load data if tables are expected to be missing.

        Args:
            name: Name of table that may be missing

        Returns:
            A new instance with caches that have table missing removed
        """
        filtered_caches = []
        for c in self._caches:
            if c.exists(name):
                filtered_caches.append(c)

        return MultiCacheFromVersion(filtered_caches, self.deduplicate)
