import json
import sys
import polars as pl
import pathlib
from pathlib import Path
from loguru import logger
import jenkspy
from typing import Optional
import argparse

class Project:
    project_filename: Path  # used only for information
    definition: dict
    results: Optional[pl.DataFrame]

    def __init__(self, projectfilename: str):
        self.project_filename = pathlib.Path(projectfilename)
        self.definition = {}
        self.results = None
        try:
            with open(self.project_filename, "rb") as project_file:
                if self.project_filename.suffix == ".json":
                    try:
                        self.definition = json.load(project_file)
                    except json.decoder.JSONDecodeError as e:
                        logger.exception(
                            "Error parsing JSON in {}".format(self.project_filename),
                            exception=e,
                        )
                        sys.exit(1)
                else:
                    logger.error("Unsupported project file type")
                    raise
        except FileNotFoundError as e:
            logger.error(f"File '{projectfilename}' not found.")
            raise e

    def __load_single_datfile(self, filename: Path) -> pl.DataFrame:
        """Load a single .dat file (space delimited csv) into a Polars DataFrame."""
        try:
            df = pl.read_csv(
                filename,
                separator=" ",
                null_values=".",
                truncate_ragged_lines=True,
                infer_schema_length=5000,
            )
            logger.info(f"Loaded file: {filename}")
            return df
        except Exception as e:
            logger.error(f"Error loading file {filename}: {e}")
            raise

    def binarize_column(self, filename: Path, column_name: str):
        """Convert a column to binary using Jenks natural breaks."""
        df = self.__load_single_datfile(filename)

        if column_name not in df.columns:
            logger.error(f"Column {column_name} not found in {filename}")
            raise ValueError(f"Column {column_name} not found in the file.")

        values = df[column_name].to_list()

        # Determine optimal break points using Jenks Natural Breaks
        num_classes = 2  # Binary classification (on/off)
        breaks = jenkspy.jenks_breaks(values, num_classes)
        threshold = breaks[1]  # Get the first split value

        logger.info(f"Threshold determined by Jenks: {threshold}")

        # Create a binary column: 0 if above threshold, 1 if below
        df = df.with_columns(
            (df[column_name] < threshold).cast(pl.Int8()).alias(f"{column_name}_binary")
        )

        logger.info(f"Binarized column {column_name}")
        self.results = df

    def saveResults(self, outfilename: pathlib.Path):
        """
        Save results to a file, including only the 'HeadPitch' and 'HeadPitch_binary' columns.

        Args:
            outfilename: filename to output csv data to.
        """
        if self.results is None or self.results.is_empty():
            logger.error("Results not computed yet. Cannot save file.")
            return

        try:
            # Print available columns for debugging
            logger.info(f"Available columns: {self.results.columns}")

            # Ensure correct column casing
            if "HeadPitch" in self.results.columns:
                columns_to_save = ["HeadPitch", "HeadPitch_binary"]
            elif "headPitch" in self.results.columns:
                columns_to_save = ["headPitch", "headPitch_binary"]
            else:
                logger.error("HeadPitch column not found in data.")
                raise ValueError("Column 'HeadPitch' not found in the data.")

            # Select only the required columns
            selected_df = self.results.select(columns_to_save)

            # Save the selected columns with proper CSV formatting
            selected_df.write_csv(outfilename, separator=",")

            logger.info(f"Results successfully saved to {outfilename}")
        except Exception as e:
            logger.error(f"Error saving results to {outfilename}: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Pydre Data Processing")
    parser.add_argument("-p", "--project", required=True, help="Path to project file")
    parser.add_argument("-d", "--data", required=True, help="Path to data file")
    parser.add_argument("-o", "--output", required=True, help="Path to output file")

    args = parser.parse_args()

    try:
        # Load project from the provided JSON file
        project = Project(args.project)

        # Process the provided .dat file using the correct column name
        project.binarize_column(Path(args.data), "HeadPitch")

        # Save processed results to the specified output file
        project.saveResults(Path(args.output))

        print(f"Processing complete. Results saved to {args.output}")
    except Exception as e:
        logger.critical(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
