import dlt
from pyspark.sql import functions as F

expectations = { "rule_1": "user_id is not null" }

@dlt.table
@dlt.expect_all_or_drop(expectations)
def DimUserStaging():
    df = spark.readStream.table("`spotify-catalog`.silver.dimuser")
    return df

dlt.create_streaming_table(
  name="dimuser",
  expect_all_or_drop=expectations
)

from pyspark import pipelines as dp

dp.create_auto_cdc_flow(
  target="dimuser",
  source="DimUserStaging",
  keys=["user_id"],
  sequence_by="updated_at",
  ignore_null_updates=False,
  apply_as_deletes=None,
  apply_as_truncates=None,
  column_list=None,
  except_column_list=None,
  stored_as_scd_type=2,
  track_history_column_list=None,
  track_history_except_column_list=None,
  name=None,
  once=False
)