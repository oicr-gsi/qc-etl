import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import shutil
import sqlalchemy

from qcetl.column import ColumnNames
from qcetl.api import QCETLCache
import qcetl.common
import os
import sys
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def show_list(args):
    for form in args.all_formats:
        print(form.name)
    return 0


def show_version(args):
    for version in args.format.schema_versions.keys():
        print(version)
    return 0


def show_tables(args):
    if args.version is None:
        args.version = args.format.latest_version()

    tables = args.format.get_tables(args.version)
    if tables:
        print("\n".join(tables.keys()))
        return 0
    else:
        sys.stderr.write(
            "Unknown version %d for format %s\n"
            % (args.version, args.format.name)
        )
        return 1


def show_schema(args):
    if args.version is None:
        args.version = args.format.latest_version()

    schema = args.format.get_tables(args.version).get(args.table, None)
    if schema:
        for name, type_descriptor in schema.items():
            print("%s\t%s" % (name, type_descriptor))
        return 0
    else:
        sys.stderr.write(
            'Unknown table "%s" for version %d for format %s\n'
            % (args.table, args.version, args.format.name)
        )
        return 1


def dump(args):
    qcapi = QCETLCache(args.directory)
    if args.version is None:
        args.version = args.format.latest_version()

    data = getattr(
        qcapi.load(
            args.format,
            args.version,
            qcetl.common.CleaningRules(args.cleaning),
            lambda x: None,
        ),
        args.table,
    )
    print(data.to_csv(index=False))
    return 0


def refill_config(args):
    form = args.format

    if args.directory is not None:
        path = args.directory
    elif os.getenv("QC_ETL_ROOT_DIRECTORY") is not None:
        path = os.getenv("QC_ETL_ROOT_DIRECTORY")
    else:
        print(
            "Cache save directory must be specified in command or via QC_ETL_ROOT_DIRECTORY env variable",
            file=sys.stderr,
        )
        return 1

    if args.incremental_cache_name is None:
        incremental_command = ""
    else:
        incremental_command = "-i " + args.incremental_cache_name

    if args.bin is None:
        bin_arg = sys.argv[0]
    else:
        bin_arg = args.bin

    rf = {
        "command": (
            "%s build %s -d %s %s -c "
            % (bin_arg, form.name, path, incremental_command)
        ),
        "parameters": form.input_format,
    }

    if args.name is None:
        print(json.dumps(rf))
    else:
        print(json.dumps({args.name: rf}))
    return 0


