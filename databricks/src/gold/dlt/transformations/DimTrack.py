import dlt

@dlt.table
def DimTrackStaging():
    df = spark.readStream.table("`spotify-catalog`.silver.dimtrack")
    return df

dlt.create_streaming_table(name="dimtrack")

from pyspark import pipelines as dp

dp.create_auto_cdc_flow(
  target = "dimtrack",
  source = "DimTrackStaging",
  keys = ["track_id"],
  sequence_by = "updated_at",
  ignore_null_updates = False,
  apply_as_deletes = None,
  apply_as_truncates = None,
  column_list = None,
  except_column_list = None,
  stored_as_scd_type = 2,
  track_history_column_list = None,
  track_history_except_column_list = None,
  name = None,
  once = False
)