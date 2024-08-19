from time import sleep
from typing import Dict, List
from datetime import datetime
from google.cloud.bigquery.table import RowIterator
from lib import bq_manager
from google.cloud import bigquery

from lib.sns_manager import NotificationCenter
from registers.bigquery_schema import TABLE_SCHEMA
from shared.constants import ProductCategory
from shared.interfaces import PriceDiff


def _drop_temp_table(pricing_query: bq_manager.PricingQuery, temp_table: str) -> None:
    try:
        pricing_query.get_table(temp_table)
        pricing_query.drop_table(temp_table)
        print(f"Temporary table [{temp_table.split('.')[-1]}] deleted")
    except:
        print(f"Temporary table [{temp_table.split('.')[-1]}] doesn't exist. Skip.")


def _create_main_table(pricing_query: bq_manager.PricingQuery, main_table: str) -> bool:
    main_table_not_exist = True
    try:
        pricing_query.get_table(main_table)
        main_table_not_exist = False
        return main_table_not_exist
    except:
        print(f"Main table [{main_table.split('.')[-1]}] doesn't exist")

    try:
        main_table_not_exist = True
        pricing_query.create_table(main_table, TABLE_SCHEMA)
        print(f"Created table [{main_table.split('.')[-1]}]")
        return main_table_not_exist
    except Exception as e:
        print(f"Cannot create main table [{main_table}] - ", e)
        raise e


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


def _load_new_data_to_table(
    pricing_query: bq_manager.PricingQuery, table: str, data: Dict
) -> None:
    try:
        table_exists = False
        while not table_exists:
            try:
                pricing_query.get_table(table)
                table_exists = True
                print(f"Table [{table.split('.')[-1]}] is now available.")
            except:
                print(f"Table {table} not found. Waiting...")
                sleep(1)

        batch_size = 30 * 1000
        records: List = []
        for idx in data:
            records.append(data[idx])

        batches: List = [
            records[i : i + batch_size] for i in range(0, len(records), batch_size)
        ]

        for batch in batches:
            pricing_query.persist_from_jsonlist(table, batch)
            sleep(1)
            print(
                f"Loaded [{len(batch)}] records to temporary table [{table.split('.')[-1]}] "
            )
    except Exception as e:
        print("Failed to load data to temporary table: ", table)
        print(e)
        raise e


def _verify_data(pricing_query: bq_manager.PricingQuery, table, data_len: int) -> None:
    query: str = f"SELECT COUNT(*) as row_count FROM `{table}`"
    result: RowIterator = pricing_query.execute_query_wait(query)
    row_count: int = 0
    for row in result:
        row_count: int = row.row_count

    if row_count != data_len:
        raise ValueError("Row count verification failed")

    print(f"Row count verification OK on table [{table.split('.')[-1]}]")


def _notify_price_changed_items(
    pricing_query: bq_manager.PricingQuery,
    product_category: ProductCategory,
    slack_noti: NotificationCenter,
    bq_full_name: str,
    temp_table: str,
) -> None:
    try:
        price_diff: List[PriceDiff] = pricing_query.get_price_change(
            bq_full_name, temp_table
        )
        slack_noti.notify(product_category, price_diff)

    except Exception as e:
        raise RuntimeError(f"Failed to get/notify price change: {e}")


def _update_price_changed_items(
    pricing_query: bq_manager.PricingQuery,
    bq_full_name: str,
    temp_table: str,
) -> None:
    try:
        pricing_query.update_price_changed_items(bq_full_name, temp_table)
    except Exception as e:
        raise RuntimeError(f"Failed to update data to the main table: {e}")


def _verify_price_updated(
    pricing_query: bq_manager.PricingQuery,
    bq_full_name: str,
    temp_table: str,
) -> None:
    try:
        price_change: List = pricing_query.get_price_change(bq_full_name, temp_table)
        if len(price_change) > 0:
            raise RuntimeError(f"Price not updated for items: {price_change}")

    except Exception as e:
        raise e


def register_to_bigquery_table(
    pricing_query: bq_manager.PricingQuery,
    slack_noti: NotificationCenter,
    bq_full_name: str,
    product_category: ProductCategory,
    data: Dict,
) -> None:
    unique_suffix: str = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_table: str = bq_full_name + "_temp_" + unique_suffix

    try:
        main_table_not_exist_previously: bool = _create_main_table(
            pricing_query, bq_full_name
        )
        if main_table_not_exist_previously == True:
            print("Load data directly to main table")
            _load_new_data_to_table(pricing_query, bq_full_name, data)
            return
        else:
            _create_temp_table(pricing_query, bq_full_name, temp_table)
            _load_new_data_to_table(pricing_query, temp_table, data)
            _verify_data(pricing_query, temp_table, len(data))
            del data
            _notify_price_changed_items(
                pricing_query, product_category, slack_noti, bq_full_name, temp_table
            )
            _update_price_changed_items(pricing_query, bq_full_name, temp_table)
            _verify_price_updated(pricing_query, bq_full_name, temp_table)
            _drop_temp_table(pricing_query, temp_table)
    except Exception as e:
        # テンポラリテーブルの蓄積を防ぐため、何か問題が発生した場合はテンポラリテーブルを削除する。
        try:
            _drop_temp_table(pricing_query, temp_table)
        except Exception as drop_table_err:
            print(drop_table_err)

        raise e
