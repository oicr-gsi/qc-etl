import test.cachechecker
import qcetl.crosscheckfingerprint_caller
from qcetl.crosscheckfingerprint_caller import utility

from pandas import DataFrame, testing


def test_crosscheckfingerprint_caller():
    test.cachechecker.check(
        qcetl.crosscheckfingerprint_caller.CrosscheckFingerprintCaller(),
        [
            {
                "swid": "tool",
                "grouping": "project",
                "grouping_name": "TEST1",
                "file_calls": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.calls.csv",
                "file_detailed": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.detailed.csv",
            }
        ],
        {
            "calls": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.calls.output.csv",
            "detailed": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.detailed.output.csv",
        },
    )


def test_crosscheckfingerprint_caller_auto_verification():
    test.cachechecker.check(
        qcetl.crosscheckfingerprint_caller.CrosscheckFingerprintCallerAutoVerification(),
        [
            {
                "swid": "tool",
                "grouping": "project",
                "grouping_name": "TEST1",
                "file_calls": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.calls.csv",
                "file_detailed": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.detailed.csv",
            }
        ],
        {
            "calls": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.calls.output.csv",
            "detailed": "test/files/crosscheckfingerprint_caller/crosscheckfingerprint_caller_TEST1.detailed.output.csv",
        },
    )


def test_utility_consistent_lims_id_calls():
    calls = DataFrame(
        {
            "lims_id": ["A", "B", "C", "C"],
            "swap_call": [True, False, True, False],
        }
    )
    calls_util = DataFrame(
        {
            "lims_id": ["A", "B", "C", "C"],
            "swap_call": [True, False, True, True],
        }
    )
    calls_util_dedup = DataFrame(
        {"lims_id": ["A", "B", "C"], "swap_call": [True, False, True]}
    )

    testing.assert_frame_equal(
        calls_util, utility.consistent_lims_id_calls(calls, False)
    )
    testing.assert_frame_equal(
        calls_util_dedup, utility.consistent_lims_id_calls(calls, True)
    )
