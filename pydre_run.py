#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.getcwd())

import pydre.project
import pydre.core
import os.path
import glob
import logging
logging.basicConfig(level=logging.INFO)


import argparse
parser = argparse.ArgumentParser()
#command line arguments for project file (pf) and data file (df)
parser.add_argument("-p","--projectfile", type= str, help="the project file path")
parser.add_argument("-d", "--datafile", type= str, help="the data file path")
parser.add_argument("-o", "--outputfile", type= str, default="out.csv", help="the name of the output file")
args = parser.parse_args()


p = pydre.project.Project(args.projectfile)
# test the data files

filelist = glob.glob(os.path.join(os.path.dirname(__file__), args.datafile))
p.run(filelist)
p.save(args.outputfile)


