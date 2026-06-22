from typing import Dict

from pandas import DataFrame

from qcetl.common import Cache
from qcetl.common.utility import TimeOut
from qcetl.column import BaseColumn
import pytest
import sqlalchemy
import pandas

"""
Check that the database backed cache behaves as expected using a simple cache class
"""


class Column(BaseColumn):
    swid = "swid"
    float = "float"
    int = "int"
    string = "string"


class SimpleCache(Cache):
    def __init__(self):
        self.name = "test"
        self.schema_versions = {
            1: {"table": {"swid": "s", "float": "f", "int": "i"}},
            2: {"simple_table": {"swid": "s", "string": "s"}},
        }
        self.input_format = {"swid": "s", "path": "p"}
        self.columns = {1: {"table": Column}, 2: {"simple_table": Column}}
        self.primary_key = {
            1: {"table": ["swid"]},
            2: {"simple_table": ["swid"]},
        }
        self.input_key = {1: ("swid", Column.swid), 2: ("swid", Column.swid)}


class SimpleCacheV2Only(Cache):
    def __init__(self):
        self.name = "test"
        self.schema_versions = {
            2: {"simple_table": {"swid": "s", "string": "s"}}
        }
        self.input_format = {"swid": "s", "path": "p"}
        self.columns = {2: {"simple_table": Column}}
        self.primary_key = {2: {"simple_table": ["swid"]}}
        self.input_key = {2: ("swid", Column.swid)}

    def add_shesmu_metadata(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, Dict[str, str]]:
        return {"simple_table": {}}

    def parse_single_record(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, DataFrame]:
        return {
            "simple_table": DataFrame(
                {
                    "swid": [single_input["swid"]],
                    "string": [single_input["string"]],
                }
            )
        }


class SimpleDifferentCache(Cache):
    def __init__(self):
        self.name = "different_test"
        self.schema_versions = {
            2: {"simple_table": {"swid": "s", "string": "s"}}
        }
        self.input_format = {"swid": "s", "path": "p"}
        self.columns = {2: {"simple_table": Column}}
        self.primary_key = {2: {"simple_table": ["swid"]}}
        self.input_key = {2: ("swid", Column.swid)}


@pytest.fixture
def empty_db():
    engine = sqlalchemy.create_engine(
        "sqlite+pysqlite:///:memory:", echo=False, future=True
    )
    SimpleCache().create_tables(engine)
    return engine


@pytest.fixture
def simple_db():
    engine = sqlalchemy.create_engine(
        "sqlite+pysqlite:///:memory:", echo=False, future=True
    )
    SimpleCache().create_tables(engine)
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    table = metadata.tables["test_table_1"]
    simple = metadata.tables["test_simple_table_2"]
    with engine.connect() as conn:
        stm = sqlalchemy.insert(table).values(
            [
                {"swid": "one", "float": 1.0, "int": 1},
                {"swid": "two", "float": 2.0, "int": 2},
            ],
        )
        conn.execute(stm)
        stm = sqlalchemy.insert(simple).values(
            [
                {"swid": "one", "string": "one"},
                {"swid": "two", "string": "two"},
            ],
        )
        conn.execute(stm)
        conn.commit()
    return engine


@pytest.fixture
def simplev2only_db():
    engine = sqlalchemy.create_engine(
        "sqlite+pysqlite:///:memory:", echo=False, future=True
    )
    SimpleCacheV2Only().create_tables(engine)
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    simple = metadata.tables["test_simple_table_2"]
    with engine.connect() as conn:
        stm = sqlalchemy.insert(simple).values(
            [
                {"swid": "one", "string": "one"},
                {"swid": "two", "string": "two"},
            ],
        )
        conn.execute(stm)
        conn.commit()
    return engine


def test_create_tables():
    cache = SimpleCache()
    blank_db = sqlalchemy.create_engine(
        "sqlite+pysqlite:///:memory:", echo=False, future=True
    )
    cache.create_tables(blank_db)
    meta = sqlalchemy.MetaData()
    meta.reflect(blank_db)
    tables = meta.tables.keys()
    assert len(tables) == 2
    assert cache.get_table_name(1, "table") in tables
    assert cache.get_table_name(2, "simple_table") in tables


def test_delete_removed_input(simple_db):
    cache = SimpleCache()
    cache.delete_removed_input([{"swid": "one"}], 1, simple_db)
    with simple_db.connect() as conn:
        df = pandas.read_sql_table(cache.get_table_name(1, "table"), conn)
        assert len(df) == 1


def test_filter_new_input(simple_db):
    cache = SimpleCache()
    new = cache.filter_new_input(
        [{"swid": "one"}, {"swid": "two"}, {"swid": "three"}], 1, simple_db
    )
    assert new == [{"swid": "three"}]


def test_filter_stale_rows(simple_db):
    cache = SimpleCache()
    stale = cache.filter_stale_rows([{"swid": "one"}], 1, simple_db)
    assert stale == {"two"}


def test_insert_record(empty_db):
    cache = SimpleCache()
    records = pandas.DataFrame(
        {"swid": ["one", "two"], "float": [1.2, 2.1], "int": [4, 2]}
    )
    cache.insert_sqlite_record({"table": records}, 1, empty_db)
    with empty_db.connect() as conn:
        df = pandas.read_sql_table(cache.get_table_name(1, "table"), conn)
        pandas.testing.assert_frame_equal(records, df)


def test_deletion_of_deprecated_versions(simple_db):
    updated_cache = SimpleCacheV2Only()
    meta_initial = sqlalchemy.MetaData()
    meta_initial.reflect(simple_db)
    assert len(meta_initial.tables) == 2
    deleted = updated_cache.delete_deprecated_tables(simple_db)
    assert deleted == ["test_table_1"]
    meta_after_build = sqlalchemy.MetaData()
    meta_after_build.reflect(simple_db)
    assert len(meta_after_build.tables) == 1


def test_multiple_caches_in_one_db(simple_db):
    meta = sqlalchemy.MetaData()
    cache = SimpleCache()
    new_cache = SimpleDifferentCache()
    new_cache.create_tables(simple_db)
    meta.reflect(simple_db)
    assert len(meta.tables) == 3
    with simple_db.connect() as conn:
        # Existing caches haven't been touched
        df = pandas.read_sql_table(cache.get_table_name(1, "table"), conn)
        assert len(df) == 2
        df = pandas.read_sql_table(
            cache.get_table_name(2, "simple_table"), conn
        )
        assert len(df) == 2
        # New cache was inserted
        df = pandas.read_sql_table(
            new_cache.get_table_name(2, "simple_table"), conn
        )
        assert len(df) == 0


def test_timeout(empty_db):
    cache = SimpleCacheV2Only()
    rslt = cache.build(
        [{"swid": f"{x}", "string": "peace"} for x in range(10)],
        empty_db,
        timeout=TimeOut(0.1),
    )
    assert not rslt.timeout
    assert len(cache.get_stored_input(2, empty_db)) == 10

    rslt = cache.build(
        [{"swid": f"{x}", "string": "peace"} for x in range(10000)],
        empty_db,
        timeout=TimeOut(0.1),
    )
    assert rslt.timeout
    assert len(cache.get_stored_input(2, empty_db)) < 10000


def test_build_return(simplev2only_db):
    cache = SimpleCacheV2Only()
    r = cache.build(
        [
            {"swid": "one", "string": "one"},
            {"swid": "three", "string": "three"},
        ],
        simplev2only_db,
    )
    assert r.parsed == 1
    assert r.failed == []
    assert r.stale == {"two"}
    assert not r.timeout
