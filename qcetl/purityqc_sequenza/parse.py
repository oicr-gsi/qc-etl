"""Extract metrics from Sequenza results; gamma parameter can be chosen automatically or supplied by the user"""

import csv
import logging
import math
import os
import re
import tempfile
import zipfile
import pandas as pd
from pandas import DataFrame
from qcetl.column import PurityQcSequenzaColumn as SequenzaColumn
from qcetl.common import InvalidRecordError

SEQUENZA_PRIMARY_SOLUTION = "_primary_"


class sequenza_reader:
    def __init__(self, zip_path, log_level=logging.WARNING, log_path=None):
        """
        Decompress the zip archive to a temporary directory
        Read values for gamma and purity/ploidy; find default gamma
        """
        self.zip_path = zip_path
        self.logger = logging.getLogger(__name__)
        self.segment_counts = {}
        self.purity = {}
        self.ploidy = {}
        self.cn_seg_archive = {}  # archive paths to CN.seg files
        self.segments_text_archive = {}  # archive paths to _segments.txt files
        tempdir = tempfile.TemporaryDirectory(prefix="djerba_sequenza_")
        tmp = tempdir.name
        # zip archives are large (~500 MB) -- only extract the files we need
        # Sequenza archives *should* have correct file contents, but we do some basic sanity checking
        #
        # Sequenza outputs one or more solutions for each value of the gamma parameter
        # We define a solution ID, designated 'sol_id'
        # 'sol_id' is the value of gamma, plus the solution designator ('_primary_', 'sol2_0.49', etc.)
        zf = zipfile.ZipFile(self.zip_path)
        sol_id_set = set()
        # zeroth pass -- get the list of filenames, excluding directories
        name_list = [x for x in zf.namelist() if not re.search("/$", x)]
        # first pass -- populate the canonical set of gamma IDs
        for name in name_list:
            if re.search("/$", name):
                continue
            sol_id = self._parse_sol_id(name)
            sol_id_set.add(sol_id)
        self.sol_ids = sorted(list(sol_id_set))
        # second pass -- parse metrics and file locations
        for name in name_list:
            sol_id = self._parse_sol_id(name)
            gamma = sol_id[0]
            if re.search(r"_segments\.txt$", name):
                # _segments.txt files vary for different solutions on the same gamma
                if sol_id in self.segment_counts:
                    msg = "Multiple _segments.txt for sol_id {0}".format(sol_id)
                    self.logger.error(msg)
                    raise InvalidRecordError(msg)
                self.segment_counts[sol_id] = self._count_segments(
                    zf.extract(name, tmp)
                )
                self.segments_text_archive[sol_id] = name
            elif re.search(
                r"_alternative_solutions\.txt$", name
            ) and self._is_primary(sol_id):
                # Only one distinct alternative_solutions.txt for each value of gamma
                self._update_purity_ploidy(gamma, zf.extract(name, tmp))
            elif re.search("_Total_CN.seg", name) and self._is_primary(sol_id):
                # Only one .seg file for each value of gamma
                if gamma in self.cn_seg_archive:
                    msg = "Multiple .seg files for gamma {0}".format(gamma)
                    self.logger.error(msg)
                    raise InvalidRecordError(msg)
                self.cn_seg_archive[gamma] = name
        # check required info is present for each sol_id
        for sol_id in self.sol_ids:
            msg = None
            if sol_id not in self.segment_counts:
                msg = "Missing segment count for sol_id {0}".format(sol_id)
            elif sol_id not in self.purity or sol_id not in self.ploidy:
                msg = "Missing purity/ploidy for sol_id {0}".format(sol_id)
            elif sol_id[0] not in self.cn_seg_archive:
                msg = "Missing .seg location for gamma {0}".format(sol_id[0])
            if msg:
                self.logger.error(msg)
                raise InvalidRecordError(msg)
        tempdir.cleanup()
        # find important values of sol_id
        [
            self.default_sol_id,
            self.sol_id_selection_table,
        ] = self._find_default_sol_id()
        [
            self.min_purity,
            self.max_purity,
            self.min_purity_sol_id,
            self.max_purity_sol_id,
        ] = self._find_minmax_purity_sol_id()

    def _construct_sol_id(self, gamma=None, solution=None):
        """
        Construct a gamma ID from the given gamma and solution (if any), defaults otherwise
        Raise an error if resulting gamma ID is unknown
        """
        self.logger.debug(
            "Constructing gamma ID with inputs gamma={0}, solution={1}".format(
                gamma, solution
            )
        )
        if gamma:
            if solution:
                sol_id = (gamma, solution)
            else:
                sol_id = (gamma, SEQUENZA_PRIMARY_SOLUTION)
        else:
            sol_id = self.default_sol_id
        if sol_id not in self.sol_ids:
            msg = "solution ID {0} not found in '{1}'; ".format(
                sol_id, self.zip_path
            ) + "available IDs are: {0}".format(self.sol_ids)
            self.logger.error(msg)
            raise InvalidRecordError(msg)
        return sol_id

    def _count_segments(self, seg_path):
        """Count the number of segments; equal to length of file, excluding the header"""
        with open(seg_path) as seg:
            length = len(seg.readlines())
        return length - 1

    def _find_default_sol_id(self):
        """
        Gamma heuristic:
        - Only consider the primary (most probable) solution for each gamma
        - Draw a straight line between least and greatest gamma (usually 50 and 2000, respectively),
          to get the "expected gradient"
        - We want to find the transition from steeper-than-linear to shallower-than-linear
        - Compare actual gradient between N-1th and Nth gamma with expected linear gradient
        - (This takes account of non-equal gamma intervals)
        - When actual gradient is less in magnitude than expected gradient, stop and use Nth gamma
        - Return table of working values as a list of lists (may be wanted for output)
        """
        if len(self.sol_ids) == 1:
            # test data sets may contain only a single solution
            chosen_sol = self.sol_ids[0]
            working_values = [chosen_sol, "NA", "NA", "NA"]
        else:
            gammas = sorted(
                [
                    g[0]
                    for g in self.sol_ids
                    if g[1] == SEQUENZA_PRIMARY_SOLUTION
                ]
            )
            sol_min_id = (gammas[0], SEQUENZA_PRIMARY_SOLUTION)
            sol_max_id = (gammas[-1], SEQUENZA_PRIMARY_SOLUTION)
            delta_y = (
                self.segment_counts[sol_max_id]
                - self.segment_counts[sol_min_id]
            )
            delta_x = sol_max_id[0] - sol_min_id[0]
            linear_gradient = float(delta_y) / delta_x
            chosen_sol = None
            working_values = []
            # columns for working_values: ['gamma', 'segments', 'gradient', 'expected']
            working_values.append(
                [sol_min_id[0], self.segment_counts[sol_min_id], "NA", "NA"]
            )
            for i in range(1, len(gammas)):
                sol_id_now = (gammas[i], SEQUENZA_PRIMARY_SOLUTION)
                sol_id_previous = (gammas[i - 1], SEQUENZA_PRIMARY_SOLUTION)
                delta_y = (
                    self.segment_counts[sol_id_now]
                    - self.segment_counts[sol_id_previous]
                )
                delta_x = sol_id_now[0] - sol_id_previous[0]
                gradient = float(delta_y) / delta_x
                fields = [
                    sol_id_now[0],
                    self.segment_counts[sol_id_now],
                    gradient,
                    linear_gradient,
                ]
                working_values.append(fields)
                if abs(gradient) <= abs(linear_gradient) and chosen_sol is None:
                    chosen_sol = sol_id_now
        return (chosen_sol, working_values)

    def _find_minmax_purity_sol_id(self):
        """
        Find sol ID(s) with the minimum and maximum purity values
        """
        min_purity = math.inf
        max_purity = 0
        for sol_id in self.sol_ids:
            purity = self.purity[sol_id]
            if purity > max_purity:
                max_purity = purity
                max_purity_gamma = [sol_id]
            elif purity == max_purity:
                max_purity_gamma.append(sol_id)
            if purity < min_purity:
                min_purity = purity
                min_purity_gamma = [sol_id]
            elif purity == min_purity:
                min_purity_gamma.append(sol_id)
        return [min_purity, max_purity, min_purity_gamma, max_purity_gamma]

    def _is_primary(self, sol_id):
        """Does the given sol_id denote a primary solution?"""
        return sol_id[1] == SEQUENZA_PRIMARY_SOLUTION

    def _parse_sol_id(self, name):
        """
        Parse gamma ID from the name of a ZIP archive member.
        ID is a tuple of (gamma, solution identifier).
        The solution identifier is a secondary directory name (eg. 'sol2_0.49') or default value.
        """
        terms = re.split(os.sep, name)
        try:
            gamma = int(terms[1])
            solution = (
                terms[2]
                if re.match(r"sol[0-9]_[01](\.[0-9]+)?$", terms[2])
                else SEQUENZA_PRIMARY_SOLUTION
            )
            sol_id = (gamma, solution)
        except (IndexError, ValueError) as err:
            msg = "Unable to parse gamma parameter from {0} ".format(
                name
            ) + "in archive {0}".format(self.zip_path)
            self.logger.error(msg)
            raise InvalidRecordError(msg) from err
        return sol_id

    def _update_purity_ploidy(self, gamma, input_path):
        """
        Update purity and ploidy for the given gamma and alternative_solutions.txt file
        alternative_solutions.txt is identical for all solution folders; contains purity/ploidy solutions for the given gamma
        Non-primary solution names are of the form sol${COUNT}_${PURITY}
        where $COUNT is the line in the alternative_solutions.txt file (header = 0, primary solution = 1)
        Record the purity and ploidy by sol_id
        """
        count = 0
        with open(input_path, "rt") as input_file:
            reader = csv.reader(input_file, delimiter="\t")
            for row in reader:
                if count > 0:  # ignore the header row
                    [purity, ploidy, slpp] = [float(x) for x in row]
                    if count == 1:
                        solution = SEQUENZA_PRIMARY_SOLUTION
                    elif purity == 1:
                        # annoying quirk of Sequenza output naming
                        solution = "sol{0}_1".format(count)
                    else:
                        solution = "sol{0}_{1}".format(count, purity)
                    sol_id = self._construct_sol_id(gamma, solution)
                    self.purity[sol_id] = purity
                    self.ploidy[sol_id] = ploidy
                count += 1
        msg = "Found purity & ploidy for gamma={0}, input={1}".format(
            gamma, input_file
        )
        self.logger.debug(msg)


def parse_record(sequenza_input: str) -> DataFrame:
    sq_reader = sequenza_reader(sequenza_input)

    default_sol_id = sq_reader._find_default_sol_id()[0]
    x = sq_reader.min_purity_sol_id[0]
    min_purity = sq_reader.purity[x]
    min_ploidy = sq_reader.ploidy[x]

    x = sq_reader.max_purity_sol_id[0]
    max_purity = sq_reader.purity[x]
    max_ploidy = sq_reader.ploidy[x]

    sequenza_df = pd.DataFrame(
        {
            SequenzaColumn.defaultGamma: default_sol_id[0],
            SequenzaColumn.defaultPurity: sq_reader.purity[
                sq_reader.default_sol_id
            ],
            SequenzaColumn.defaultPloidy: sq_reader.ploidy[
                sq_reader.default_sol_id
            ],
            SequenzaColumn.minPurity: min_purity,
            SequenzaColumn.minPloidy: min_ploidy,
            SequenzaColumn.maxPurity: max_purity,
            SequenzaColumn.maxPloidy: max_ploidy,
        },
        index=[0],
    )

    return sequenza_df
