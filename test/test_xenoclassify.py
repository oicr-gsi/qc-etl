import qcetl.xenoclassify
import test.cachechecker


def tests_xenoclassify():
    test.cachechecker.check(
        qcetl.xenoclassify.XenoclassifyCache(),
        [
            {
                "run": "210929_A00469_0222_BHL3YCDSX2",
                "lane": 1,
                "barcodes": "TTCGCCGA-CGGTATAC",
                "swid": "SWID",
                "file": "test/files/xenoclassify/xenoclassify.json",
            }
        ],
        {"xenoclassify": "test/files/xenoclassify/xenoclassify.csv"},
    )


def test_xenoclassify_nested():
    test.cachechecker.check(
        qcetl.xenoclassify.XenoclassifyCache(),
        [
            {
                "run": "220805_A00469_0338_AHJ2LMDSX3",
                "lane": 2,
                "barcodes": "GTCGAAGA-CCACATTG",
                "swid": "SWID",
                "file": "test/files/xenoclassify/xenoclassify_merged.json",
            }
        ],
        {"xenoclassify": "test/files/xenoclassify/xenoclassify_merged.csv"},
    )
