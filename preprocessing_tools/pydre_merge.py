#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

import pydre.merge_tool
import os.path
import glob
#import logging
#logging.basicConfig(level=logging.INFO)

import argparse
parser = argparse.ArgumentParser()
#command line arguments for project file (pf) and data file (df)
parser.add_argument("-d","--mergeDirectory", type= str, help="the directory of files to merge", required = True)
parser.add_argument("-t","--mergeType", type= str, help="the type of merge to perform", required = True)

#Maybe add this in later? No logging utilities in merge tool right now.
#parser.add_argument("-l", "--warninglevel", type= str, default="WARNING", help="Loggging error level. DEBUG, INFO, WARNING, ERROR, and CRITICAL are allowed.")

args = parser.parse_args()

p = pydre.merge_tool.MergeTool(args.mergeDirectory, args.mergeType)



