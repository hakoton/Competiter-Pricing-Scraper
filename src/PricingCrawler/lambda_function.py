import json
import global_settings as gs

"""
event: Dict[str,str] = {
    "TARGET": "<コマンド名>"
}
例:
lambda_handler({ "TARGET": "crawl_seal_prices_printpac" },{})
"""


def lambda_handler(event, context):
    prm = event[gs.COMMAND_PRM_NAME]
    if not gs.COMMAND_MAP[prm].doCrawl(
        gs.S3_PRICING_BUCKET_NAME, gs.S3_PRICING_SUBDIR_PATH
    ):
        print(f"{event[gs.COMMAND_PRM_NAME]} crawler failed.")

    return {
        "statusCode": 200,
        "body": json.dumps(f"{event[gs.COMMAND_PRM_NAME]} has done."),
    }
