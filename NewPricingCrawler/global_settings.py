from crawlers import ppac_seal_teikei

COMMAND_PRM_NAME = "TARGET"

"""
Crawlerを作成したら以下の設定ファイルに１行を追加してください。
（Importも忘れずに）
文字列のモジュール名 : 作成したCrawlerモジュール名
"""
COMMAND_MAP:dict = {
 "ppac_seal_teikei" : ppac_seal_teikei,   
}

# S3関連
S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"