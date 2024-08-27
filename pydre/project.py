import json
import polars as pl
import re
import sys
import tomllib
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
    project_filename: pathlib.Path
    definition: dict

    def __init__(self, projectfilename: str):
        self.project_filename = pathlib.Path(projectfilename)
        self.definition = {}
        with open(self.project_filename, 'rb') as project_file:
            if self.project_filename.suffix == ".json":
                try:
                    self.definition = json.load(project_file)
                except json.decoder.JSONDecodeError as e:
                    logger.exception("Error parsing JSON in {}".format(self.project_filename), exception=e)
                    # exited as a general error because it is seemingly best suited for the problem encountered
                    sys.exit(1)
            elif self.project_filename.suffix == ".toml":
                try:
                    self.definition = tomllib.load(project_file)
                except tomllib.TOMLDecodeError as e:
                    logger.exception("Error parsing TOML in {}".format(self.project_filename), exception=e)
                # convert toml to previous project structure:
                new_definition = {}
                if "rois" in self.definition.keys():
                    new_definition["rois"] = Project.__restructureProjectDefinition(self.definition["rois"])
                if "metrics" in self.definition.keys():
                    new_definition["metrics"] = Project.__restructureProjectDefinition(self.definition["metrics"])
                if "filters" in self.definition.keys():
                    new_definition["filters"] = Project.__restructureProjectDefinition(self.definition["filters"])
                self.definition = new_definition
            else:
                logger.error("Unsupported project file type")
                sys.exit(1)

        self.data = []

    @staticmethod
    def __restructureProjectDefinition(def_dict: dict) -> list:
        new_def = []
        for k, v in def_dict.items():
            v['name'] = k
            new_def.append(v)
        return new_def

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
            report = pl.DataFrame(datafile, schema=col_names)
        else:
            x.append(filter_func(datafile, **filter))
            report = pl.DataFrame(
                x,
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
