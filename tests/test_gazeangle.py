import polars as pl
import numpy as np

path = r"C:\Users\spark\Downloads\AMS1_testdat\Experimenter_51_Test_1747251071.dat"

df = pl.read_csv(path, separator=" ", has_header=True, infer_schema_length=0)

print("Detected gaze-related columns:", [c for c in df.columns if "GAZE" in c])

df = df.with_columns([
    pl.col("GAZE_HEADING").cast(pl.Float64),
    pl.col("GAZE_PITCH").cast(pl.Float64)
])

df = df.with_columns(
    (pl.col("GAZE_HEADING") ** 2 + pl.col("GAZE_PITCH") ** 2).sqrt().alias("gaze_angle")
)

stats = df.select([
    pl.col("GAZE_HEADING").mean().alias("mean_heading"),
    pl.col("GAZE_HEADING").std().alias("std_heading"),
    pl.col("GAZE_PITCH").mean().alias("mean_pitch"),
    pl.col("GAZE_PITCH").std().alias("std_pitch"),
    pl.col("gaze_angle").mean().alias("mean_angle"),
    pl.col("gaze_angle").max().alias("max_angle"),
])
print(stats)