def rebuild_postgres(args):
    # Request input data from Shesmu
    print("UPDATE", flush=True)  # Required for Shesmu
    input_data = json.load(sys.stdin)
    if not input_data:
        # stdout is reserved for Shesmu communication
        print("No records. Bailing...", file=sys.stderr)
        return 0

    if args.directory is not None:
        root_dir = args.directory
    elif os.getenv("QC_ETL_ROOT_DIRECTORY") is not None:
        root_dir = os.getenv("QC_ETL_ROOT_DIRECTORY")
    # If it's in the refiller, remove that key. Caches don't need to know where their output is being saved.
    else:
        from_refill = set()
        for i in input_data:
            from_refill.add(i.pop("qcetl_root_dir", None))

        if from_refill == {None}:
            print(
                "No root directory provided. Use -d flag, QC_ETL_ROOT_DIRECTORY env variable, or in the "
                "refiller with the qcetl_root_dir key",
                file=sys.stderr,
            )
            return 1
        elif len(from_refill) > 1:
            print(
                "Each refiller element must have the same value for qcetl_root_dir",
                file=sys.stderr,
            )
            return 1
        else:
            root_dir = next(iter(from_refill))

    path_config = os.path.join(root_dir, QCETLCache.CONFIG_FILE)
    if not os.path.exists(path_config):
        if args.urlfile is None:
            print(
                "Postgres file with URL must be specified if config file does not exist",
                file=sys.stderr,
            )
            return 1
        backend = "postgres"
        url_file = args.urlfile
        with open(path_config, "w") as f:
            json.dump({"backend": backend, "url_file": url_file}, f)
    else:
        with open(path_config, "r") as f:
            config = json.load(f)
            if config.get("backend") != "postgres":
                print("Backends don't match", file=sys.stderr)
                return 1
            url_file = (
                args.urlfile
                if args.urlfile is not None
                else config.get("url_file")
            )

    if not os.path.exists(url_file):
        print(f"URL file at {url_file} does not exist", file=sys.stderr)
        return 1

    with open(url_file, "r") as f:
        url = f.readline().strip()

    form = args.format
    path = os.path.join(root_dir, form.cache_folder_name())
    if not os.path.exists(path):
        os.makedirs(path)

    register_build_log(path)

    logger.info("Starting")
    logger.info("Reading input for checksum %s..." % args.checksum)

    # Normally, if we get the same data again from Shesmu, we won't rebuild. If
    # a file named `force` is in the directory, rebuild it even if it looks
    # clean and delete the `force` file on success.
    force_file = os.path.join(path, "force")
    force = os.path.exists(force_file)
    latest_input_name = "%s.json" % args.checksum
    latest_input = os.path.join(path, QCETLCache.SHESMU_INPUT_FILE)

    with open(os.path.join(path, latest_input_name), "w") as input_dump:
        json.dump(input_data, input_dump)
    logger.info("Read %d records..." % len(input_data))

    engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{url}", future=True
    )
    if args.archive:
        logger.info("Archival caching enabled")
        if force:
            logger.info(
                "Force file not allowed in archival caching. Deleting it."
            )
            if os.path.exists(force_file):
                os.remove(force_file)
    elif args.increment and not force:
        logger.info("Incremental caching enabled")
    else:
        logger.info(
            "Re-caching everything! All records will be deleted and re-parsed."
        )
        form.delete_all_tables(engine)

    if force and os.path.exists(force_file):
        logger.info("Rebuild was forced via force file. Not doing that again.")
        os.remove(force_file)

    rslt = form.build(input_data, engine, args.archive)

    with open(
        os.path.join(path, QCETLCache.FAILED_INPUT_FILE), "w"
    ) as input_dump:
        json.dump(rslt.failed, input_dump)

    # temp file approach gets around `os.symlink` not being able to replace symlinks
    def update_symlink(dest, sym):
        temp_link_file = os.path.join(path, "newest")
        os.symlink(dest, temp_link_file)
        os.replace(temp_link_file, sym)

    logger.info("Updating symlink...")
    update_symlink(latest_input_name, latest_input)

    return len(rslt.failed)


