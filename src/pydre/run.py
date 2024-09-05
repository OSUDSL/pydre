from loguru import logger
from . import project
import sys
import pathlib
import argparse

def main():
    parser = argparse.ArgumentParser()
    # command line arguments for project file (pf) and data file (df)
    parser.add_argument(
        "-p", "--projectfile", type=str, help="the project file path", required=True
    )
    parser.add_argument(
        "-d",
        "--datafiles",
        type=str,
        help="the data file path",
        nargs="+",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        type=str,
        default="out.csv",
        help="the name of the output file",
    )
    parser.add_argument(
        "-l",
        "--warninglevel",
        type=str,
        default="WARNING",
        help="Loggging error level. DEBUG, INFO, WARNING, ERROR, and CRITICAL are allowed.",
    )
    args = parser.parse_args()
    logger.remove(0)
    try:
        logger.add(sys.stderr, level=args.warninglevel.upper())
    except Exception:
        logger.add(sys.stderr, level="WARNING")
        logger.warning("Command line log level (-l) invalid. Defaulting to WARNING")
    if args.outputfile == "out.csv":
        logger.warning("No output file specified. Defaulting to 'out.csv'")
    p = project.Project(args.projectfile)
    # test the data files
    filelist = []
    for fn in args.datafiles:
        # convert relative path to absolute path
        datapath = pathlib.Path(fn).resolve()
        datafiles = datapath.parent.glob(datapath.name)
        filelist.extend(datafiles)
    p.processDatafiles(filelist, 12)
    p.saveResults(pathlib.Path(args.outputfile))


if __name__ == "__main__":
    main()
