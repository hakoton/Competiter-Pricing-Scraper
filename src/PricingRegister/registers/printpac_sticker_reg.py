import json
from typing import Dict
from global_settings import GlobalSettings
from lib import bq_manager

from .utils import register_to_bigquery_table


def doRegist(data: bytes, settings=GlobalSettings()) -> bool:
    BIGQUERY_TABLE: str = "printpac_sticker_prices"

    converted_data: Dict = {} if data == None else json.loads(data.decode("utf-8"))
    if len(converted_data) == 0:
        return False

    pricing_query: bq_manager.PricingQuery = bq_manager.PricingQuery(settings)
    bq_full_name: str = pricing_query.get_qualified_fullname(BIGQUERY_TABLE)

    register_to_bigquery_table(pricing_query, bq_full_name, converted_data)
    print(f"[{BIGQUERY_TABLE.split('.')[-1]}] registration completed")

    return True
