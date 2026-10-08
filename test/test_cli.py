import qcetl
import qcetl.common
import qcetl.column
import pandas
import pytest
import tempfile
import io
import json
import os.path


class Column(qcetl.column.BaseColumn):
    Numbers = "numbers"
    Index = "index"


class NumberTestCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "test_number_cache"
        self.schema_versions = {
            1: {"test_number_cache": {Column.Numbers: "i", Column.Index: "i"}}
        }
        self.columns = {1: {"test_number_cache": Column}}
        self.input_format = {"store": "i", "index": "i"}
        self.primary_key = {1: {"test_number_cache": [Column.Index]}}
        self.input_key = {1: ("index", Column.Index)}

    def load(self, schema_version, path, cleaning_rules, log_creator):
        return qcetl.common.SQLiteCacheFile(
            path, self.name, schema_version, lambda df, name: df
        )

    def parse_single_record(self, single_input, schema_version):
        df = pandas.DataFrame({Column.Numbers: [single_input["store"]]})
        return {1: {"test_number_cache": df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "test_number_cache": {
                Column.Index: single_input["index"],
            }
        }


class IusColumn(qcetl.column.BaseColumn):
    Index = "index"
    Run = qcetl.column.ColumnNames.Run
    Lane = qcetl.column.ColumnNames.Lane
    Barcodes = qcetl.column.ColumnNames.Barcodes


class IusTestCache(qcetl.common.Cache):
    def __init__(self):
        self.name = "test_ius_cache"
        self.schema_versions = {
            1: {
                "test_ius_cache": {
                    IusColumn.Index: "i",
                    IusColumn.Run: "s",
                    IusColumn.Lane: "i",
                    IusColumn.Barcodes: "s",
                }
            }
        }
        self.columns = {1: {"test_ius_cache": IusColumn}}
        self.input_format = {
            "index": "i",
            "run": "s",
            "lane": "i",
            "barcode": "s",
        }
        self.primary_key = {1: {"test_ius_cache": [IusColumn.Index]}}
        self.input_key = {1: ("index", IusColumn.Index)}

    def load(self, schema_version, path, cleaning_rules, log_creator):
        return qcetl.common.SQLiteCacheFile(
            path, self.name, schema_version, lambda df, name: df
        )

    def parse_single_record(self, single_input, schema_version):
        df = pandas.DataFrame({IusColumn.Run: [single_input["run"]]})
        return {1: {"test_ius_cache": df}}[schema_version]

    def add_shesmu_metadata(self, single_input, schema_version):
        return {
            "test_ius_cache": {
                IusColumn.Index: single_input["index"],
                IusColumn.Lane: single_input["lane"],
                IusColumn.Barcodes: single_input["barcode"],
            }
        }


CACHES = (NumberTestCache(),)
IUS_CACHES = (IusTestCache(),)


def test_list(capsys):
    with pytest.raises(SystemExit) as e:
        qcetl.main(["list"], CACHES)
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "test_number_cache\n"


def test_versions(capsys):
    with pytest.raises(SystemExit) as e:
        qcetl.main(["versions", "test_number_cache"], CACHES)
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "1\n"


def test_tables(capsys):
    with pytest.raises(SystemExit) as e:
        qcetl.main(["tables", "test_number_cache"], CACHES)
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "test_number_cache\n"


def test_schema(capsys):
    with pytest.raises(SystemExit) as e:
        qcetl.main(["schema", "test_number_cache", "test_number_cache"], CACHES)
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "numbers\ti\nindex\ti\n"


def test_refill_config(capsys):
    with pytest.raises(SystemExit) as e:
        qcetl.main(
            [
                "refill-config",
                "-d",
                "/root/dir",
                "-i",
                "latest_cache",
                "-b",
                "/usr/bin/qcetl",
                "-n",
                "refiller_name_v1",
                "test_number_cache",
            ],
            CACHES,
        )
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == (
        '{"refiller_name_v1": {"command": "/usr/bin/qcetl build test_number_cache -d /root/dir -i latest_cache '
        '-c ", "parameters": {"store": "i", "index": "i"}}}\n'
    )


def test_build_d_flag(monkeypatch):
    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as e:
            monkeypatch.setattr(
                "sys.stdin", io.StringIO('[{"store": 42, "index": 2}]')
            )
            qcetl.main(["build", "-d", test_dir, "test_number_cache"], CACHES)
        assert e.value.code == 0

    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as e:
            monkeypatch.setattr("sys.stdin", io.StringIO("[]"))
            qcetl.main(["build", "-d", test_dir, "test_number_cache"], CACHES)
        assert e.value.code == 0


def test_build_timeout(monkeypatch):
    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as e:
            inpt = [{"index": x, "store": 42} for x in range(1000)]
            inpt = json.dumps(inpt)
            monkeypatch.setattr("sys.stdin", io.StringIO(inpt))
            qcetl.main(
                [
                    "build",
                    "-d",
                    test_dir,
                    "-t",
                    "1",
                    "-c",
                    "checksum",
                    "test_number_cache",
                ],
                CACHES,
            )
        assert e.value.code == 0
        assert os.path.exists(
            os.path.join(test_dir, "test_number_cache", "checksum.timeout")
        )
        assert os.path.exists(
            os.path.join(test_dir, "test_number_cache", "latest")
        )

        with pytest.raises(SystemExit) as e:
            inpt = [{"index": x, "store": 42} for x in range(10)]
            inpt = json.dumps(inpt)
            monkeypatch.setattr("sys.stdin", io.StringIO(inpt))
            qcetl.main(
                [
                    "build",
                    "-d",
                    test_dir,
                    "-t",
                    "1",
                    "-c",
                    "checksum",
                    "-i",
                    "latest",
                    "test_number_cache",
                ],
                CACHES,
            )
        assert e.value.code == 0
        assert not os.path.exists(
            os.path.join(test_dir, "test_number_cache", "checksum.timeout")
        )


def test_build_files(monkeypatch):
    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as _:
            inpt = [
                {"index": 1, "store": 42},
                {"index": 2, "store": 42},
                {"index": "error"},
            ]
            inpt = json.dumps(inpt)
            monkeypatch.setattr("sys.stdin", io.StringIO(inpt))
            qcetl.main(
                [
                    "build",
                    "-d",
                    test_dir,
                    "-c",
                    "checksum",
                    "test_number_cache",
                ],
                CACHES,
            )
        with open(
            os.path.join(test_dir, "test_number_cache", "checksum.failed.json")
        ) as f:
            fail = json.load(f)
            assert fail == [{"index": "error"}]
        with open(
            os.path.join(test_dir, "test_number_cache", "checksum.stale.json")
        ) as f:
            stale = json.load(f)
            assert stale == []

        with pytest.raises(SystemExit) as _:
            inpt = [{"index": 1, "store": 42}]
            inpt = json.dumps(inpt)
            monkeypatch.setattr("sys.stdin", io.StringIO(inpt))
            qcetl.main(
                [
                    "build",
                    "-d",
                    test_dir,
                    "-c",
                    "checksum2",
                    "-i",
                    "latest",
                    "test_number_cache",
                ],
                CACHES,
            )
        with open(
            os.path.join(test_dir, "test_number_cache", "checksum2.failed.json")
        ) as f:
            fail = json.load(f)
            assert fail == []
        with open(
            os.path.join(test_dir, "test_number_cache", "checksum2.stale.json")
        ) as f:
            stale = json.load(f)
            assert stale == [2]


def test_build_env(monkeypatch):
    with tempfile.TemporaryDirectory() as test_dir:
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", test_dir)
        with pytest.raises(SystemExit) as e:
            monkeypatch.setattr(
                "sys.stdin", io.StringIO('[{"store": 42, "index": 2}]')
            )
            qcetl.main(["build", "test_number_cache"], CACHES)
        assert e.value.code == 0

    with tempfile.TemporaryDirectory() as test_dir:
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", test_dir)
        with pytest.raises(SystemExit) as e:
            monkeypatch.setattr("sys.stdin", io.StringIO("[]"))
            qcetl.main(["build", "test_number_cache"], CACHES)
        assert e.value.code == 0


def test_build_refiller(monkeypatch):
    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as e:
            i = '[{"store": 42, "index": 2, "qcetl_root_dir": "%s"}]' % test_dir
            monkeypatch.setattr("sys.stdin", io.StringIO(i))
            qcetl.main(["build", "test_number_cache"], CACHES)
        assert e.value.code == 0

    with pytest.raises(SystemExit) as e:
        monkeypatch.setattr("sys.stdin", io.StringIO("[]"))
        qcetl.main(["build", "test_number_cache"], CACHES)

    # Check that conflicting root dir exists gracefully
    with tempfile.TemporaryDirectory() as test_dir:
        with pytest.raises(SystemExit) as e:
            i = (
                '[{"store": 42, "index": 2, "qcetl_root_dir": "%s"},'
                '{"store": 42, "index": 2, "qcetl_root_dir": "DIFFERENT"}]'
                % test_dir
            )
            monkeypatch.setattr("sys.stdin", io.StringIO(i))
            qcetl.main(["build", "test_number_cache"], CACHES)
        # assert e.value.code == 1 # TODO: This passes locally, but fails (is 0) on Jenkins. Figure out why.


def build_ius_cache(monkeypatch, root_dir, records):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(records)))
    with pytest.raises(SystemExit) as e:
        qcetl.main(["build", "-d", root_dir, "test_ius_cache"], IUS_CACHES)
    assert e.value.code == 0