def rebuild(args):
    # Request input data from Shesmu
    print("UPDATE", flush=True)  # Required for Shesmu
    input_data = json.load(sys.stdin)
    if not input_data:
        # stdout is reserved for Shesmu communication
        print("No records. Bailing...", file=sys.stderr)
        return 0
    timeout = (
        None
        if args.timeout is None
        else qcetl.common.utility.TimeOut(args.timeout)
    )
    if args.directory is not None:
        root_dir = args.directory
    elif os.getenv("QC_ETL_ROOT_DIRECTORY") is not None:
        root_dir = os.getenv("QC_ETL_ROOT_DIRECTORY")
    # If it's in the refiller, remove that key. Caches don't need to know where their output is being saved.
    else:
        from_refill = set()
        for i in input_data:
            from_refill.add(i.pop("qcetl_root_dir", None))

        if from_refill == {None}:
            print(
                "No root directory provided. Use -d flag, QC_ETL_ROOT_DIRECTORY env variable, or in the "
                "refiller with the qcetl_root_dir key",
                file=sys.stderr,
            )
            return 1
        elif len(from_refill) > 1:
            print(
                "Each refiller element must have the same value for qcetl_root_dir",
                file=sys.stderr,
            )
            return 1
        else:
            root_dir = next(iter(from_refill))

    form = args.format
    path = os.path.join(root_dir, form.cache_folder_name())
    if not os.path.exists(path):
        os.makedirs(path)

    register_build_log(path)

    logger.info("Starting")
    logger.info("Reading input for checksum %s..." % args.checksum)

    # Normally, if we get the same data again from Shesmu, we won't rebuild. If
    # a file named `force` is in the directory, rebuild it even if it looks
    # clean and delete the `force` file on success.
    force_file = os.path.join(path, "force")
    force = os.path.exists(force_file) or args.force
    # File to mark if the caching has timed out
    # Do not revert to a cache that has timed out
    timeout_name = f"{args.checksum}.timeout"
    timeout_file = os.path.join(path, timeout_name)
    timed_out = os.path.exists(timeout_file)
    # Final path where cache will be saved
    target_file_name = "%s.sqlite" % args.checksum
    target_file = os.path.join(path, target_file_name)
    latest_input_name = "%s.json" % args.checksum
    failed_input_name = f"{args.checksum}.failed.json"
    stale_rows_name = f"{args.checksum}.stale.json"
    # Used while cache is being build. Prevents existing caches from becoming corrupted
    # if they are being rebuild (force or change of schema)
    target_temp_file = os.path.join(path, "%s_temp.sqlite" % args.checksum)
    latest_link = os.path.join(path, QCETLCache.LATEST_FILE_NAME)
    latest_input = os.path.join(path, QCETLCache.SHESMU_INPUT_FILE)
    incremental_cache = (
        None
        if args.incremental_cache_name is None
        else os.path.join(path, args.incremental_cache_name)
    )
    if incremental_cache is not None:
        if force:
            logger.info("Incremental cache ignored as rebuild was forced")
            incremental_cache = None
        elif not os.path.exists(incremental_cache):
            logger.info(
                "Incremental cache file {} does not exist. Will do full rebuild".format(
                    incremental_cache
                )
            )
            incremental_cache = None
        else:
            logger.info(
                "Doing incremental cache with %s..." % incremental_cache
            )

    # temp file approach gets around `os.symlink` not being able to replace symlinks
    def update_symlink(dest, sym):
        temp_link_file = os.path.join(path, "newest")
        os.symlink(dest, temp_link_file)
        os.replace(temp_link_file, sym)

    if not force:
        # Check if the latest is already the right file
        if os.path.exists(latest_link):
            if not form.match_versions(latest_link):
                logger.info(
                    "Latest cache schema versions are stale. "
                    "Will build cache even if input is unchanged."
                )
            if timed_out:
                logger.info("Latest cache timed out. Will attempt again.")
            else:
                link_contents = os.path.join(path, os.readlink(latest_link))
                if link_contents == target_file:
                    os.utime(target_file, None)
                    print("OK", flush=True)  # Required for Shesmu
                    logger.info("Input already cached.")
                    return 0
        # Check if the file already exists.
        # This means we reverted to a previous state. Just update the link
        if os.path.exists(target_file):
            if not form.match_versions(target_file):
                logger.info(
                    "Previously cached schema versions are stale. "
                    "Will build cache even if input has already been cached."
                )
            if timed_out:
                logger.info("Previous cache timed out. Will attempt again.")
            else:
                update_symlink(target_file_name, latest_link)
                update_symlink(latest_input_name, latest_input)
                print("OK", flush=True)  # Required for Shesmu
                logger.info(
                    "Input previously cached. Pointing latest symlink to {}.".format(
                        args.checksum
                    )
                )
                return 0

    with open(os.path.join(path, latest_input_name), "w") as input_dump:
        json.dump(input_data, input_dump)
    logger.info("Read %d records..." % len(input_data))

    logger.info(
        "Building cache at temporary location {}".format(target_temp_file)
    )
    if incremental_cache is not None:
        logger.info(
            "Using existing cache for incremental build: {}".format(
                incremental_cache
            )
        )
        shutil.copy2(incremental_cache, target_temp_file, follow_symlinks=True)
    engine = sqlalchemy.create_engine(
        "sqlite:///" + target_temp_file, future=True
    )
    try:
        # Create the timeout file, which will stick around if build loop is quit externally
        if args.timeout:
            open(timeout_file, "a")
        rslt = form.build(input_data, engine, args.archive, timeout)
        if not rslt.timeout:
            if os.path.exists(timeout_file):
                os.remove(timeout_file)
            logger.info("Cache has finished building")
        else:
            logger.info("Cache building has timed out")
        logger.info("Moving cache to final location {}".format(target_file))
        os.replace(target_temp_file, target_file)
    finally:
        # If an uncaught exception happens, don't leave stray temp files around
        if os.path.exists(target_temp_file):
            os.remove(target_temp_file)

    logger.info("Updating symlink...")
    update_symlink(target_file_name, latest_link)
    update_symlink(latest_input_name, latest_input)
    if force and os.path.exists(force_file):
        logger.info("Rebuild was forced via force file. Not doing that again.")
        os.remove(force_file)
    logger.info("Done!")

    with open(
        os.path.join(path, QCETLCache.FAILED_INPUT_FILE), "w"
    ) as input_dump:
        json.dump(rslt.failed, input_dump, indent=4)

    with open(os.path.join(path, failed_input_name), "w") as fail_dump:
        json.dump(rslt.failed, fail_dump, indent=4)

    with open(os.path.join(path, stale_rows_name), "w") as stale_dump:
        json.dump(list(rslt.stale), stale_dump, indent=4)

    return len(rslt.failed)


