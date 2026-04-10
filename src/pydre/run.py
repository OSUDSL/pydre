import inspect
import os
import tomllib
from loguru import logger
from . import project
from . import filters as filters_module
from . import metrics as metrics_module
import sys
import argparse
from pathlib import Path
from typing import List, Optional


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Set up argparse based parser."""
    parser = argparse.ArgumentParser(
        description="pydre: Driving simulation data processing engine"
    )
    parser.add_argument(
        "-p", "--projectfile", type=str, help="the project file path", default=None
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
        "--log-level",
        "--warninglevel",
        dest="warninglevel",
        type=str,
        default="WARNING",
        help="Logging level. DEBUG, INFO, WARNING, ERROR, and CRITICAL are allowed.",
    )
    parser.add_argument(
        "--list-metrics",
        action="store_true",
        default=False,
        help="List all available metrics and their parameters, then exit. "
             "Combine with -p to include custom metrics from a project file.",
    )
    parser.add_argument(
        "--list-filters",
        action="store_true",
        default=False,
        help="List all available filters and their parameters, then exit. "
             "Combine with -p to include custom filters from a project file.",
    )
    return parser.parse_args(args)


def _ensure_modules_loaded():
    """Import all metric and filter submodules so their @register decorators run."""
    import importlib
    import pkgutil
    for pkg, mod_name in (
        (filters_module, "filters"),
        (metrics_module, "metrics"),
    ):
        pkg_path = getattr(pkg, "__path__", [])
        pkg_prefix = f"pydre.{mod_name}."
        for _finder, name, _ispkg in pkgutil.iter_modules(pkg_path, prefix=pkg_prefix):
            importlib.import_module(name)


def _load_custom_from_project(project_file: str) -> None:
    """Parse the [config] block of a project TOML and load any custom metrics/filters dirs.

    Delegates the actual directory scanning and module loading to
    :meth:`~pydre.project.Project._load_custom_dir`, so the logic is not duplicated.
    """
    pf = Path(project_file)
    if not pf.exists():
        print(f"  [warning] Project file not found: {pf}")
        return

    try:
        with open(pf, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"  [warning] Could not parse project file: {e}")
        return

    config = data.get("config", {})
    project.Project._load_custom_dir(
        config.get("custom_metrics_dirs", []), pf.parent, "metrics"
    )
    project.Project._load_custom_dir(
        config.get("custom_filters_dirs", []), pf.parent, "filters"
    )


def _format_param(name: str, param: inspect.Parameter) -> str:
    """Format a single parameter for display."""
    if param.default is inspect.Parameter.empty:
        return name
    return f"{name}={param.default!r}"


def print_metrics(project_file: Optional[str] = None):
    """Print all registered metrics with their parameters to stdout.

    Args:
        project_file: Optional path to a project TOML. When provided, any custom
            metrics defined via ``custom_metrics_dirs`` in ``[config]`` are loaded
            and included in the listing.
    """
    _ensure_modules_loaded()
    if project_file is not None:
        print(f"  Loading custom functions from: {project_file}")
        _load_custom_from_project(project_file)
    from . import metrics as m
    if not m.metricsList:
        print("No metrics registered.")
        return
    sep = "-" * 60
    print(f"\n{sep}")
    print(f"  {'METRIC NAME':<30}  OUTPUT COLUMN(S)")
    print(sep)
    for name in sorted(m.metricsList):
        func = m.metricsList[name]
        col_names = m.metricsColNames.get(name, [name])
        sig = inspect.signature(func)
        params = [
            _format_param(pname, p)
            for pname, p in sig.parameters.items()
            if pname != "drivedata"
        ]
        col_display = ", ".join(col_names)
        param_display = ", ".join(params) if params else "(no extra parameters)"
        print(f"  {name:<30}  -> {col_display}")
        print(f"  {'':30}     params: {param_display}")
    print(f"{sep}\n")


def print_filters(project_file: Optional[str] = None):
    """Print all registered filters with their parameters to stdout.

    Args:
        project_file: Optional path to a project TOML. When provided, any custom
            filters defined via ``custom_filters_dirs`` in ``[config]`` are loaded
            and included in the listing.
    """
    _ensure_modules_loaded()
    if project_file is not None:
        print(f"  Loading custom functions from: {project_file}")
        _load_custom_from_project(project_file)
    from . import filters as f
    if not f.filtersList:
        print("No filters registered.")
        return
    sep = "-" * 60
    print(f"\n{sep}")
    print("  FILTER NAME")
    print(sep)
    for name in sorted(f.filtersList):
        func = f.filtersList[name]
        sig = inspect.signature(func)
        params = [
            _format_param(pname, p)
            for pname, p in sig.parameters.items()
            if pname != "drivedata"
        ]
        param_display = ", ".join(params) if params else "(no extra parameters)"
        print(f"  {name}")
        print(f"    params: {param_display}")
    print(f"{sep}\n")


def run_project(
    projectfile: str,
    datafiles: Optional[List[str]],
    outputfile: Optional[str],
    num_threads: int = 0,
    log_level: str = "WARNING",
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
    p = project.Project(projectfile, datafiles, outputfile, log_level=log_level)
    p.processDatafiles(numThreads=num_threads)
    p.saveResults()
    return p


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application."""
    try:
        parsed_args = parse_arguments(args)

        # Handle listing flags before requiring a project file
        if parsed_args.list_metrics:
            print_metrics(parsed_args.projectfile)
            return 0
        if parsed_args.list_filters:
            print_filters(parsed_args.projectfile)
            return 0

        if parsed_args.projectfile is None:
            print(
                "error: the following arguments are required: -p/--projectfile\n"
                "       (use --list-metrics or --list-filters to explore available options)"
            )
            return 1

        run_project(
            parsed_args.projectfile, parsed_args.datafiles, parsed_args.outputfile,
            log_level=parsed_args.warninglevel,
        )
        return 0
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return 1


def pydre():
    sys.exit(main())


if __name__ == "__main__":
    pydre()
