import qcetl.common.canary
import test.cachechecker


def test_qcetl_canary():
    test.cachechecker.check(
        qcetl.common.canary.QcEtlCanary(),
        [{"key": "hello", "number": 4}, {"key": "world", "number": 2}],
        {"canary": "test/files/qcetl/qcetl_canary.csv"},
    )
