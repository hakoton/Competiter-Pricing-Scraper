from typing import List
from google.cloud import bigquery

TABLE_SCHEMA: List = [
    bigquery.SchemaField("yid", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("oid1", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("oid2", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("oid3", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("oid4", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("shape", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("size", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("color", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("path", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("is_variable", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("pid", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("weight", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("day", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("set", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("List_price", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("campaign_price", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("Actual_price", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("start_date", "DATE", mode="NULLABLE"),
]
