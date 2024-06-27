import json
import boto3


def put_s3(output_data, bucket, key):
    s3 = boto3.client("s3")

    res = s3.put_object(
        Body=json.dumps(output_data, indent=4, ensure_ascii=False).encode("utf-8"),
        Bucket=bucket,
        Key=key,
    )
    print("[Upload Result] ", res)
