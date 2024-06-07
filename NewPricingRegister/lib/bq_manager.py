import datetime
from datetime import datetime as dt
from google.cloud import bigquery
from google.oauth2 import service_account
from . import ssm_manager

import sys
sys.path.append('../')
import global_settings as gs


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

class pricing_query:

    ssm:ssm_manager.Ssm
    cli:bigquery.client.Client

    @staticmethod
    def get_qualified_fullname(table_name:str):
        return gs.BQ_PRODUCT_ID + "." + gs.BQ_DATASET_ID + "." + table_name

    def __init__(self, credentials:dict={}):
        """ SSMから認証情報を取得してBigQuery環境へ繋ぎこみを行う
            parameters
                credentials: 
                    Raksul環境以外で疎通したい場合はここに直接認証情報のJsonオブジェクトを入れてください
                    こちらで指定した認証先への接続を優先して接続を行います
        """
        self.ssm = ssm_manager.Ssm(credentials)
        self.__connect()

    def __connect(self):
        c = service_account.Credentials.from_service_account_info(self.ssm.get_cred())
        c = c.with_scopes(['https://www.googleapis.com/auth/bigquery'])
        self.cli = bigquery.Client(credentials=c, project=gs.BQ_PRODUCT_ID)

    def persist_from_jsonlist(self, target_name:str, rows:list):
        """ JsonからBigQueryにデータを登録する
            Parameters:
                target_name     : [プロジェクト名].[データセット名].[テーブル名]
                rows            : List<Json(dict)>形式
        """
        err = self.cli.insert_rows_json(target_name,rows)
        if err == []:
            return True
        else:
            print("BigQuery Persist Error {}".format(err))
            return False

    def get_day_diff(self, target_name:str, concat_cols:str, partition_key:str, date_key:str, price_key:str, old_price_col_name:str, target_date:str)->bigquery.table.RowIterator:
        """ 指定された情報に従い前日価格カラムを追加して返す
            Parameters:
                target_name     : [プロジェクト名].[データセット名].[テーブル名]
                concat_cols     : 取得したい情報を１列にまとめて定義　⇒ 例：CONCAT(shape, '-' , unit, '-', eigyo) AS item_name
                partition_key   : 商品を一意に識別できる列名
                date_key        : 取得日を判定できる列名
                price_key       : 価格が格納されている列名
                old_price_col_name : 旧価格が格納される列名を指定（結果セットで返ってくる）
                target_date     : 取得基準日（この日のデータを前日価格が入って返却される）
        """
        d:date = dt.strptime(target_date, '%Y-%m-%d')
        d = d + datetime.timedelta(days=-1)
        target_prev_date:str = d.strftime('%Y-%m-%d')
        query:str = DIFF_QUERY \
            .replace('{partition_key}', partition_key) \
            .replace('{concat_columns}', concat_cols) \
            .replace('{date_key}', date_key) \
            .replace('{price}', price_key) \
            .replace('{prev_price}', old_price_col_name)  \
            .replace('{prev_date}', "'" + target_prev_date + "'")  \
            .replace('{target_date}', "'" + target_date + "'")  \
            .replace('{full_data_name}', "`" + target_name + "`")
        
        return self.cli.query_and_wait(query)
        
    def execute_qyery_wait(self, query:str): self.cli.query_and_wait(query)