def count(args):
    form = args.format
    etlapi = QCETLCache(args.directory)
    version = form.latest_version() if args.version is None else args.version
    cache = etlapi.load(
        form.name,
        version,
        # Count all records in cache without any cleaning
        qcetl.common.CleaningRules(False),
        lambda x: None,
    )
    data = getattr(cache, args.table)
    cache.close()

    def check_filter_column(col):
        if col not in data:
            print(
                "Filtering by column {} was ignored as it does not exist".format(
                    col
                ),
                file=sys.stderr,
            )
            return False
        return True

    if args.run is not None and check_filter_column(ColumnNames.Run):
        data = data[data[ColumnNames.Run] == args.run]
    if args.lane is not None and check_filter_column(ColumnNames.Lane):
        data = data[data[ColumnNames.Lane] == str(args.lane)]
    if args.barcode is not None and check_filter_column(ColumnNames.Barcodes):
        data = data[data[ColumnNames.Barcodes] == args.barcode]

    print(data.shape[0])


def shesmu_input(args):
    etlapi = QCETLCache(args.directory)
    form = args.format
    if args.which == "shesmu":
        path = etlapi.path_latest_input(form)
    else:
        path = etlapi.path_failed_input(form)

    if not os.path.exists(path):
        sys.stderr.write("File does not exist: {}\n".format(path))
        return 1

    if args.modified:
        print(os.stat(path).st_mtime)
        return 0

    with open(path, "r") as f:
        loaded = json.load(f)

    if args.run is not None:
        loaded = [x for x in loaded if x.get("run") == args.run]
    if args.lane is not None:
        loaded = [x for x in loaded if x.get("lane") == args.lane]
    if args.barcode is not None:
        loaded = [x for x in loaded if x.get("barcode") == args.barcode]

    if args.count:
        print(str(len(loaded)))
        return 0

    print(json.dumps(loaded))
    return 0


def register_build_log(path):
    # Filter that allows for logging of exactly one log level
    class LevelFilter(logging.Filter):
        def __init__(self, level):
            super().__init__()
            self.level = level

        def filter(self, record):
            return record.levelno == self.level

    stdout = os.path.join(path, "stdout.log")
    stderr = os.path.join(path, "stderr.log")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    log = logging.getLogger("qcetl")
    log.setLevel(logging.INFO)

    handler_stdout = RotatingFileHandler(
        stdout, maxBytes=10 * 1024 * 1024, backupCount=1
    )
    handler_stdout.addFilter(LevelFilter(logging.INFO))
    handler_stdout.setFormatter(formatter)
    log.addHandler(handler_stdout)

    handler_stderr = RotatingFileHandler(
        stderr, maxBytes=10 * 1024 * 1024, backupCount=1
    )
    handler_stderr.setLevel(logging.WARNING)
    handler_stderr.setFormatter(formatter)
    log.addHandler(handler_stderr)

    # Stream logging only to stderr, as stdout is reserved for Shesmu communication
    # Grafana uses this to display logs
    stream_stderr = logging.StreamHandler(stream=sys.stderr)
    stream_stderr.setLevel(logging.INFO)
    stream_stderr.setFormatter(formatter)
    log.addHandler(stream_stderr)

    # Uncaught exceptions are not logged by default
    # https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
    def handle_exception(exc_type, exc_value, exc_traceback):
        log.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception


