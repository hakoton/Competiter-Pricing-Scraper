from crawler import (
    printpac_seals_crawler,
    printpac_stickers_crawler,
    printpac_multi_stickers_crawler,
)


COMMAND_PRM_NAME = "TARGET"
COMMAND_MAP: dict = {
    "crawl_seal_prices_printpac": printpac_seals_crawler,
    "crawl_sticker_prices_printpac": printpac_stickers_crawler,
    "crawl_multi_sticker_prices_printpac": printpac_multi_stickers_crawler,
}

S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"
