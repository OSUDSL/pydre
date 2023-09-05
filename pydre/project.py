# -*- coding: utf-8 -*-

import json
import polars as pl
import re
import sys
import pydre.core
import pydre.rois
import pydre.metrics
import ntpath
from pydre.metrics import *
from pydre.filters import *
import pathlib
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class Project:
    def __init__(self,  projectfilename: str, progressbar=None, app=None):
        self.app = app
        self.project_filename = projectfilename
        self.progress_bar = progressbar

        # This will suppress the unnecessary SettingWithCopy Warning.
        #pandas.options.mode.chained_assignment = None

        self.definition = None
        with open(self.project_filename) as project_file:
            try:
                self.definition = json.load(project_file)
            except json.decoder.JSONDecodeError as e:
                # The exact location of the error according to the exception, is a little wonky. Amongst all the text
                # 	editors used, the line number was consistently 1 more than the actual location of the syntax error.
                # 	Hence, the "e.lineno -1" in the logger error below.

                logger.critical("In " + projectfilename + ": " + str(e.msg) + ". Invalid JSON syntax found at Line: "
                             + str(e.lineno - 1) + ".")
                # exited as a general error because it is seemingly best suited for the problem encountered
                sys.exit(1)

        self.data = []

    def __loadSingleFile(self, filename: str):
        file = ntpath.basename(filename)
        """Load a single .dat file (space delimited csv) into a DriveData object"""
        d = pl.read_csv(filename, separator=' ', null_values='.', truncate_ragged_lines=True)
        datafile_re_format0 = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")  # old format
        datafile_re_format1 = re.compile(
            "([^_]+)_([^_]+)_([^_]+)_(\d+)(?:.*).dat")  # [mode]_[participant id]_[scenario name]_[uniquenumber].dat
        match_format0 = datafile_re_format0.search(filename)
        if match_format0:
            experiment_name, subject_id, drive_id = match_format0.groups()
            drive_id = int(drive_id) if drive_id and drive_id.isdecimal() else None
            return pydre.core.DriveData.initV2(d, filename, subject_id, drive_id)
        elif match_format1 := datafile_re_format1.search(
                file):  # assign bool value to var "match_format1", only available in python 3.8 or higher
            mode, subject_id, scen_name, unique_id = match_format1.groups()
            return pydre.core.DriveData.initV4(d, filename, subject_id, unique_id, scen_name, mode)
        else:
            logger.warning(
                "Drivedata filename {} does not an expected format.".format(filename))
            return pydre.core.DriveData(d, filename)

    def processROI(self, roi, dataset):
        """
                Handles running region of interest definitions for a dataset

                Args:
                        roi: A dict containing the type of a roi and the filename of the data used to process it
                        dataset: a list of pandas dataframes containing the source data to partition

                Returns:
                        A list of pandas DataFrames containing the data for each region of interest
                """
        roi_type = roi['type']
        if roi_type == "time":
            logger.info("Processing ROI file " + roi['filename'])
            roi_obj = pydre.rois.TimeROI(roi['filename'])
            return roi_obj.split(dataset)
        elif roi_type == "rect":
            logger.info("Processing ROI file " + roi['filename'])
            roi_obj = pydre.rois.SpaceROI(roi['filename'])
            return roi_obj.split(dataset)
        elif roi_type == "column":
            logger.info("Processing ROI column " + roi['columnname'])
            roi_obj = pydre.rois.ColumnROI(roi['columnname'])
            return roi_obj.split(dataset)
        else:
            return []

    def processFilter(self, filter, dataset):
        """
        Handles running any filter definition

        Args:
            filter: A dict containing the type of a filter and the parameters to process it

        Returns:
            A list of values with the results
        """

        try:
            func_name = filter.pop('function')
            filter_func = pydre.filters.filtersList[func_name]
            report_name = filter.pop('name')
            col_names = pydre.filters.filtersColNames[func_name]
        except KeyError as e:
            logger.warning(
                "Filter definitions require both \"name\" and \"function\". Malformed filters definition: missing " + str(
                    e))
            sys.exit(1)

        x = []
        if len(col_names) > 1:
            for d in tqdm(dataset, desc=func_name):
                x.append(d)
                if self.progress_bar:
                    value = self.progress_bar.value() + 100.0 / len(dataset)
                    self.progress_bar.setValue(value)
                if self.app:
                    self.app.processEvents()
            report = pl.DataFrame(x, schema=col_names)
        else:
            for d in tqdm(dataset, desc=func_name):
                x.append(filter_func(d, **filter))
                if self.progress_bar:
                    value = self.progress_bar.value() + 100.0 / len(dataset)
                    self.progress_bar.setValue(value)
                if self.app:
                    self.app.processEvents()
            report = pl.DataFrame(x, schema=[report_name, ])

        return report

    def processMetric(self, metric: object, dataset: list) -> pl.DataFrame:
        """

        :param metric:
        :param dataset:
        :return:
        """
        try:
            func_name = metric.pop('function')
            metric_func = pydre.metrics.metricsList[func_name]
            report_name = metric.pop('name')
            col_names = pydre.metrics.metricsColNames[func_name]
        except KeyError as e:
            logger.warning(
                "Metric definitions require both \"name\" and \"function\". Malformed metrics definition: missing " + str(
                    e))
            sys.exit(1)

        if len(col_names) > 1:
            x = [metric_func(d, **metric) for d in tqdm(dataset, desc=report_name)]
            report = pl.DataFrame(x, schema=col_names)
        else:
            report = pl.DataFrame(
                [metric_func(d, **metric) for d in tqdm(dataset, desc=report_name)], schema=[report_name, ])

        return report

    def loadFileList(self, datafiles):
        """
                Args:
                        datafiles: a list of filename strings (SimObserver .dat files)

                Loads all datafiles into the project raw data list.
                Before loading, the internal list is cleared.
                """
        self.raw_data = []
        for datafile in tqdm(datafiles, desc="Loading files"):
            logger.info("Loading file #{}: {}".format(
                len(self.raw_data), datafile))
            self.raw_data.append(self.__loadSingleFile(datafile))
            if self.progress_bar:
                value = self.progress_bar.value() + 100.0 / len(datafiles)
                self.progress_bar.setValue(value)
            if self.app:
                self.app.processEvents()

    # remove any parenthesis, quote mark and un-necessary directory names from a str
    def __clean(self, string):
        return string.replace('[', '').replace(']', '').replace('\'', '').split("\\")[-1]

    def run(self, datafiles):
        """
                Args:
                        datafiles: a list of filename strings (SimObserver .dat files)

                Load all files in datafiles, then process the rois and metrics
                """

        self.loadFileList(datafiles)
        data_set = []

        if 'filters' in self.definition:
            for filter in self.definition['filters']:
                self.processFilter(filter, self.raw_data)

        if 'rois' in self.definition:
            for roi in self.definition['rois']:
                data_set.extend(self.processROI(roi, self.raw_data))
        else:
            # no ROIs to process, but that's OK
            logger.warning("No ROIs, processing raw data.")
            data_set = self.raw_data

        logger.info("number of datafiles: {}, number of rois: {}".format(
            len(datafiles), len(data_set)))

        # for filter in self.definition['filters']:
        #     self.processFilter(filter, data_set)
        result_data = pl.DataFrame()
        result_data.hstack([pl.Series("Subject", [d.PartID for d in data_set])], in_place=True)

        if (data_set[0].format_identifier == 2):  # these drivedata object was created from an old format data file
            result_data.hstack([pl.Series("DriveID", [d.DriveID for d in data_set])], in_place=True)
        elif (data_set[
                  0].format_identifier == 4):  # these drivedata object was created from a new format data file ([mode]_[participant id]_[scenario name]_[uniquenumber].dat)
            result_data.hstack([
                pl.Series("Mode", [self.__clean(str(d.mode)) for d in data_set]),
                pl.Series("ScenarioName", [self.__clean(str(d.scenarioName)) for d in data_set]),
                pl.Series("UniqueID", [self.__clean(str(d.UniqueID)) for d in data_set])

            ], in_place=True)

        result_data.hstack([pl.Series("ROI", [d.roi for d in data_set])], in_place=True)

        if 'metrics' not in self.definition:
            logger.critical("No metrics in project file. No results will be generated")
            return None
        else:
            for metric in self.definition['metrics']:
                processed_metric = self.processMetric(metric, data_set)
                result_data.hstack(processed_metric, in_place=True)
#        except pydre.core.ColumnsMatchError as e:
#            logger.critical(f"Failed to match columns: {e.missing_columns}. No results will be generated")
#           return None

        self.results = result_data
        return result_data

    def save(self, outfilename="out.csv"):
        """
        Args:
            outfilename: filename to output csv data to.

            The filename specified will be overwritten automatically.
        """
        try:
            self.results.write_csv(outfilename)
        except AttributeError:
            logger.error("Results not computed yet")
