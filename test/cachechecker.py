import qcetl.common
import qcetl.api
import json
import os
import pandas
import pandas.testing
import tempfile
import sqlalchemy


def check_with_loaded_cache(result, schema, golden_data, version, column_types):
    for name, attributes in schema.items():
        generated = getattr(result, name)
        if version in golden_data:
            golden_data = golden_data[version]

        # Confirm schema columns specified match parsed columns
        expected_columns = set(attributes.keys())
        generated_columns = set(generated)
        assert (
            expected_columns == generated_columns
        ), "Missing expected columns %s and got extra columns %s" % (
            expected_columns.difference(generated_columns),
            generated_columns.difference(expected_columns),
        )

        # If the file doesn't exist, assume this cache is in development and write out the current data as a golden for a human to validate and add to git. If it's not checked in, this leads to a failure mode where the test will always pass.
        if not os.path.exists(golden_data[name]):
            generated.sort_index().to_csv(golden_data[name], index=False)

        def load_json(j):
            # `pandas.to_csv` saves JSON lists in the wrong format and the ' and " need to be switched.
            return json.loads(j.replace("'", '"'))

        reference = pandas.read_csv(
            golden_data[name],
            # Force evaluation of anything that's a list
            converters={
                key: load_json
                for key, typedescriptor in attributes.items()
                if typedescriptor.startswith("a")
            },
        )
        reference = reference.astype(column_types[name])

        # Default error of assert_frame_equal is bad, does not state columns
        # Add joined columns and types for easy identification of mismatch
        col_compare = pandas.DataFrame(generated.dtypes).merge(
            pandas.DataFrame(reference.dtypes),
            how="outer",
            left_index=True,
            right_index=True,
        )
        col_compare = col_compare[col_compare["0_x"] != col_compare["0_y"]]
        assert len(col_compare) == 0, "Unexpected columns:\n{}".format(
            col_compare
        )

        # use consistent null value for future assert_frame_equal None/nan strict checking change
        # see https://github.com/pandas-dev/pandas/pull/52081
        generated = generated.fillna(value=pandas.NA)
        reference = reference.fillna(value=pandas.NA)

        pandas.testing.assert_frame_equal(generated, reference, check_like=True)


def check_columns(cache, version):
    """
    Check if all Column class variables are used. This prevents the Column class
    having variables that are deprecated.

    Check that the IUS columns (run, lane, barcode) are present.

    Args:
        cache: Cache instance to check
        version: Which schema version to check

    Returns:

    """
    schema = cache.get_tables(version)
    columns = cache.get_columns(version)
    for name, attributes in schema.items():
        used_cols = set(attributes.keys())
        annotated_cols = set(getattr(columns, name).values())

        assert (
            used_cols == annotated_cols
        ), "For %s, missing expected columns %s and got extra columns %s" % (
            name,
            annotated_cols.difference(used_cols),
            used_cols.difference(annotated_cols),
        )


def check_column_names(cache, version):
    """
    Ensures column names have no funny business in them

    Args:
        cache: Cache instance to check
        version: Which schema version to check

    """
    schema = cache.get_tables(version)
    for name, attributes in schema.items():
        used_cols = set(attributes.keys())

        for col_str in used_cols:
            assert (
                len(col_str) < 64
            ), f"Column name {col_str} is longer than 63 characters"


def check_table_names(cache, version):
    """
    Ensure table names (which will be the database table names) fit requirements

    Args:
        cache: Cache instance to check
        version: Which schema version to check
    """
    for t in cache.get_tables(version):
        table = cache.get_table_name(version, t)
        assert (
            len(table) < 64
        ), f"Table name {table} is longer than 63 characters"


def check_primary_keys(cache, version):
    """
    Primary keys cannot be nested types, as that is not supported by postgres

    Args:
        cache: Cache instance to check
        version: Which schema version to check
    """
    primary_key = cache.primary_key[version]
    tables = cache.get_tables(version)
    for t in primary_key:
        for key_column in primary_key[t]:
            assert (
                key_column in tables[t]
            ), f"Primary key {key_column} not annotated for table {t}"
            assert (
                "a" not in tables[t][key_column]
            ), f"Primary key {key_column} for table {t} cannot be a list"


