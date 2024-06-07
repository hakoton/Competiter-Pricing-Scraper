import json
import global_settings as gs

def lambda_handler(event, context):
    """
        Crawler追加時にこのファイルを直す必要はない
    """

    # Invoke from event Parameter
    prm = event[gs.COMMAND_PRM_NAME]
    if not gs.COMMAND_MAP[prm].doCrawl(gs.S3_PRICING_BUCKET_NAME, gs.S3_PRICING_SUBDIR_PATH):
        print(f"{event["TARGET"]} crawler failed.")

    #FIXME: 適切なbody
    return {
        'statusCode': 200,
        'body': json.dumps(f"{event["TARGET"]} has done.")
    }
