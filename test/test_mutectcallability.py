import qcetl.mutectcallability
import test.cachechecker


def tests_mutectcallability():
    test.cachechecker.check(
        qcetl.mutectcallability.MutectCallabilityCache(),
        [
            {
                "donor": "TEST_0001",
                "file": "test/files/mutectcallability/mutect_callability.snvs.callability_metrics.json",
                "group_id": "G",
                "library_design": "NN",
                "pinery_lims_ids": ["ID1", "ID2"],
                "project": "PROJ",
                "swid": "SWID",
                "tissue_origin": "nn",
                "tissue_type": "P",
            }
        ],
        {
            "mutectcallability": "test/files/mutectcallability/mutect_callability.snvs.callability_metrics.csv"
        },
    )
