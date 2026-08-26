import test.cachechecker
from qcetl.ultimamethylcontrol import UltimaMethylControlCache


def tests_ultimamethylcontrol():
    test.cachechecker.check(
        UltimaMethylControlCache(),
        [
            {
                "path": "test/files/ultimamethylcontrol/446499-Example1_Pl_T_nn_1-1_LB04-01-Z0012-CTGCCATAGCACGAT_mergeContext.csv",
                "barcode": "CTGCCATAGCACGAT",
                "run": "446499-20260727_1147",
                "pinery_lims_id": "ID1",
            },
            {
                "path": "test/files/ultimamethylcontrol/446499-Example2_Ct_T_nn_2-2_LB05-01-Z0009-CGCGCATCCTGCATGAT_mergeContext.csv",
                "barcode": "CGCGCATCCTGCATGAT",
                "run": "446499-20260727_1147",
                "pinery_lims_id": "ID2",
            },
        ],
        {
            "ultimamethylcontrol": "test/files/ultimamethylcontrol/ultimamethylcontrol.csv"
        },
    )
