# -*- coding: utf-8 -*-

import json
import pandas
import re
import sys
import pydre.core
import pydre.rois
import pydre.metrics

import logging
logger = logging.getLogger('PydreLogger')


class Project():

	def __init__(self, projectfilename):
		self.project_filename = projectfilename
		self.definition = None
		with open(self.project_filename) as project_file:
			try:
				self.definition = json.load(project_file)
			except json.decoder.JSONDecodeError as e:
				# The exact location of the error according to the exception, is a little wonky. Amongst all the text
				# 	editors used, the line number was consistently 1 more than the actual location of the syntax error.
				# 	Hence, the "e.lineno -1" in the logger error below.

				logger.error("In " + projectfilename + ": " + str(e.msg) + ". Invalid JSON syntax found at Line: "
								+ str(e.lineno - 1) + ".")
				# exited as a general error because it is seemingly best suited for the problem encountered
				sys.exit(1)

		self.data = []

	def __loadSingleFile(self, filename):
		"""Load a single .dat file (whitespace delmited csv) into a DriveData object"""
		# Could cache this re, probably affect performance
		d = pandas.read_csv(filename, sep='\s+', na_values='.')
		datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")
		match = datafile_re.search(filename)
		experiment_name, subject_id, drive_id = match.groups()
		return pydre.core.DriveData(SubjectID=int(subject_id), DriveID=int(drive_id),
									roi=None, data=d, sourcefilename=filename)

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

	def processMetric(self, metric, dataset):
		"""
		Handles running any metric defninition

		Args:
			metric: A dict containing the type of a metric and the parameters to process it

		Returns:
			A list of values with the results
		"""

		try:
			func_name = metric.pop('function')
			metric_func = pydre.metrics.metricsList[func_name]
			report_name = metric.pop('name')
			col_names = pydre.metrics.metricsColNames[func_name]
		except KeyError as e:
			logger.warning("Metric definitions require both \"name\" and \"function\". Malformed metrics definition: missing " + str(e))
			raise e

		if len(col_names) > 1:
			x = [metric_func(d, **metric) for d in dataset]
			report = pandas.DataFrame(x, columns=col_names)
		else:
			report = pandas.DataFrame([metric_func(d, **metric) for d in dataset], columns=[report_name,])
		return report

	def loadFileList(self, datafiles):
		"""
		Args:
			datafiles: a list of filename strings (SimObserver .dat files)

		Loads all datafiles into the project raw data list.
		Before loading, the internal list is cleared.
		"""
		self.raw_data = []
		for datafile in datafiles:
			logger.info("Loading file #{}: {}".format(len(self.raw_data), datafile))
			self.raw_data.append(self.__loadSingleFile(datafile))

	def run(self, datafiles):
		"""
		Args:
			datafiles: a list of filename strings (SimObserver .dat files)

		Load all files in datafiles, then process the rois and metrics
		"""

		self.loadFileList(datafiles)
		data_set = []
		if 'rois' in self.definition:
			for roi in self.definition['rois']:
				data_set.extend(self.processROI(roi, self.raw_data))
		else:
			# no ROIs to process, but that's OK
			logger.warning("No ROIs, processing raw data.")
			data_set = self.raw_data

		logger.info("number of datafiles: {}, number of rois: {}".format(len(datafiles), len(data_set)))

		result_data = pandas.DataFrame()
		result_data['Subject'] = pandas.Series([d.SubjectID for d in data_set])
		result_data['DriveID'] = pandas.Series([d.DriveID for d in data_set])
		result_data['ROI'] = pandas.Series([d.roi for d in data_set])
		processed_metrics = [result_data]

		for metric in self.definition['metrics']:
			processed_metric = self.processMetric(metric, data_set)
			processed_metrics.append(processed_metric)
		result_data = pandas.concat(processed_metrics, axis=1)
		self.results = result_data
		return result_data


	def save(self, outfilename="out.csv"):
		"""
		Args:
			outfilename: filename to output csv data to.

		The filename specified will be overwritten automatically.
		"""
		
		try:
			self.results.to_csv(outfilename, index=False)
		except AttributeError:
			logger.error("Results not computed yet")