def run_count(capsys, args):
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        qcetl.main(
            ["count"] + args + ["test_ius_cache", "test_ius_cache"],
            IUS_CACHES,
        )
    out, err = capsys.readouterr()
    return e.value.code, out.splitlines()[-1] if out else None, err


IUS_RECORDS = [
    {"index": 1, "run": "RUN_A", "lane": 1, "barcode": "AAAA-CCCC"},
    {"index": 2, "run": "RUN_A", "lane": 2, "barcode": "AAAA-CCCC"},
    {"index": 3, "run": "RUN_A", "lane": 2, "barcode": "GGGG-TTTT"},
    {"index": 4, "run": "RUN_B", "lane": 1, "barcode": "AAAA-CCCC"},
]


def test_count_filters(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        d = ["-d", test_dir]
        assert run_count(capsys, d)[:2] == (0, "4")
        assert run_count(capsys, d + ["-r", "RUN_A"])[:2] == (0, "3")
        assert run_count(capsys, d + ["-l", "2"])[:2] == (0, "2")
        assert run_count(capsys, d + ["-b", "AAAA-CCCC"])[:2] == (0, "3")
        assert run_count(
            capsys, d + ["-r", "RUN_A", "-l", "2", "-b", "AAAA-CCCC"]
        )[:2] == (0, "1")
        assert run_count(capsys, d + ["-l", "3"])[:2] == (0, "0")


def test_count_env_directory(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", test_dir)
        assert run_count(capsys, [])[:2] == (0, "4")


def test_count_multiple_directories(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as dir_a, tempfile.TemporaryDirectory() as dir_b:
        build_ius_cache(monkeypatch, dir_a, IUS_RECORDS[:2])
        # Index 2 is in both directories and should only be counted once
        build_ius_cache(monkeypatch, dir_b, IUS_RECORDS[1:])
        both = ["-d", dir_a, "-d", dir_b]
        assert run_count(capsys, ["-d", dir_a])[:2] == (0, "2")
        assert run_count(capsys, ["-d", dir_b])[:2] == (0, "3")
        assert run_count(capsys, both)[:2] == (0, "4")
        assert run_count(capsys, both + ["-r", "RUN_B"])[:2] == (0, "1")
        assert run_count(capsys, both + ["-l", "2"])[:2] == (0, "2")


def test_count_env_multiple_directories(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as dir_a, tempfile.TemporaryDirectory() as dir_b:
        build_ius_cache(monkeypatch, dir_a, IUS_RECORDS[:2])
        build_ius_cache(monkeypatch, dir_b, IUS_RECORDS[1:])
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", dir_a + os.pathsep + dir_b)
        assert run_count(capsys, [])[:2] == (0, "4")
        assert run_count(capsys, ["-l", "2"])[:2] == (0, "2")
        # -d takes precedence over the environment
        assert run_count(capsys, ["-d", dir_a])[:2] == (0, "2")


@pytest.mark.parametrize("env", [None, "", os.pathsep])
def test_count_no_directory(monkeypatch, capsys, env):
    if env is None:
        monkeypatch.delenv("QC_ETL_ROOT_DIRECTORY", raising=False)
    else:
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", env)
    code, out, err = run_count(capsys, [])
    assert code == 1
    assert out is None
    assert "QC_ETL_ROOT_DIRECTORY" in err


def test_count_missing_env_directory(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        missing = os.path.join(test_dir, "does", "not", "exist")
        monkeypatch.setenv("QC_ETL_ROOT_DIRECTORY", missing)
        code, out, err = run_count(capsys, [])
        assert code == 1
        assert out is None
        assert missing in err
        assert "None" not in err


def test_count_missing_directory(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        missing = os.path.join(test_dir, "does", "not", "exist")

        code, out, err = run_count(capsys, ["-d", test_dir, "-d", missing])
        assert (code, out) == (0, "4")
        assert missing in err

        code, out, err = run_count(capsys, ["-d", missing])
        assert code == 1
        assert out is None
        assert missing in err


def run_find(capsys, args):
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        qcetl.main(
            ["find"] + args + ["test_ius_cache", "test_ius_cache"],
            IUS_CACHES,
        )
    out, err = capsys.readouterr()
    return e.value.code, out, err


def test_find_single_match(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        code, out, err = run_find(
            capsys,
            ["-d", test_dir, "-r", "RUN_A", "-l", "2", "-b", "GGGG-TTTT"],
        )
        assert code == 0
        assert json.loads(out) == {
            "index": 3,
            "Run Alias": "RUN_A",
            "Lane Number": 2,
            "Barcodes": "GGGG-TTTT",
        }


def test_find_no_match(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        code, out, err = run_find(capsys, ["-d", test_dir, "-l", "3"])
        assert code == 1
        assert out == ""
        assert "0" in err


def test_find_multiple_matches(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        code, out, err = run_find(capsys, ["-d", test_dir, "-r", "RUN_A"])
        assert code == 1
        assert out == ""
        assert "3" in err


def test_find_multiple_directories(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as dir_a, tempfile.TemporaryDirectory() as dir_b:
        build_ius_cache(monkeypatch, dir_a, IUS_RECORDS[:2])
        build_ius_cache(monkeypatch, dir_b, IUS_RECORDS[1:])
        # Index 2 is in both directories but is still a single record
        code, out, err = run_find(
            capsys,
            [
                "-d",
                dir_a,
                "-d",
                dir_b,
                "-r",
                "RUN_A",
                "-b",
                "AAAA-CCCC",
                "-l",
                "2",
            ],
        )
        assert code == 0
        assert json.loads(out)["index"] == 2


def test_find_no_directory(monkeypatch, capsys):
    monkeypatch.delenv("QC_ETL_ROOT_DIRECTORY", raising=False)
    code, out, err = run_find(capsys, [])
    assert code == 1
    assert out == ""
    assert "QC_ETL_ROOT_DIRECTORY" in err


def make_lims_cache(name, lims_column, lims_type):
    class LimsColumn(qcetl.column.BaseColumn):
        Index = "index"
        Note = "note"
        Lims = lims_column

    class LimsTestCache(qcetl.common.Cache):
        def __init__(self):
            self.name = name
            self.schema_versions = {
                1: {
                    name: {
                        LimsColumn.Index: "i",
                        LimsColumn.Note: "s",
                        LimsColumn.Lims: lims_type,
                    }
                }
            }
            self.columns = {1: {name: LimsColumn}}
            self.input_format = {"index": "i", "lims": lims_type}
            self.primary_key = {1: {name: [LimsColumn.Index]}}
            self.input_key = {1: ("index", LimsColumn.Index)}

        def load(self, schema_version, path, cleaning_rules, log_creator):
            return qcetl.common.SQLiteCacheFile(
                path, self.name, schema_version, lambda df, name: df
            )

        def parse_single_record(self, single_input, schema_version):
            df = pandas.DataFrame({LimsColumn.Note: ["note"]})
            return {1: {name: df}}[schema_version]

        def add_shesmu_metadata(self, single_input, schema_version):
            return {
                name: {
                    LimsColumn.Index: single_input["index"],
                    LimsColumn.Lims: single_input["lims"],
                }
            }

    return LimsTestCache()


SINGLE_LIMS_CACHE = make_lims_cache(
    "test_single_lims_cache", qcetl.column.ColumnNames.PineryLimsID, "s"
)
MERGED_LIMS_CACHE = make_lims_cache(
    "test_merged_lims_cache", qcetl.column.ColumnNames.MergedPineryLimsID, "as"
)
LIMS_CACHES = (SINGLE_LIMS_CACHE, MERGED_LIMS_CACHE, IusTestCache())

SINGLE_LIMS_RECORDS = [
    {"index": 1, "lims": "1_1_LDI1"},
    {"index": 2, "lims": "1_2_LDI2"},
]
MERGED_LIMS_RECORDS = [
    {"index": 1, "lims": ["1_1_LDI1", "1_2_LDI2"]},
    {"index": 2, "lims": ["1_2_LDI2", "1_3_LDI3"]},
    {"index": 3, "lims": ["1_4_LDI4"]},
]


def build_lims_cache(monkeypatch, root_dir, name, records):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(records)))
    with pytest.raises(SystemExit) as e:
        qcetl.main(["build", "-d", root_dir, name], LIMS_CACHES)
    assert e.value.code == 0


def run_find_lims(capsys, name, args):
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        qcetl.main(["find"] + args + [name, name], LIMS_CACHES)
    out, err = capsys.readouterr()
    return e.value.code, out, err


def test_find_external_key_single(monkeypatch, capsys):
    name = "test_single_lims_cache"
    with tempfile.TemporaryDirectory() as test_dir:
        build_lims_cache(monkeypatch, test_dir, name, SINGLE_LIMS_RECORDS)
        code, out, err = run_find_lims(
            capsys, name, ["-d", test_dir, "-e", "1_2_LDI2"]
        )
        assert code == 0
        assert json.loads(out)["index"] == 2
        # Exact match only, not a substring
        code, out, err = run_find_lims(
            capsys, name, ["-d", test_dir, "-e", "1_2_LDI"]
        )
        assert (code, out) == (1, "")
        assert "0" in err


def test_find_external_key_merged(monkeypatch, capsys):
    name = "test_merged_lims_cache"
    with tempfile.TemporaryDirectory() as test_dir:
        build_lims_cache(monkeypatch, test_dir, name, MERGED_LIMS_RECORDS)
        code, out, err = run_find_lims(
            capsys, name, ["-d", test_dir, "-e", "1_3_LDI3"]
        )
        assert code == 0
        assert json.loads(out)["index"] == 2
        # Member of two records is ambiguous
        code, out, err = run_find_lims(
            capsys, name, ["-d", test_dir, "-e", "1_2_LDI2"]
        )
        assert (code, out) == (1, "")
        assert "2" in err
        # Exact member match only, not a substring
        code, out, err = run_find_lims(
            capsys, name, ["-d", test_dir, "-e", "1_4_LDI"]
        )
        assert (code, out) == (1, "")


def test_find_external_key_no_lims_column(monkeypatch, capsys):
    with tempfile.TemporaryDirectory() as test_dir:
        build_ius_cache(monkeypatch, test_dir, IUS_RECORDS)
        code, out, err = run_find(capsys, ["-d", test_dir, "-e", "1_1_LDI1"])
        assert (code, out) == (1, "")
        assert "Pinery Lims ID" in err


def test_find_external_key_conflicts_with_run_lane_barcode(monkeypatch, capsys):
    name = "test_single_lims_cache"
    with tempfile.TemporaryDirectory() as test_dir:
        build_lims_cache(monkeypatch, test_dir, name, SINGLE_LIMS_RECORDS)
        for extra in (["-r", "RUN_A"], ["-l", "1"], ["-b", "AAAA-CCCC"]):
            code, out, err = run_find_lims(
                capsys, name, ["-d", test_dir, "-e", "1_1_LDI1"] + extra
            )
            assert (code, out) == (1, "")
            assert "-e" in err
