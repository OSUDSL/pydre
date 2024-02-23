#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

import pydre.project
import pydre.core
import os.path
import glob
import logging
import datetime
import argparse

parser = argparse.ArgumentParser()
# command line arguments for project file (pf) and data file (df)
parser.add_argument("-p", "--projectfile", type=str, help="the project file path", required=True)
parser.add_argument("-d", "--datafiles", type=str, help="the data file path", nargs="+", required=True)
parser.add_argument("-o", "--outputfile", type=str, default="out.csv", help="the name of the output file")
parser.add_argument("-l", "--warninglevel", type=str, default="WARNING",
                    help="Loggging error level. DEBUG, INFO, WARNING, ERROR, and CRITICAL are allowed.")

args = parser.parse_args()

logger = logging.getLogger()

try:
    logger.setLevel(args.warninglevel.upper())
except Exception:
    logger.setLevel(logging.WARNING)
    logger.warning("Command line log level (-l) invalid. Defaulting to WARNING")

if args.outputfile == 'out.csv':
    logger.warning("No output file specified. Defaulting to 'out.csv'")

p = pydre.project.Project(args.projectfile)

# test the data files
filelist = []
for fn in args.datafiles:
    filelist.extend(glob.glob(os.path.join(os.getcwd(), fn)))
p.run_par(filelist, 12)
p.save(args.outputfile)
