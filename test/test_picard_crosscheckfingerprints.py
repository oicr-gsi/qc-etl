import test.cachechecker
import qcetl.picard.crosscheckfingerprints


def tests_picard_crosscheckfingerprints():
    test.cachechecker.check(
        qcetl.picard.crosscheckfingerprints.CrosscheckFingerprintsCache(),
        [
            {
                "file": "test/files/crosscheckfingerprints/crosscheckfingerprints.crosscheck_metrics.txt",
                "swid": "SWID",
                "version": "1.0",
            }
        ],
        {
            4: {
                "filterswaps": "test/files/crosscheckfingerprints/crosscheckfingerprints.filterswaps.csv",
            }
        },
    )


def tests_picard_crosscheckfingerprints_complex():
    test.cachechecker.check(
        qcetl.picard.crosscheckfingerprints.CrosscheckFingerprintsCache(),
        [
            {
                "file": "test/files/crosscheckfingerprints/crosscheckfingerprints.complex.crosscheck_metrics.txt",
                "swid": "SWID",
                "version": "1.0",
            }
        ],
        {
            4: {
                "filterswaps": "test/files/crosscheckfingerprints/crosscheckfingerprints.complex.filterswaps.csv",
            }
        },
    )


def tests_picard_crosscheckfingerprints_version2():
    test.cachechecker.check(
        qcetl.picard.crosscheckfingerprints.CrosscheckFingerprintsCache(),
        [
            {
                "file": "test/files/crosscheckfingerprints/crosscheckfingerprints_version2.crosscheck_metrics.txt",
                "swid": "SWID",
                "version": "2.0",
            }
        ],
        {
            4: {
                "filterswaps": "test/files/crosscheckfingerprints/crosscheckfingerprints_version2.filterswaps.csv",
            }
        },
    )
