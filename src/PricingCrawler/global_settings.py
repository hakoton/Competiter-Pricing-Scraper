from crawler import printpac_seals_crawler


COMMAND_PRM_NAME = "TARGET"
COMMAND_MAP: dict = {"crawl_seal_prices_printpac": printpac_seals_crawler}

S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"
