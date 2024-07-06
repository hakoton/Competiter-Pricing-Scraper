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
