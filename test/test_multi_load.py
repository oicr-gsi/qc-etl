from qcetl.common import Cache, SQLiteCacheFile, MultiCacheFromVersion
from qcetl.column import BaseColumn
import pytest
import pandas
import sqlalchemy


class Column(BaseColumn):
    swid = "swid"
    float = "float"
    int = "int"


class SimpleCache(Cache):
    def __init__(self):
        self.name = "test"
        self.schema_versions = {
            1: {"table": {"swid": "s", "int": "i"}},
            2: {"simple_table": {"swid": "s", "int": "i", "float": "f"}},
        }
        self.input_format = {"swid": "s", "path": "p"}
        self.columns = {1: {"table": Column}, 2: {"simple_table": Column}}
        self.primary_key = {
            1: {"table": ["swid"]},
            2: {"simple_table": ["swid"]},
        }
        self.input_key = {1: ("swid", Column.swid), 2: ("swid", Column.swid)}

    def parse_single_record(self, single_input, schema_version):
        if schema_version == 1:
            return {
                "table": pandas.DataFrame(
                    {
                        "int": [single_input["int"]],
                    }
                )
            }
        elif schema_version == 2:
            return {
                "simple_table": pandas.DataFrame(
                    {
                        "int": [single_input["int"]],
                        "float": [single_input["float"]],
                    }
                )
            }

    def add_shesmu_metadata(self, single_input, schema_version):
        name = "table" if schema_version == 1 else "simple_table"
        return {
            name: {
                Column.swid: single_input["swid"],
            }
        }


@pytest.fixture(scope="session")
def multi_cache_source(tmp_path_factory):
    cache = SimpleCache()
    c = tmp_path_factory.mktemp("caches")
    one = str(c / "one.sqlite")
    two = str(c / "two.sqlite")
    engine_one = sqlalchemy.create_engine("sqlite:///" + one, future=True)
    engine_two = sqlalchemy.create_engine("sqlite:///" + two, future=True)

    cache.build(
        [
            {"swid": "one", "int": 1, "float": 1.0},
            {"swid": "two", "int": 2, "float": 2.0},
        ],
        engine_one,
    )
    cache.build(
        [
            {"swid": "two", "int": 2, "float": 2.5},
            {"swid": "three", "int": 3, "float": 3.0},
        ],
        engine_two,
    )

    return one, two


def test_multi_single_version_load(multi_cache_source):
    one, two = multi_cache_source
    one = SQLiteCacheFile(str(one), "test", 2, lambda x, name: x)
    two = SQLiteCacheFile(two, "test", 2, lambda x, name: x)
    multi = MultiCacheFromVersion([one, two], {"simple_table": ["swid"]})
    assert multi.schema_versions() == [2, 2]
    df = multi.unique("simple_table")
    assert len(df) == 3
    # Confirm the right row was dropped (second cache had a 3.5 instead of 3.0)
    assert set(df["float"]) == {1.0, 2.0, 3.0}
