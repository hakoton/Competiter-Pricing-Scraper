from typing import List
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
from google.oauth2 import service_account
from . import ssm_manager
from global_settings import GlobalSettings


# 差分抽出クエリ
DIFF_QUERY = """
  SELECT * FROM
  (
    SELECT
      {partition_key},
      {concat_columns},
      {date_key},
      {price},
      LAG({price}, 1) OVER (PARTITION BY {partition_key} ORDER BY {date_key}) AS {prev_price}
    FROM
      {full_data_name}
    WHERE
      {date_key} BETWEEN {prev_date} AND {target_date}
  ) WHERE {date_key} = {target_date}
"""


class PricingQuery:
    ssm: ssm_manager.Ssm
    cli: bigquery.Client
    gs: GlobalSettings

    def __init__(self, settings: GlobalSettings, credentials: dict = {}) -> None:
        """AWS SSMから認証情報を取得してBigQuery環境へ繋ぎこみを行う
        parameters
            credentials:
                Raksul環境以外で疎通したい場合はここに直接認証情報のJsonオブジェクトを入れてください
                こちらで指定した認証先への接続を優先して接続を行います
        """
        self.ssm: ssm_manager.Ssm = ssm_manager.Ssm(settings, credentials)
        self.settings: GlobalSettings = settings
        self.__connect()

    def __connect(self) -> None:
        creds: service_account.Credentials = (
            service_account.Credentials.from_service_account_info(
                self.ssm.get_cred()
            ).with_scopes(["https://www.googleapis.com/auth/bigquery"])
        )

        self.cli: bigquery.Client = bigquery.Client(
            credentials=creds, project=self.settings.BQ_PROJECT_ID
        )

    def get_qualified_fullname(self, table_name: str) -> str:
        return (
            self.settings.BQ_PROJECT_ID
            + "."
            + self.settings.BQ_DATASET_ID
            + "."
            + table_name
        )

    def get_table(self, table_name: str) -> bigquery.Table:
        return self.cli.get_table(table_name)

    def create_table(self, table_name, schema) -> bigquery.Table:
        table: bigquery.Table = bigquery.Table(table_name, schema=schema)
        return self.cli.create_table(table)

    def drop_table(self, table_name) -> None:
        return self.cli.delete_table(table_name)

    def persist_from_jsonlist(self, target_name: str, rows: list) -> bool:
        err = self.cli.insert_rows_json(target_name, rows)
        if err == []:
            return True
        else:
            print("BigQuery Persist Error {}".format(err))
            return False

    def execute_query_wait(self, query: str) -> RowIterator:
        return self.cli.query_and_wait(query)

    # () => List[PriceDiff]
    def get_price_change(self, current_table_name: str, new_table_name: str) -> List:
        raw_query = """
        WITH old_data AS (
          SELECT 
            CONCAT(
              CAST(oid1 AS STRING), 
              '_', 
              CAST(oid2 AS STRING), 
              '_', 
              CAST(oid3 AS STRING), 
              '_', 
              CAST(shape AS STRING), 
              '_', 
              CAST(size AS STRING), 
              '_', 
              CAST(color AS STRING), 
              '_', 
              CAST(path AS STRING), 
              '_', 
              CAST(pid AS STRING), 
              '_', 
              CAST(day AS STRING), 
              '_', 
              CAST(`set` AS STRING)
            ) AS composite_key, 
            campaign_price as old_campaign_price, 
            Actual_price as old_actual_price, 
            List_price as old_list_price 
          FROM 
            `{current_table_name}`
        ), 
        new_data AS (
          SELECT 
            CONCAT(
              CAST(oid1 AS STRING), 
              '_', 
              CAST(oid2 AS STRING), 
              '_', 
              CAST(oid3 AS STRING), 
              '_', 
              CAST(shape AS STRING), 
              '_', 
              CAST(size AS STRING), 
              '_', 
              CAST(color AS STRING), 
              '_', 
              CAST(path AS STRING), 
              '_', 
              CAST(pid AS STRING), 
              '_', 
              CAST(day AS STRING), 
              '_', 
              CAST(`set` AS STRING)
            ) AS composite_key, 
            campaign_price AS new_campaign_price, 
            Actual_price as new_actual_price, 
            List_price as new_list_price 
          FROM 
            `{new_table_name}`
        ) 
        SELECT 
          old_data.composite_key AS composite_key,
          old_data.old_campaign_price,
          old_data.old_actual_price,
          old_data.old_list_price,
          new_data.new_campaign_price,
          new_data.new_actual_price,
          new_data.new_list_price
        FROM 
          old_data 
          JOIN new_data ON old_data.composite_key = new_data.composite_key 
        WHERE 
          (
            old_data.old_campaign_price != new_data.new_campaign_price 
            OR old_data.old_actual_price != new_data.new_actual_price 
            OR old_data.old_list_price != new_data.new_list_price
          )
        """

        query: str = raw_query.replace(
            "{current_table_name}", current_table_name
        ).replace("{new_table_name}", new_table_name)

        row_iterator = self.cli.query_and_wait(query)
        data = [dict(row) for row in row_iterator]
        return data

    def update_price_changed_items(self, current_table_name, new_table_name) -> None:
        raw_query: str = """
        UPDATE
          `{current_table_name}` AS target
        SET
          target.campaign_price = source.new_campaign_price,
          target.Actual_price = source.new_actual_price,
          target.List_price = source.new_list_price,
          target.start_date = source.start_date
        FROM
          (
            SELECT
              CONCAT(
                CAST(oid1 AS STRING),
                '_',
                CAST(oid2 AS STRING),
                '_',
                CAST(oid3 AS STRING),
                '_',
                CAST(shape AS STRING),
                '_',
                CAST(size AS STRING),
                '_',
                CAST(color AS STRING),
                '_',
                CAST(path AS STRING),
                '_',
                CAST(pid AS STRING),
                '_',
                CAST(day AS STRING),
                '_',
                CAST(`set` AS STRING)
              ) AS composite_key,
              campaign_price AS new_campaign_price,
              List_price as new_list_price,
              Actual_price as new_actual_price,
              start_date
            FROM
              `{new_table_name}`
          ) AS source
        WHERE
          CONCAT(
            CAST(target.oid1 AS STRING),
            '_',
            CAST(target.oid2 AS STRING),
            '_',
            CAST(target.oid3 AS STRING),
            '_',
            CAST(target.shape AS STRING),
            '_',
            CAST(target.size AS STRING),
            '_',
            CAST(target.color AS STRING),
            '_',
            CAST(target.path AS STRING),
            '_',
            CAST(target.pid AS STRING),
            '_',
            CAST(target.day AS STRING),
            '_',
            CAST(target.`set` AS STRING)
          ) = source.composite_key
          AND (
            target.campaign_price != source.new_campaign_price
            OR target.List_price != source.new_List_price
            OR target.Actual_price != source.new_Actual_price
          )
        """

        query: str = raw_query.replace(
            "{current_table_name}", current_table_name
        ).replace("{new_table_name}", new_table_name)
        self.cli.query_and_wait(query)
