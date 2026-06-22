import argparse
import collections
from os import environ
import pathlib
from typing import Type
import sys
import urllib.parse

from dotenv import load_dotenv
import numpy
import pandas
from pymongo import MongoClient
import sqlalchemy

from qcetl.column import BaseColumn
import qcetl.common
import qcetl.common.utility
import pinery.parse
from pinery.column import (
    InstrumentColumn,
    InstrumentModelColumn,
    InstrumentWithModelColumn,
    LaneProvenanceColumn,
    ProjectsColumn,
    SampleProvenanceColumn,
    SampleCategory,
    HeredityColumn,
    HeredityIndex,
    SamplesColumn,
    SamplesIndex,
    PoolsColumn,
    RunsColumn,
)

load_dotenv()


def add_missing_columns(cls: Type[BaseColumn], df):
    for column in set(cls.values()).difference(df.columns):
        df[column] = numpy.nan
    return df


SequencerRuns = collections.namedtuple("SequencerRuns", ["runs", "pools"])
SampleInfo = collections.namedtuple("SampleInfo", ["samples", "heredity"])


class PineryClient:
    """
    Access Pinery data stored via the web service
    """

    def __init__(self, pinery_url=None):
        self.pinery_url = pinery_url
        if self.pinery_url is None:
            self.pinery_url = environ.get("PINERY_URL")
        if self.pinery_url is None:
            raise TypeError(
                "Pinery URL must be specified in PINERY_URL environment "
                "variable or as argument to PineryClient"
            )

    def get_instruments(self):
        """
        Get all the sequencing instruments from Pinery
        """
        return pandas.DataFrame.from_records(
            qcetl.common.utility.load_json_from_url(
                urllib.parse.urljoin(self.pinery_url, "instruments")
            )
        ).drop(columns=["url", "model_url"])

    def get_instrument_models(self):
        """
        Get all the models (types) of sequencing instruments from Pinery
        """
        return pandas.DataFrame.from_records(
            qcetl.common.utility.load_json_from_url(
                urllib.parse.urljoin(self.pinery_url, "instrumentmodels")
            )
        ).drop(columns=["url", "instruments_url"])

    def get_instruments_with_models(self):
        """
        Get all the instruments joined up with their model information from Pinery
        """
        instruments = self.get_instruments()
        models = self.get_instrument_models()
        return pandas.merge(
            instruments,
            models,
            left_on="model_id",
            right_on="id",
            validate="many_to_one",
            suffixes=("_instrument", "_model"),
        ).drop(columns=["model_id"])

    def get_projects(self):
        """
        Get all the projects from Pinery
        """
        return pandas.DataFrame.from_records(
            qcetl.common.utility.load_json_from_url(
                urllib.parse.urljoin(self.pinery_url, "sample/projects")
            )
        )

    def get_runs(self, parse_pools=True):
        """
        Get all the run and pool information from Pinery

        Args:
            parse_pools: Should pools be parsed (the positions columns)

        Returns:

        """
        master_json = qcetl.common.utility.load_json_from_url(
            urllib.parse.urljoin(self.pinery_url, "sequencerruns")
        )

        runs, pools = pinery.parse.get_run_data_frame(master_json, parse_pools)

        return SequencerRuns(runs=runs, pools=pools)

    def get_samples(self):
        """
        Get all the samples from Pinery
        """
        master_json = qcetl.common.utility.load_json_from_url(
            urllib.parse.urljoin(self.pinery_url, "samples")
        )
        s, h = pinery.parse.get_samples_data_frame(master_json)
        df = SampleInfo(samples=s, heredity=h)
        return df


