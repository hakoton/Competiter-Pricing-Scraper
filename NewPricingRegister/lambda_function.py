import json
import urllib.parse
import boto3
import global_settings as gs


s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    # S3 Put eventから通知が来るため、対象のファイル名を取得
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    fname:str = key.split('/')[-1]
    target:str = fname.split('_')[0]

    try:
        # ファイル名からInvoke先を特定し、ストリームを渡す
        if gs.DEBUG_S3_NO_STREAM:
            gs.FILE_PREFIX_MAP[target].doRegist(None)
        else:
            response = s3.get_object(Bucket=bucket, Key=key)
            gs.FILE_PREFIX_MAP[target].doRegist(response["Body"].read())
        return f"Pricing Register : {key} Succeed!";
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
