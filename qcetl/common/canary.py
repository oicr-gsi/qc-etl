from typing import Dict
from pandas import DataFrame

import qcetl.common
import qcetl.column


class QcEtlCanaryColumn(qcetl.column.BaseColumn):
    Number = "number"
    Key = "key"


class QcEtlCanary(qcetl.common.Cache):
    def __init__(self):
        self.name = "qcetl_canary"
        self.schema_versions = {
            1: {
                "canary": {
                    QcEtlCanaryColumn.Number: "i",
                    QcEtlCanaryColumn.Key: "s",
                }
            }
        }
        self.columns = {1: {"canary": QcEtlCanaryColumn}}
        self.input_format = {"number": "i", "key": "s"}
        self.primary_key = {1: {"canary": [QcEtlCanaryColumn.Key]}}

        self.input_key = {1: ("key", QcEtlCanaryColumn.Key)}

    def parse_single_record(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, DataFrame]:
        return {"canary": DataFrame({"number": [single_input["number"]]})}

    def add_shesmu_metadata(
        self, single_input: dict, schema_version: int
    ) -> Dict[str, Dict[str, str]]:
        return {"canary": {QcEtlCanaryColumn.Key: single_input["key"]}}
