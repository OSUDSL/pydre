import polars as pl

output_df = pl.read_csv('R2D_reaction_fixed1.csv')
output_df = output_df.with_columns((pl.col("ROI") / 2 + 0.5).alias("EventId").cast(pl.Int64))
event_df = pl.read_csv('R2D_events.csv')
new_df = output_df.join(event_df, on=["Week", "ScenarioName", "EventId"], how='left')
new_df.write_csv('output.csv', separator=',')