def check_attribute_validity(cache):
    """
    Cache class attributes need to match in various ways. If they don't, one gets
    weird errors well after the fact

    Args:
        cache: The cache being tested

    Returns:

    """
    # The schema is the truth about versions and tables. Hold version and set of tables
    golden = {}
    for ver in cache.schema_versions:
        golden[ver] = set(cache.schema_versions[ver].keys())

    for col in cache.columns:
        assert col in golden, "`column` version field is wrong/missing"
        assert (
            set(cache.columns[col].keys()) == golden[col]
        ), "`column` field has wrong/missing tables"

    for key in cache.primary_key:
        assert key in golden, "`primary_key` version field is wrong/missing"
        assert (
            set(cache.primary_key[key].keys()) == golden[key]
        ), "`primary_key` field has wrong/missing tables"

    for key in cache.input_key:
        assert key in golden, "`input_key` version field is wrong/missing"
        print(cache.input_key[key][0])
        assert (
            cache.input_key[key][0] in cache.input_format
        ), "Declared Shesmu `input_key` is not in `input_format`"


def check_shesmu_input(cache, input_data):
    """
    Check that the annotated Shesmu input format is valid and that the test input data matches that.

    Args:
        cache: The cache class
        input_data: The list of Shesmu input data

    """
    expected = cache.input_format
    # input data is a list of dictionaries
    for d in input_data:
        for field in d:
            assert (
                field in expected
            ), "Shesmu field ({}) in test is not annotated in cache class".format(
                field
            )
            field_type = expected[field]
            if isinstance(field_type, str) and field_type.startswith("q"):
                field_type = field_type[1:]
                if d[field] is None:
                    continue

            value = d[field]

            if isinstance(field_type, list):
                assert isinstance(
                    value, list
                ), "Shesmu field {} is not the annotated type".format(field)
            elif field_type.startswith("a"):
                assert isinstance(
                    value, list
                ), "Shesmu field {} is not the annotated type".format(field)
            elif field_type == "i":
                assert isinstance(
                    value, int
                ), "Shesmu field {} is not the annotated type".format(field)
            elif field_type == "f":
                assert isinstance(
                    value, float
                ), "Shesmu field {} is not the annoated type".format(field)
            elif field_type == "p":
                assert isinstance(
                    value, str
                ), "Shesmu field {} is not the annotated type".format(field)
            elif field_type == "s":
                assert isinstance(
                    value, str
                ), "Shesmu field {} is not the annotated type".format(field)
            else:
                assert False, "Unknown Shesmu type: {}".format(field_type)


def check(cache, input_data, golden_data):
    """
    Build the cache; check column names against schema, and equivalence with gold standard data

    Args:
        input_data:  The input JSON data
        golden_data: Path to CSV file with gold standard data
    """
    assert sum((cache.name == c.name for c in qcetl.api.QCETLCache.caches())), (
        "Cache %s is not on format list" % cache.name
    )

    check_attribute_validity(cache)
    check_shesmu_input(cache, input_data)

    for version in cache.schema_versions:
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        ) as test_dir:
            check_columns(cache, version)
            check_column_names(cache, version)
            check_table_names(cache, version)
            check_primary_keys(cache, version)
            test_file = os.path.join(test_dir, "test.sqlite")
            engine = sqlalchemy.create_engine(
                "sqlite:///" + test_file, future=True
            )
            rslt = cache.build(input_data, engine)
            assert (
                len(rslt.failed) == 0
            ), "Failed to parse all inputs. Check test logs."
            clean = qcetl.common.CleaningRules()
            result = cache.load(version, test_file, clean, lambda x: None)
            schema = cache.get_tables(version)
            check_with_loaded_cache(
                result, schema, golden_data, version, cache.get_dtypes(version)
            )

            # Ensure empty input data is valid (only checks successful completion)
            test_empty_file = os.path.join(test_dir, "test_empty.hdf5")
            empty_engine = sqlalchemy.create_engine(
                "sqlite:///" + test_empty_file, future=True
            )
            cache.build([], empty_engine)