class PineryProvenanceClient:
    """
    Access Pinery data stored in a MongoDB cache
    """

    def __init__(self, mongo_url=None, provider="pinery-miso-v8"):
        self.mongo_url = mongo_url
        if self.mongo_url is None:
            self.mongo_url = environ.get("MONGO_URL")
        if self.mongo_url is None:
            raise TypeError(
                "Mongo URL must be specified in MONGO_URL environment "
                "variable or as argument to PineryProvenanceClient"
            )

        self.mongo = MongoClient(self.mongo_url)["provenance"]
        self.provider = provider

    def get_all_lanes(self):
        """
        Get all the lane provenance from the MongoDB cache

        Returns: probaby more data than you want
        """
        return self.get_lanes_by_query({})

    def get_all_samples(self):
        """
        Get all the sample provenance from the MongoDB cache

        Returns: probaby more data than you want
        """
        return self.get_samples_by_query({})

    def get_lanes_by_query(self, query):
        """
        Extract lane provenance using a MongoDB match-style query
        """
        return add_missing_columns(
            LaneProvenanceColumn,
            pandas.DataFrame(
                list(
                    self.mongo["lanes"].aggregate(
                        [
                            {"$match": {"provider": self.provider}},
                            {"$match": query},
                            {"$sort": {"lastModified": 1}},
                            {
                                "$group": {
                                    "_id": {
                                        "run": "$sequencerRunName",
                                        "lane": "$laneNumber",
                                    },
                                    "x": {"$last": "$$ROOT"},
                                }
                            },
                            {
                                "$replaceRoot": {  # Collapse nested objects into their parents
                                    "newRoot": {
                                        "$mergeObjects": [
                                            "$$ROOT.x",
                                            "$$ROOT.x.sequencerRunAttributes",
                                        ]
                                    }
                                }
                            },  # Flatten arrays
                            {"$unwind": "$instrument_name"},
                            {"$unwind": "$run_bases_mask"},
                            {"$unwind": "$sequencing_parameters"},
                            {"$unwind": "$run_dir"},
                            {
                                "$project": {
                                    column: True
                                    for column in LaneProvenanceColumn.values()
                                }
                            },
                            {"$project": {"_id": False}},
                        ],
                        allowDiskUse=True,
                    )
                )
            ),
        )

    def get_lanes_by_run(self, run):
        """
        Extract lane provenance for all lanes in a run
        """
        return self.get_lanes_by_query({"sequencerRunName": run})

    def get_lanes_by_run_and_lane(self, run, lane):
        """
        Extract lane provenance for a single lane in a run
        """
        return self.get_lanes_by_query(
            {"sequencerRunName": run, "laneNumber": str(lane)}
        )

    def get_samples_by_query(self, query):
        """
        Extract sample provenance using a MongoDB match-style query
        """
        return add_missing_columns(
            SampleProvenanceColumn,
            pandas.DataFrame(
                list(
                    self.mongo["samples"].aggregate(
                        [
                            {"$match": {"provider": self.provider}},
                            {"$match": query},
                            {"$sort": {"lastModified": 1}},
                            {
                                "$group": {
                                    "_id": {
                                        "run": "$sequencerRunName",
                                        "lane": "$laneNumber",
                                        "iusTag": "$iusTag",
                                    },
                                    "x": {"$last": "$$ROOT"},
                                }
                            },
                            {
                                "$replaceRoot": {  # Collapse nested objects into their parents
                                    "newRoot": {
                                        "$mergeObjects": [
                                            "$$ROOT.x",
                                            "$$ROOT.x.sequencerRunAttributes",
                                            "$$ROOT.x.sampleAttributes",
                                            "$$ROOT.x.studyAttributes",
                                        ]
                                    }
                                }
                            },  # Flatten arrays
                            {
                                "$unwind": {
                                    "path": "$geo_external_name",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_group_id",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_group_id_description",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_library_source_template_type",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_organism",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_prep_kit",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_purpose",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_receive_date",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_run_id_and_position",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_str_result",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_targeted_resequencing",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_template_type",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_tissue_origin",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_tissue_preparation",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_tissue_type",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$geo_tube_id",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$institute",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$instrument_name",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$run_bases_mask",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$run_dir",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$sequencing_parameters",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$subproject",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$rin",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$dv200",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$umis",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$unwind": {
                                    "path": "$sequencing_control_type",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {
                                "$project": {
                                    column: True
                                    for column in SampleProvenanceColumn.values()
                                }
                            },
                            {"$project": {"_id": False}},
                        ],
                        allowDiskUse=True,
                    )
                )
            ),
        )

    def get_samples_by_run(self, run):
        """
        Extract sample provenance for all samples in all lanes of a run
        """
        return self.get_samples_by_query({"sequencerRunName": run})

    def get_samples_by_run_and_lane(self, run, lane):
        """
        Extract sample provenance for all samples in a lane of a run
        """
        return self.get_samples_by_query(
            {"sequencerRunName": run, "laneNumber": str(lane)}
        )

    def get_samples_by_ius(self, run, lane, barcode):
        """
        Extract sample provenance for a specific IUS (run, lane, barcode triple).

        Barcodes which are None are treated as "NoIndex"
        """
        return self.get_samples_by_query(
            {
                "sequencerRunName": run,
                "laneNumber": str(lane),
                "iusTag": barcode or "NoIndex",
            }
        )

    def get_samples_by_iuses(self, run, lane, barcodes):
        """
        Extract sample provenance for the specified list of barcodes in a lane of a run

        Barcodes which are None are treated as "NoIndex"
        """
        return self.get_samples_by_query(
            {
                "sequencerRunName": run,
                "laneNumber": str(lane),
                "iusTag": {
                    "$in": [str(barcode) or "NoIndex" for barcode in barcodes]
                },
            }
        )


def dump(args):
    p = PineryProvenanceClient(args.mango_url, args.provider)
    if args.data_source == "sample":
        df = p.get_all_samples()
    elif args.data_source == "lane":
        df = p.get_all_lanes()
    else:
        sys.stderr.write("Unknown data source")
        return 1
    if args.to_sqlite is None:
        print(df.to_csv(index=False, encoding="utf-8"))
    else:
        engine = sqlalchemy.create_engine("sqlite:///" + str(args.to_sqlite))
        df.to_sql(
            "pinery",
            engine,
            if_exists="replace",
            dtype={
                # No automatic conversation of list/dicts
                "geo_qubit_concentration": sqlalchemy.JSON,
                "geo_nanodrop_concentration": sqlalchemy.JSON,
                "geo_tissue_region": sqlalchemy.JSON,
                "workflow_type": sqlalchemy.JSON,
            },
        )

    return 0


def load_db(path):
    engine = sqlalchemy.create_engine(path)
    return pandas.read_sql_table("pinery", engine)


def main():
    parser = argparse.ArgumentParser(prog="qcetl-mongodb")
    subparsers = parser.add_subparsers()
    parser_dump = subparsers.add_parser(
        "dump", help="Dumps Mongo DB Provenance data."
    )
    parser_dump.add_argument(
        "--mango-url",
        dest="mango_url",
        type=str,
        help="If not provided, uses MONGO_URL environmental variable.",
    )
    parser_dump.add_argument(
        "--provider",
        type=str,
        default="pinery-miso-v8",
        help="Defaults to %(default)s.",
    )
    parser_dump.add_argument(
        "--to-sqlite",
        dest="to_sqlite",
        type=pathlib.Path,
        help="If file path provided, dump to sqlite instead of CSV to stdout.",
    )
    parser_dump.add_argument(
        "data_source",
        choices=["sample", "lane"],
        help="Dump sample or lane data.",
    )
    parser_dump.set_defaults(func=dump)

    args = parser.parse_args()
    args.func(args)
