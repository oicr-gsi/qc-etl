import csv
import pandas as pd
from pandas import DataFrame
from qcetl.column import PurityQcPurpleColumn as PurpleColumn
from qcetl.common import InvalidRecordError


def parse_record(purple_purity_input: str) -> DataFrame:
    # Read purple purity input tsv and making a dataframe
    try:
        with open(purple_purity_input, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            purple_purity_input_data = [row for row in reader]
            if not purple_purity_input_data:
                raise InvalidRecordError(
                    "File is empty or only contains headers"
                )

    except InvalidRecordError as e:
        print(f"Invalid Record Error: {e}")
        raise

    result = {
        column: []
        for column in [
            PurpleColumn.Purity,
            PurpleColumn.Ploidy,
            PurpleColumn.NormFactor,
            PurpleColumn.Score,
            PurpleColumn.DiploidProportion,
            PurpleColumn.PolyclonalProportion,
            PurpleColumn.MinPurity,
            PurpleColumn.MaxPurity,
            PurpleColumn.MinPloidy,
            PurpleColumn.MaxPloidy,
            PurpleColumn.MinDiploidProportion,
            PurpleColumn.MaxDiploidProportion,
            PurpleColumn.SomaticPenalty,
        ]
    }
    for row in purple_purity_input_data:
        for column in result.keys():
            result[column].append(row[column])

    purple_df = pd.DataFrame(result)

    return purple_df
