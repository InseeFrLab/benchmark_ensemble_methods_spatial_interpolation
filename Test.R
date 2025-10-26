library(DBI)
library(duckdb)
library(dplyr)
library(glue)

conn_ddb <- DBI::dbConnect(duckdb::duckdb())

dbExecute(conn_ddb, "LOAD httpfs;")

dbExecute(
  conn_ddb,
  "
  CREATE OR REPLACE VIEW bdalti AS
  SELECT *
  FROM read_parquet('s3://oliviermeslin/BDALTI/BDALTI_parquet/**/*.parquet')
  "
)

bdalti <- tbl(conn_ddb, "bdalti")

