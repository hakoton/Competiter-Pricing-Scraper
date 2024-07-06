import json
from time import sleep
from typing import Dict, List
from datetime import datetime
from google.cloud.bigquery.table import RowIterator
from global_settings import GlobalSettings
from lib import bq_manager
from google.cloud import bigquery
import math
from sys import getsizeof


def _delete_old_data(pricing_query: bq_manager.PricingQuery, table: str) -> None:
    try:
        pricing_query.execute_query_wait(f"DELETE FROM `{table}` where 1=1")
        print(f"Deleted old data in table [{table.split('.')[-1]}]")
    except Exception as e:
        print(f"Failed to delete old data in table[{table.split('.')[-1]}]")
        print(e)
        raise e


def _drop_temp_table(pricing_query: bq_manager.PricingQuery, temp_table: str) -> None:
    try:
        pricing_query.get_table(temp_table)
        pricing_query.drop_table(temp_table)
        print(f"Temporary table [{temp_table.split('.')[-1]}] deleted")
    except:
        print(f"Temporary table [{temp_table.split('.')[-1]}] doesn't exist. Skip.")


def _create_temp_table(
    pricing_query: bq_manager.PricingQuery, main_table: str, temp_table: str
) -> None:
    try:
        pricing_query.get_table(temp_table)
        return
    except:
        print(f"Temporary table [{temp_table.split('.')[-1]}] doesn't exist")

    try:
        # Get the schema from the source table
        source_table: bigquery.Table = pricing_query.get_table(main_table)
        schema: List[bigquery.SchemaField] = source_table.schema

        # Create the temporary table with the same schema
        pricing_query.create_table(temp_table, schema)
        print(f"Created table [{temp_table.split('.')[-1]}]")
        sleep(3)

    except Exception as e:
        print("Failed to create temporary table: ", temp_table)
        print(e)
        raise e


def _load_new_data_to_temp_table(
    pricing_query: bq_manager.PricingQuery, temp_table: str, data: Dict
) -> None:
    table_exists = False
    while not table_exists:
        try:
            pricing_query.get_table(temp_table)
            table_exists = True
            print(f"Table [{temp_table.split('.')[-1]}] is now available.")
        except:
            print(f"Table {temp_table} not found. Waiting...")
            sleep(1)

    batch_size = 30 * 1000
    records: List = []
    for idx in data:
        records.append(data[idx])

    batches: List = [
        records[i : i + batch_size] for i in range(0, len(records), batch_size)
    ]

    for batch in batches:
        pricing_query.persist_from_jsonlist(temp_table, batch)
        sleep(1)
        print(
            f"Loaded [{len(batch)}] records to temporary table [{temp_table.split('.')[-1]}] "
        )


def _verify_data(pricing_query: bq_manager.PricingQuery, table, data_len: int) -> None:
    query: str = f"SELECT COUNT(*) as row_count FROM `{table}`"
    result: RowIterator = pricing_query.execute_query_wait(query)
    row_count: int = 0
    for row in result:
        row_count: int = row.row_count

    if row_count != data_len:
        raise ValueError("Row count verification failed")

    print(f"Row count verification OK on table [{table.split('.')[-1]}]")


def _copy_data_to_main_table(
    pricing_query: bq_manager.PricingQuery,
    bq_full_name: str,
    temp_table: str,
) -> None:
    try:
        query: str = f"""
        INSERT INTO `{bq_full_name}`
        SELECT * FROM `{temp_table}`
        """
        pricing_query.execute_query_wait(query)
        print(f"Copied data to [{bq_full_name.split('.')[-1]}].")
    except Exception as e:
        raise RuntimeError(f"Failed to copy data to the main table: {e}")


def _register_to_bigquery_table(
    pricing_query: bq_manager.PricingQuery, bq_full_name: str, data: Dict
) -> None:
    unique_suffix: str = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_table: str = bq_full_name + "_temp_" + unique_suffix

    try:
        _create_temp_table(pricing_query, bq_full_name, temp_table)
        _load_new_data_to_temp_table(pricing_query, temp_table, data)
        _verify_data(pricing_query, temp_table, len(data))
        _delete_old_data(pricing_query, bq_full_name)
        _copy_data_to_main_table(pricing_query, bq_full_name, temp_table)
        _drop_temp_table(pricing_query, temp_table)
        _verify_data(pricing_query, bq_full_name, len(data))
    except Exception as e:
        # テンポラリテーブルの蓄積を防ぐため、何か問題が発生した場合はテンポラリテーブルを削除する。
        _drop_temp_table(pricing_query, temp_table)
        raise e


def doRegist(data: bytes, settings=GlobalSettings()) -> bool:
    BIGQUERY_TABLE: str = "printpac_seal_prices"

    converted_data: Dict = {} if data == None else json.loads(data.decode("utf-8"))
    if len(converted_data) == 0:
        return False

    pricing_query: bq_manager.PricingQuery = bq_manager.PricingQuery(settings)
    bq_full_name: str = pricing_query.get_qualified_fullname(BIGQUERY_TABLE)

    _register_to_bigquery_table(pricing_query, bq_full_name, converted_data)
    print(f"[{BIGQUERY_TABLE.split('.')[-1]}] registration completed")

    return True
