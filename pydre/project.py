import json
import polars as pl
import re
import sys
import os
from typing import Dict, List
import pydre.core
import pydre.rois
import pydre.metrics
import ntpath
from pydre.metrics import *
from pydre.filters import *
import pathlib
from loguru import logger
from tqdm import tqdm
import concurrent.futures


class Project:
    def __init__(self, projectfilename: str, progressbar=None, app=None):
        self.app = app
        self.project_filename = projectfilename
        self.progress_bar = progressbar

        # This will suppress the unnecessary SettingWithCopy Warning.
        # pandas.options.mode.chained_assignment = None

        self.definition = None
        with open(self.project_filename) as project_file:
            try:
                self.definition = json.load(project_file)
            except json.decoder.JSONDecodeError as e:
                # The exact location of the error according to the exception, is a little wonky. Amongst all the text
                # 	editors used, the line number was consistently 1 more than the actual location of the syntax error.
                # 	Hence, the "e.lineno -1" in the logger error below.

                logger.critical(
                    "In "
                    + projectfilename
                    + ": "
                    + str(e.msg)
                    + ". Invalid JSON syntax found at Line: "
                    + str(e.lineno - 1)
                    + "."
                )
                # exited as a general error because it is seemingly best suited for the problem encountered
                sys.exit(1)

        self.data = []

    def __loadSingleFile(self, filename: str) -> pydre.core.DriveData:
        file = ntpath.basename(filename)
        """Load a single .dat file (space delimited csv) into a DriveData object"""
        d = pl.read_csv(
            filename,
            separator=" ",
            null_values=".",
            truncate_ragged_lines=True,
            infer_schema_length=5000,
        )
        datafile_re_format0 = re.compile(
            "([^_]+)_Sub_(\\d+)_Drive_(\\d+)(?:.*).dat"
        )  # old format
        datafile_re_format1 = re.compile(
            "([^_]+)_([^_]+)_([^_]+)_(\\d+)(?:.*).dat"
        )  # [mode]_[participant id]_[scenario name]_[uniquenumber].dat
        match_format0 = datafile_re_format0.search(filename)

        if match_format0:
            experiment_name, subject_id, drive_id = match_format0.groups()
            drive_id = int(drive_id) if drive_id and drive_id.isdecimal() else None
            return pydre.core.DriveData.initV2(d, filename, subject_id, drive_id)
        elif (
            match_format1 := datafile_re_format1.search(file)
        ):  # assign bool value to var "match_format1", only available in python 3.8 or higher
            mode, subject_id, scen_name, unique_id = match_format1.groups()
            return pydre.core.DriveData.initV4(
                d, filename, subject_id, unique_id, scen_name, mode
            )
        else:
            logger.warning(
                "Drivedata filename {} does not an expected format.".format(filename)
            )
            return pydre.core.DriveData(d, filename)

    # testing

    def processROI(self, roi: Dict[str, str], dataset: List[pl.DataFrame]):
        """
        Handles running region of interest definitions for a dataset

        Args:
                roi: A dict containing the type of a roi and the filename of the data used to process it
                dataset: a list of polars dataframes containing the source data to partition

        Returns:
                A list of polars DataFrames containing the data for each region of interest
        """
        roi_type = roi["type"]
        if roi_type == "time":
            logger.info("Processing ROI file " + roi["filename"])
            roi_obj = pydre.rois.TimeROI(roi["filename"])
            return roi_obj.split(dataset)
        elif roi_type == "rect":
            logger.info("Processing ROI file " + roi["filename"])
            roi_obj = pydre.rois.SpaceROI(roi["filename"])
            return roi_obj.split(dataset)
        elif roi_type == "column":
            logger.info("Processing ROI column " + roi["columnname"])
            roi_obj = pydre.rois.ColumnROI(roi["columnname"])
            return roi_obj.split(dataset)
        else:
            return []

    def processROISingle(self, roi, datafile):
        """
        Handles running region of interest definitions for a dataset

        Args:
                roi: A dict containing the type of a roi and the filename of the data used to process it
                dataset: a list of polars dataframes containing the source data to partition

        Returns:
                A list of polars DataFrames containing the data for each region of interest
        """
        roi_type = roi["type"]
        dataset = [datafile]
        try:
            if roi_type == "time":
                logger.info("Processing time ROI " + roi["filename"])
                roi_obj = pydre.rois.TimeROI(roi["filename"])
                return roi_obj.split(dataset)
            elif roi_type == "rect":
                logger.info("Processing space ROI " + roi["filename"])
                roi_obj = pydre.rois.SpaceROI(roi["filename"])
                return roi_obj.split(dataset)
            elif roi_type == "column":
                logger.info("Processing column ROI " + roi["columnname"])
                roi_obj = pydre.rois.ColumnROI(roi["columnname"])
                return roi_obj.split(dataset)
            else:
                return []
        except FileNotFoundError as e:
            logger.error(e.args)
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
            func_name = filter.pop("function")
            filter_func = pydre.filters.filtersList[func_name]
            report_name = filter.pop("name")
            col_names = pydre.filters.filtersColNames[func_name]
        except KeyError as e:
            logger.warning(
                'Filter definitions require both "name" and "function". Malformed filters definition: missing '
                + str(e)
            )
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
            report = pl.DataFrame(
                x,
                schema=[
                    report_name,
                ],
            )

        return report

    def processFilterSingle(self, filter, datafile):
        """
        Handles running any filter definition

        Args:
            filter: A dict containing the type of a filter and the parameters to process it

        Returns:
            A list of values with the results
        """
        filter = filter.copy()
        try:
            func_name = filter.pop("function")
            filter_func = pydre.filters.filtersList[func_name]
            report_name = filter.pop("name")
            col_names = pydre.filters.filtersColNames[func_name]
        except KeyError as e:
            logger.error(
                'Filter definitions require both "name" and "function". Malformed filters definition: missing '
                + str(e)
            )
            raise e

        x = []
        if len(col_names) > 1:
            x.append(datafile)
            if self.app:
                self.app.processEvents()
            report = pl.DataFrame(datafile, schema=col_names)
        else:
            x.append(filter_func(datafile, **filter))
            if self.app:
                self.app.processEvents()
            report = pl.DataFrame(
                x,
                schema=[
                    report_name,
                ],
            )

        return report

    def processMetric(self, metric: object, dataset: list) -> pl.DataFrame:
        """

        :param metric:
        :param dataset:
        :return:
        """
        try:
            func_name = metric.pop("function")
            metric_func = pydre.metrics.metricsList[func_name]
            report_name = metric.pop("name")
            col_names = pydre.metrics.metricsColNames[func_name]
        except KeyError as e:
            logger.error(
                'Metric definitions require both "name" and "function". Malformed metrics definition: missing '
                + str(e)
            )
            raise RuntimeError("Malformed metric call")

        if len(col_names) > 1:
            x = [metric_func(d, **metric) for d in tqdm(dataset, desc=report_name)]
            report = pl.DataFrame(x, schema=col_names)
        else:
            report = pl.DataFrame(
                [metric_func(d, **metric) for d in tqdm(dataset, desc=report_name)],
                schema=[
                    report_name,
                ],
            )

        return report

    def processMetricSingle(
        self, metric: dict, dataset: pydre.core.DriveData
    ) -> pl.DataFrame:
        """
        :param metric:
        :param dataset:
        :return:
        """

        metric = metric.copy()
        try:
            func_name = metric.pop("function")
            metric_func = pydre.metrics.metricsList[func_name]
            report_name = metric.pop("name")
            col_names = pydre.metrics.metricsColNames[func_name]
        except KeyError as e:
            logger.warning(
                'Metric definitions require both "name" and "function". Malformed metrics definition: missing '
                + str(e)
            )
            sys.exit(1)

        if len(col_names) > 1:
            x = [metric_func(dataset, **metric)]
            report = pl.DataFrame(x, schema=col_names)
        else:
            report = pl.DataFrame(
                [metric_func(dataset, **metric)],
                schema=[
                    report_name,
                ],
            )

        return report

    def processMetricSinglePar(
        self, metric: dict, dataset: pydre.core.DriveData
    ) -> dict:
        """

        :param metric:
        :param dataset:
        :return:
        """

        metric = metric.copy()
        try:
            func_name = metric.pop("function")
            metric_func = pydre.metrics.metricsList[func_name]
            report_name = metric.pop("name")
            col_names = pydre.metrics.metricsColNames[func_name]
        except KeyError as e:
            logger.warning(
                'Metric definitions require both "name" and "function". Malformed metrics definition: missing '
                + str(e)
            )
            sys.exit(1)

        metric_dict = dict()
        if len(col_names) > 1:
            x = [metric_func(dataset, **metric)]
            report = pl.DataFrame(x, schema=col_names, orient="row")
            for i in range(len(col_names)):
                name = col_names[i - 1]
                data = x[0][i]
                metric_dict[name] = data
        else:
            # report = pl.DataFrame(
            #    [metric_func(dataset, **metric) ], schema=[report_name, ])
            metric_dict[report_name] = metric_func(dataset, **metric)
        return metric_dict

    def loadFileList(self, datafiles):
        """
        Args:
                datafiles: a list of filename strings (SimObserver .dat files)

        Loads all datafiles into the project raw data list.
        Before loading, the internal list is cleared.
        """
        self.raw_data = []
        for datafile in tqdm(datafiles, desc="Loading files"):
            logger.info("Loading file #{}: {}".format(len(self.raw_data), datafile))
            self.raw_data.append(self.__loadSingleFile(datafile))
            if self.progress_bar:
                value = self.progress_bar.value() + 100.0 / len(datafiles)
                self.progress_bar.setValue(value)
            if self.app:
                self.app.processEvents()

    # remove any parenthesis, quote mark and un-necessary directory names from a str
    def __clean(self, string):
        return string.replace("[", "").replace("]", "").replace("'", "").split("\\")[-1]

    def run_par(self, datafilenames: list[str], numThreads: int = 12):
        """
        Args:
                datafilenames: a list of filename strings (SimObserver .dat files)

        Load all metrics, then iterate over each file and process the filters, rois, and metrics for each.
        """
        if "metrics" not in self.definition:
            logger.critical("No metrics in project file. No results will be generated")
            return None
        self.raw_data = []
        result_dataframe = pl.DataFrame()
        results_list = []
        # for datafilename in tqdm(datafilenames, desc="Loading files"):

        # with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
        #    for result in executor.map(self.processSingleFile, datafilenames):
        #        for result_dict in result:
        #            results_list.append(result_dict)
        with tqdm(total=len(datafilenames)) as pbar:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=numThreads
            ) as executor:
                futures = {
                    executor.submit(self.processSingleFile, singleFile): singleFile
                    for singleFile in datafilenames
                }
                results = {}
                for future in concurrent.futures.as_completed(futures):
                    arg = futures[future]
                    try:
                        results[arg] = future.result()
                    except Exception as exc:
                        executor.shutdown(cancel_futures=True)
                        logger.critical('Unhandled Exception {}'.format(exc))
                        sys.exit(1)

                    results_list.extend(future.result())
                    pbar.update(1)
        result_dataframe = pl.from_dicts(results_list)
        self.results = result_dataframe
        return result_dataframe

    def processSingleFile(self, datafilename):
        logger.info("Loading file #{}: {}".format(len(self.raw_data), datafilename))
        datafile = self.__loadSingleFile(datafilename)
        roi_datalist = []
        results_list = []

        if "filters" in self.definition:
            for filter in self.definition["filters"]:
                try:
                    self.processFilterSingle(filter, datafile)
                except Exception as e:
                    logger.exception(
                        "Unhandled exception in {} while processing {}.".format(
                            filter, datafilename
                        )
                    )
                    raise e
        if "rois" in self.definition:
            for roi in self.definition["rois"]:
                try:
                    roi_datalist.extend(self.processROISingle(roi, datafile))
                except Exception as e:
                    logger.exception(
                        "Unhandled exception in {} while processing {}.".format(
                            roi, datafilename
                        )
                    )
                    raise e

        else:
            # no ROIs to process, but that's OK
            logger.warning("No ROIs, processing raw data.")
            roi_datalist.append(datafile)

        # if len(roi_datalist) == 0:
        # logger.warning("No ROIs found in {}".format(datafilename))
        roi_processed_metrics = []
        for data in roi_datalist:
            result_dict = {"Subject": data.PartID}
            if (
                data.format_identifier == 2
            ):  # these drivedata object was created from an old format data file
                result_dict["DriveID"] = datafile.DriveID
            elif (
                data.format_identifier == 4
            ):  # these drivedata object was created from a new format data file ([mode]_[participant id]_[scenario name]_[uniquenumber].dat)
                result_dict["Mode"] = self.__clean(str(data.mode))
                result_dict["ScenarioName"] = self.__clean(str(data.scenarioName))
                result_dict["UniqueID"] = self.__clean(str(data.UniqueID))
            result_dict["ROI"] = data.roi

            for metric in self.definition["metrics"]:
                try:
                    processed_metric = self.processMetricSinglePar(metric, data)
                    result_dict.update(processed_metric)
                except Exception as e:
                    logger.critical(
                        "Unhandled exception {} in {} while processing {}.".format(
                            e.args, metric, datafilename
                        )
                    )
                    raise e
            results_list.append(result_dict)
        return results_list

    def run(self, datafilenames: list[str]):
        """
        Args:
                datafilenames: a list of filename strings (SimObserver .dat files)

        Load all metrics, then iterate over each file and process the filters, rois, and metrics for each.
        """

        self.raw_data = []
        result_dataframe = pl.DataFrame()
        for datafilename in tqdm(datafilenames, desc="Loading files"):
            logger.info("Loading file #{}: {}".format(len(self.raw_data), datafilename))
            datafile = self.__loadSingleFile(datafilename)
            data_set = []
            if self.progress_bar:
                value = self.progress_bar.value() + 100.0 / len(datafilenames)
                self.progress_bar.setValue(value)
            if self.app:
                self.app.processEvents()

            if "filters" in self.definition:
                for filter in self.definition["filters"]:
                    self.processFilterSingle(filter, datafile)
            if "rois" in self.definition:
                for roi in self.definition["rois"]:
                    data_set.extend(self.processROISingle(roi, datafile))
            else:
                # no ROIs to process, but that's OK
                logger.warning("No ROIs, processing raw data.")
                data_set.append(datafile)

            for data in data_set:
                result_dict = {"Subject": [data.PartID]}
                if (
                    data.format_identifier == 2
                ):  # these drivedata object was created from an old format data file
                    result_dict["DriveID"] = [datafile.DriveID]
                elif (
                    data.format_identifier == 4
                ):  # these drivedata object was created from a new format data file ([mode]_[participant id]_[scenario name]_[uniquenumber].dat)
                    result_dict["Mode"] = [self.__clean(str(data.mode))]
                    result_dict["ScenarioName"] = [self.__clean(str(data.scenarioName))]
                    result_dict["UniqueID"] = [self.__clean(str(data.UniqueID))]
                result_dict["ROI"] = data.roi
                if "metrics" not in self.definition:
                    logger.critical(
                        "No metrics in project file. No results will be generated"
                    )
                    return None
                else:
                    cur_metric = pl.DataFrame()
                    for metric in self.definition["metrics"]:
                        processed_metric = self.processMetricSingle(metric, data)
                        if cur_metric.is_empty():
                            cur_metric = processed_metric
                        else:
                            cur_metric.hstack(processed_metric, in_place=True)
                if result_dataframe.is_empty():
                    result_dataframe = pl.DataFrame(result_dict)
                    result_dataframe.hstack(cur_metric, in_place=True)
                else:
                    cur_dataframe = pl.DataFrame(result_dict)
                    cur_dataframe.hstack(cur_metric, in_place=True)
                    result_dataframe.vstack(cur_dataframe, in_place=True)
        logger.info(
            "number of datafiles: {}, number of rois: {}".format(
                len(datafilenames), len(data_set)
            )
        )
        print("result dataframe:", result_dataframe)
        self.results = result_dataframe
        return result_dataframe

    def run_old(self, datafiles):
        """
        Args:
                datafiles: a list of filename strings (SimObserver .dat files)

        Load all files in datafiles, then process the rois and metrics
        """

        self.loadFileList(datafiles)
        data_set = []

        if "filters" in self.definition:
            for filter in self.definition["filters"]:
                self.processFilter(filter, self.raw_data)

        if "rois" in self.definition:
            for roi in self.definition["rois"]:
                data_set.extend(self.processROI(roi, self.raw_data))
        else:
            # no ROIs to process, but that's OK
            logger.warning("No ROIs, processing raw data.")
            data_set = self.raw_data

        logger.info(
            "number of datafiles: {}, number of rois: {}".format(
                len(datafiles), len(data_set)
            )
        )

        # for filter in self.definition['filters']:
        #     self.processFilter(filter, data_set)
        result_data = pl.DataFrame()
        result_data.hstack(
            [pl.Series("Subject", [d.PartID for d in data_set])], in_place=True
        )
        if (
            data_set[0].format_identifier == 2
        ):  # these drivedata object was created from an old format data file
            result_data.hstack(
                [pl.Series("DriveID", [d.DriveID for d in data_set])], in_place=True
            )
        elif (
            data_set[0].format_identifier == 4
        ):  # these drivedata object was created from a new format data file ([mode]_[participant id]_[scenario name]_[uniquenumber].dat)
            result_data.hstack(
                [
                    pl.Series("Mode", [self.__clean(str(d.mode)) for d in data_set]),
                    pl.Series(
                        "ScenarioName",
                        [self.__clean(str(d.scenarioName)) for d in data_set],
                    ),
                    pl.Series(
                        "UniqueID", [self.__clean(str(d.UniqueID)) for d in data_set]
                    ),
                ],
                in_place=True,
            )

        result_data.hstack([pl.Series("ROI", [d.roi for d in data_set])], in_place=True)

        if "metrics" not in self.definition:
            logger.critical("No metrics in project file. No results will be generated")
            return None
        else:
            for metric in self.definition["metrics"]:
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
