import os
# Singleton
class GlobalSettings:
    _instance = None

    # AWS 関係
    AWS_REGION = "ap-northeast-1"
    S3_PRICING_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    S3_PRICING_SUBDIR_PATH = "pricing/"
    # AWS SSM関連
    SSM_AUTH_PRM_KEY = "/mbs-new-pricing/auth/bigquery"

    # BiqQuery 関係
    BQ_PROJECT_ID = "raksul-429806"
    BQ_DATASET_ID = "lake_competitor"
    DEBUG_S3_NO_STREAM = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalSettings, cls).__new__(cls)
            for key, value in kwargs.items():
                setattr(cls._instance, key, value)

        return cls._instance
