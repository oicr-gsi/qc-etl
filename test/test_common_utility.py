from qcetl.common.utility import (
    median_from_frequency_table,
    quantile_from_frequency_table,
    none_to_nan_json_hook,
    TimeOut,
)
import io
import json
import numpy
import pandas
import time


def test_medican_calc():
    c = pandas.DataFrame({"value": [1, 10], "count": [4, 4]})
    assert median_from_frequency_table(c) == 5.5

    c = pandas.DataFrame({"value": [1, 10], "count": [5, 4]})
    assert median_from_frequency_table(c) == 1

    c = pandas.DataFrame({"value": [1, 10], "count": [4, 5]})
    assert median_from_frequency_table(c) == 10


def test_quantile_calc():
    c = pandas.DataFrame({"value": [1, 10], "count": [4, 6]})
    assert quantile_from_frequency_table(c, 0) == 1
    assert quantile_from_frequency_table(c, 0.4) == 1
    assert quantile_from_frequency_table(c, 0.41) == 10
    assert quantile_from_frequency_table(c, 1) == 10


def test_none_to_nan_json_hook():
    j_in = """{
        "hello": 1,
        "why": null,
        "nested_dict": {"yay": "yo", "no": null, "list": [1, null]},
        "list": [
            "one",
            1,
            null,
            [2, null],
            {"deep": null, "really": [1, null]}
        ]
    }"""
    expected = {
        "hello": 1,
        "why": numpy.nan,
        "nested_dict": {"yay": "yo", "no": numpy.nan, "list": [1, numpy.nan]},
        "list": [
            "one",
            1,
            numpy.nan,
            [2, numpy.nan],
            {"deep": numpy.nan, "really": [1, numpy.nan]},
        ],
    }
    out = json.load(io.StringIO(j_in), object_hook=none_to_nan_json_hook)
    assert out == expected


def test_timeout():
    t = TimeOut(0.1)
    assert not t.timeout()
    time.sleep(0.05)
    assert not t.timeout()
    time.sleep(0.06)
    assert t.timeout()
