import urllib.parse
import boto3
from typing import Dict
from global_settings import GlobalSettings
import handler_mapping


def lambda_handler(event: Dict, context):
    """
    S3 イベント:
    {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": str
                    }
                    "object": {
                        "key": str
                    }
                }
            }
         ]
    }
    """

    # S3 Put eventから通知が来るため、対象のファイル名を取得
    settings: GlobalSettings = GlobalSettings()
    s3 = boto3.client("s3")
    bucket: str = event["Records"][0]["s3"]["bucket"]["name"]

    # 例:
    # key    = pricing/printpac-label-seal_2024-06-23-00-22-25.json
    # fname  = printpac-label-seal_2024-06-23-00-22-25.json
    # target = printpac-label-seal
    key: str = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    fname: str = key.split("/")[-1]
    target: str = fname.split("_")[0]

    try:
        # ファイル名からInvoke先を特定し、ストリームを渡す
        print("Getting data...")
        if settings.DEBUG_S3_NO_STREAM:
            handler_mapping.FILE_PREFIX_MAP[target].doRegist(None)
        else:
            print("Bucket: ", bucket)
            print("Key: ", key)
            response = s3.get_object(Bucket=bucket, Key=key)
            handler_mapping.FILE_PREFIX_MAP[target].doRegist(response["Body"].read())
        return f"Pricing Register : {key} Succeed!"

    except Exception as e:
        print(e)
        raise e
