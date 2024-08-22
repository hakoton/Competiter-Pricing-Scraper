from crawler import (
    printpac_seals_crawler,
    printpac_stickers_crawler,
    printpac_multi_stickers_crawler,
    printpac_ondemand_envelopes_crawler
)
import os

COMMAND_PRM_NAME = "TARGET"
COMMAND_MAP: dict = {
    "crawl_seal_prices_printpac": printpac_seals_crawler,
    "crawl_sticker_prices_printpac": printpac_stickers_crawler,
    "crawl_multi_sticker_prices_printpac": printpac_multi_stickers_crawler,
    "crawl_ondemand_envelope_prices_printpac": printpac_ondemand_envelopes_crawler,
}

S3_PRICING_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_PRICING_SUBDIR_PATH = "pricing/"