def main(args=None, caches=QCETLCache.caches()):
    """
    Entry point for the CLI

    Args:
        args: sys.argv by default. Exposed for testing.
        caches: The available caches. Exposed for testing.

    Returns:

    """
    parser = argparse.ArgumentParser(
        prog="qcetl",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
To find available formats (caches):

`qcetl list`

By default, all commands will return the latest cache version. To list all versions:

`qcetl versions bamqc4`

Each cache stores one or more tables. To list them:

`qcetl tables bamqc4`

To get the columns and types of a table:

`qcetl schema bamqc4 bamqc4`

Do download a cache, its location is specified with the -d flag or set via the
QC_ETL_ROOT_DIRECTORY environmental variable. The below are equivalent:

```
qcetl dump bamqc4 bamqc4
qcetl dump bamqc4 bamqc4 -d $QC_ETL_ROOT_DIRECTORY
```

To generate the Shesmu refiller command (allows for optional incremental cache)

`qcetl refill-config bamqc4 -i latest`

To build a cache, it is necessary to pipe the Shesmu refiller output to the `build`
command.

```
qcetl input bamqc4 shesmu > refiller.json
cat refiller.json | qcetl build bamqc4 -d /save/dir -c cache_file_name
```
""",
    )
    subparsers = parser.add_subparsers(
        help="sub-command help", dest="subcommand"
    )

    parser_list = subparsers.add_parser("list", help="List all known formats")
    parser_list.set_defaults(func=show_list)

    parser_versions = subparsers.add_parser(
        "versions", help="List all known versions for a format"
    )
    parser_versions.add_argument("format", help="The format")
    parser_versions.set_defaults(func=show_version)

    parser_tables = subparsers.add_parser(
        "tables", help="List all known tables for a format"
    )
    parser_tables.add_argument("format", help="The format")
    parser_tables.add_argument(
        "-v", "--version", type=int, help="The format version (default: latest)"
    )
    parser_tables.set_defaults(func=show_tables)

    parser_schema = subparsers.add_parser(
        "schema", help="Display the schema for a table"
    )
    parser_schema.add_argument("format", help="The format")
    parser_schema.add_argument("table", help="The table")
    parser_schema.add_argument(
        "-v", "--version", type=int, help="The format version (default: latest)"
    )
    parser_schema.set_defaults(func=show_schema)

    parser_dump = subparsers.add_parser(
        "dump", help="Convert a table to a CSV file"
    )
    parser_dump.add_argument("format", help="The format")
    parser_dump.add_argument("table", help="The table")
    parser_dump.add_argument(
        "-v", "--version", type=int, help="The format version (default: latest)"
    )
    parser_dump.add_argument(
        "-d",
        "--directory",
        help="The root directory where the all caches are being saved",
    )
    parser_dump.add_argument(
        "-r",
        "--raw",
        dest="cleaning",
        action="store_false",
        help="Normally, invalid data will be cleaned; Set this flag to include it",
    )
    parser_dump.set_defaults(func=dump)

    parser_refill_config = subparsers.add_parser(
        "refill-config",
        help="Create a Shesmu-compatible definition to rebuild this format",
    )
    parser_refill_config.add_argument("format", help="The format")
    parser_refill_config.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The root directory where the cache folders should be placed",
    )
    parser_refill_config.add_argument(
        "-i",
        "--incremental-cache",
        dest="incremental_cache_name",
        help="Name of existing cache. Enables incremental caching",
    )
    parser_refill_config.add_argument(
        "-b",
        "--bin",
        dest="bin",
        help="The binary to call for the refiller. By default the binary used in this call",
    )
    parser_refill_config.add_argument(
        "-n",
        "--name",
        dest="name",
        help="The name to use for the refiller",
    )
    parser_refill_config.set_defaults(func=refill_config)

    parser_build_sqlite = subparsers.add_parser(
        "build", help="Build a cache and store it in a SQLite backend"
    )
    parser_build_sqlite.add_argument("format", help="The format")
    parser_build_sqlite.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The root directory where the cache folders should be placed",
    )
    parser_build_sqlite.add_argument(
        "-c",
        "--checksum",
        dest="checksum",
        help="The data checksum from Shesmu",
    )
    parser_build_sqlite.add_argument(
        "-i",
        "--incremental-cache",
        dest="incremental_cache_name",
        help="Name of existing cache. Enables incremental caching",
    )
    parser_build_sqlite.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        help="Force caching. Will override incremental caching. Can also be done by placing `force` file in directory",
    )
    parser_build_sqlite.add_argument(
        "-a",
        "--archive",
        action="store_true",
        dest="archive",
        help=(
            "If this is enabled, no records will be deleted. Without this, records that are no longer in the Shesmu "
            "input or are in deprecated cache version will be removed."
        ),
    )
    # Timeout is needed as SQLite database is not modified in place during incremental builds
    # The last file is copied, updated, and once finished, replaces the last file
    # If the process is interrupted, the last file remains. Add this timeout if you expect distributions
    parser_build_sqlite.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        type=int,
        help="Number of seconds after which record parsing will stop and the database is written out",
    )
    parser_build_sqlite.set_defaults(func=rebuild)

    parser_build_postgres = subparsers.add_parser(
        "build-postgres",
        help="Build a cache and store it in a Postgres backend",
    )
    parser_build_postgres.add_argument("format", help="The format")
    parser_build_postgres.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The root directory where the config and logs are stored",
    )
    parser_build_postgres.add_argument(
        "-c",
        "--checksum",
        dest="checksum",
        help="The data checksum from Shesmu",
    )
    parser_build_postgres.add_argument(
        "-i",
        "--increment",
        dest="increment",
        action="store_true",
        help="Enable incremental caching",
    )
    parser_build_postgres.add_argument(
        "-u",
        "--url-file",
        dest="urlfile",
        help=(
            "Location of a text file that contains the URL in the format "
            "{user}:{password}@{hostname}:{port}/{database-name}. The path will be stored in the config file in the "
            "root directory. This argument is not necessary if the path is already there."
        ),
    )
    parser_build_postgres.add_argument(
        "-a",
        "--archive",
        action="store_true",
        dest="archive",
        help=(
            "If this is enabled, no records will be deleted. Without this, records that are no longer in the Shesmu "
            "input or are in deprecated cache version will be removed."
        ),
    )
    parser_build_postgres.set_defaults(func=rebuild_postgres)

    parser_count = subparsers.add_parser(
        "count", help="Count records. Filter by run, lane, and barcode"
    )
    parser_count.add_argument("format", help="The format")
    parser_count.add_argument("table", help="The table")
    parser_count.add_argument(
        "-v",
        "--version",
        type=int,
        help="The format version. Defaults to latest.",
    )
    parser_count.add_argument(
        "-r", "--run", type=str, help="Count records for this run only."
    )
    parser_count.add_argument(
        "-l", "--lane", type=int, help="Count records for this lane only."
    )
    parser_count.add_argument(
        "-b", "--barcode", type=str, help="Count records for this barcode only."
    )
    parser_count.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The root directory of the cache folders",
    )
    parser_count.set_defaults(func=count)
    parser_input = subparsers.add_parser(
        "input", help="Information on Shesmu input."
    )
    parser_input.set_defaults(func=shesmu_input)
    parser_input.add_argument("format", help="The format")
    parser_input.add_argument(
        "which",
        choices=["shesmu", "failed"],
        help="Look at latest Shesmu input or failed inputs",
    )
    parser_input.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The root directory of the cache folders",
    )
    parser_input.add_argument(
        "-m",
        "--modified",
        action="store_true",
        help="Get the last modified date of file in Epoch time instead of JSON output",
    )
    parser_input.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Count the number of Shesmu records in file instead of JSON output",
    )
    parser_input.add_argument(
        "-r", "--run", type=str, help="Filter for this run only"
    )
    parser_input.add_argument(
        "-l", "--lane", type=int, help="Filter for this lane only"
    )
    parser_input.add_argument(
        "-b", "--barcode", type=str, help="Filter for this barcode only"
    )

    args = parser.parse_args(args)
    args.all_formats = caches
    if hasattr(args, "format"):
        form = None
        for f in caches:
            if f.name == args.format:
                form = f
        if form is None:
            sys.stderr.write("Unknown format: %s\n" % args.format)
            return 1
        else:
            args.format = form

    if hasattr(args, "func"):
        sys.exit(args.func(args))
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)


# Re-export
from qcetl.api import QCETLCache, QCETLColumns, QCETLMultiCache  # noqa
