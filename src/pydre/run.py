import os
from loguru import logger
from pydre import project
import sys
import argparse
from typing import List, Optional


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Set up argparse based parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--projectfile", type=str, help="the project file path", required=True
    )
    parser.add_argument(
        "-d", "--datafiles", type=str, help="the data file path", nargs="+"
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        type=str,
        help="the name of the output file",
        default="out.csv",
    )
    parser.add_argument(
        "-l",
        "--warninglevel",
        type=str,
        default="WARNING",
        help="Loggging error level. DEBUG, INFO, WARNING, ERROR, and CRITICAL are allowed.",
    )
    return parser.parse_args(args)


def setup_logging(level: str) -> str:
    """Set up logging with the specified level."""
    logger.remove()
    level = level.upper()
    accepted_levels = ["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    if level in accepted_levels:
        logger.add(sys.stderr, level=level)
        return level
    else:
        logger.add(sys.stderr, level="WARNING")
        logger.warning("Command line log level (-l) invalid. Defaulting to WARNING")
        return "WARNING"


def run_project(
    projectfile: str,
    datafiles: Optional[List[str]],
    outputfile: Optional[str],
    num_threads: int = 0,
) -> project.Project:
    """Create, process and save a project."""

    # Auto-detect thread count when num_threads is 0
    if num_threads == 0:
        try:
            # Get number of logical processors
            logical_cores = os.cpu_count()

            # Fallback if cpu_count() returns None
            if logical_cores is None:
                logger.warning("os.cpu_count() returned None; defaulting to 1 thread.")
                logical_cores = 1

            # Compute 75% of available CPUs
            calculated_threads = max(1, int(logical_cores * 0.75))

            # Sanity check: ensure calculated_threads is not greater than logical_cores
            if calculated_threads > logical_cores:
                logger.warning(
                    f"Calculated threads ({calculated_threads}) exceeded logical cores ({logical_cores}); "
                    f"resetting to {logical_cores}."
                )
                calculated_threads = logical_cores

            num_threads = calculated_threads
            logger.info(
                f"Thread count set automatically to {num_threads} "
                f"(75% of {logical_cores} logical processors)."
            )

        except Exception as e:
            # In case something unexpected happens during detection
            logger.error(f"Failed to compute CPU-based thread count: {e}")
            logger.warning("Defaulting to 1 thread.")
            num_threads = 1

    # Initialize and run project
    p = project.Project(projectfile, datafiles, outputfile)
    p.processDatafiles(numThreads=num_threads)
    p.saveResults()
    return p


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application."""
    try:
        parsed_args = parse_arguments(args)
        setup_logging(parsed_args.warninglevel)
        run_project(
            parsed_args.projectfile, parsed_args.datafiles, parsed_args.outputfile
        )
        return 0
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return 1


def pydre():
    sys.exit(main())


if __name__ == "__main__":
    pydre()
