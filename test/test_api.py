import os
import pytest

import qcetl.common
from qcetl import QCETLCache, QCETLMultiCache

from qcetl.fastqc import FastQcCache
import test.cachechecker


def test_custom_loading():
    api = QCETLCache("test/files/test_caches")

    clean = qcetl.common.CleaningRules()

    custom_load = api.load(
        "fastqc", 1, clean, lambda x: None, "custom_cache_name"
    )
    schema = FastQcCache().get_tables(FastQcCache().latest_version())

    test.cachechecker.check_with_loaded_cache(
        custom_load,
        schema,
        {
            "fastqc": "test/files/test_caches/fastqc/SWID_12909889_GLCS_0022_Br_P_PE_288_EX_NFBT_08Nov2018-3_181109_A00469_0016_AHGC37DMXX_CGTCTCATAT-TATAGTAGCT_L001_R1_001_fastqc.csv"
        },
        1,
        FastQcCache().get_dtypes(),
    )


def test_default_loading():
    default_load = QCETLCache("test/files/test_caches").fastqc
    schema = FastQcCache().get_tables(FastQcCache().latest_version())

    test.cachechecker.check_with_loaded_cache(
        default_load,
        schema,
        {
            "fastqc": "test/files/test_caches/fastqc/SWID_12909889_GLCS_0022_Br_P_PE_288_EX_NFBT_08Nov2018-3_181109_A00469_0016_AHGC37DMXX_CGTCTCATAT-TATAGTAGCT_L001_R1_001_fastqc.csv"
        },
        1,
        FastQcCache().get_dtypes(),
    )


def test_env_loading():
    os.environ["QC_ETL_ROOT_DIRECTORY"] = "test/files/test_caches"
    default_load = QCETLCache().fastqc
    schema = FastQcCache().get_tables(FastQcCache().latest_version())

    test.cachechecker.check_with_loaded_cache(
        default_load,
        schema,
        {
            "fastqc": "test/files/test_caches/fastqc/SWID_12909889_GLCS_0022_Br_P_PE_288_EX_NFBT_08Nov2018-3_181109_A00469_0016_AHGC37DMXX_CGTCTCATAT-TATAGTAGCT_L001_R1_001_fastqc.csv"
        },
        1,
        FastQcCache().get_dtypes(),
    )


def test_cache_exists():
    default_load = QCETLCache("test/files/test_caches").fastqc
    assert default_load.exists("fastqc")
    assert not default_load.exists("XXX")

    not_cached = QCETLCache("test/files/test_caches").bamqc4
    assert not not_cached.exists("bamqc4")


def test_multi_load():
    multi = QCETLMultiCache(
        ["test/files/test_caches", "test/files/test_caches"]
    )
    deduped_double_df = multi.load_same_version(FastQcCache())
    # The collapsing function removes duplicate records
    assert len(deduped_double_df.unique("fastqc")) == 1


def test_multi_empty():
    with pytest.raises(ValueError):
        QCETLMultiCache([])


def test_multie_remove_missing():
    multi = QCETLMultiCache(["test/files/test_caches", "does/not/exist"])
    m = multi.load_same_version(FastQcCache())
    cleaned = m.remove_missing("fastqc")
    # Loading the data should not throw any errors since missing sources are gone
    cleaned.unique("fastqc")


def test_version():
    # Time will differ based on user, so just ensure it gets the time
    assert (
        "(Unknown time)"
        not in QCETLCache("test/files/test_caches").fastqc.version()
    )


def test_connection():
    api = QCETLCache("test/files/test_caches")
    assert api.test_connection()
    broken = QCETLCache("/does/not/exist")
    assert not broken.test_connection()
    multi = QCETLMultiCache(["test/files/test_caches", "does/not/exist"])
    assert multi.test_connection() == [True, False]
