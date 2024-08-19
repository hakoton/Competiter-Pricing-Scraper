import json
import boto3
from typing import Dict
from global_settings import GlobalSettings


class Ssm:
    settings: GlobalSettings

    def __init__(self, settings: GlobalSettings) -> None:
        self.ssm = boto3.client("ssm", region_name=settings.AWS_REGION)
        self.settings: GlobalSettings = settings

    def get_bigquery_cred(self) -> Dict:
        response = self.ssm.get_parameter(
            Name=self.settings.BIGQUERY_AUTH_PRM_KEY, WithDecryption=False
        )
        return json.loads(response["Parameter"]["Value"], strict=False)

    def get_slack_cred(self) -> str:
        response = self.ssm.get_parameter(
            Name=self.settings.SLACK_WEBHOOK_PRM_KEY, WithDecryption=False
        )
        return response["Parameter"]["Value"]
