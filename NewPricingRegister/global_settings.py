from registers import ppac_seal_teikei_reg

# コマンドと実行するCrawlerの対応表
FILE_PREFIX_MAP:dict = {
 "printpack-seal-teikei" : ppac_seal_teikei_reg,   
}

# S3関連
S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"

# AWS SSM関連
SSM_KEY_BASE = '/mbs-new-pricing/prod'
SSM_AUTH_PRM_KEY = '/mbs-new-pricing/auth/bigquery'

# BiqQuery関係
BQ_PRODUCT_ID:str = "raksulcrm-dev"
BQ_DATASET_ID:str = "lake_competitor"

# slack
SLACK_WEBHOOK_URL:str = 'https://hooks.slack.com/services/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'

# local or vendor環境用のDebug Switch
DEBUG_S3_NO_STREAM = False  # ONにすると空のStreamがRegisterに渡る（データ取得や差分検出のみ検証したい時に）