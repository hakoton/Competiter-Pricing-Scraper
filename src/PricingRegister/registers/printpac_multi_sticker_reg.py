import json
from typing import Dict
from global_settings import GlobalSettings
from lib import bq_manager
from lib.sns_manager import NotificationCenter
from shared.constants import ProductCategory

from .utils import register_to_bigquery_table


def doRegist(data: bytes, settings=GlobalSettings()) -> bool:
    BIGQUERY_TABLE: str = "printpac_multi_sticker_prices"

    converted_data: Dict = {} if data == None else json.loads(data.decode("utf-8"))
    if len(converted_data) == 0:
        return False

    pricing_query: bq_manager.PricingQuery = bq_manager.PricingQuery(settings)
    bq_full_name: str = pricing_query.get_qualified_fullname(BIGQUERY_TABLE)
    slack_noti: NotificationCenter = NotificationCenter(settings)

    register_to_bigquery_table(
        pricing_query,
        slack_noti,
        bq_full_name,
        ProductCategory.MULTI_STICKER,
        converted_data,
    )
    print(f"[{BIGQUERY_TABLE.split('.')[-1]}] registration completed")

    return True
