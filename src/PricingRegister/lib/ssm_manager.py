import json
import boto3
from typing import Dict
from global_settings import GlobalSettings


class Ssm:
    settings: GlobalSettings
    credentials: Dict

    def __init__(self, settings: GlobalSettings, credentials: Dict = {}) -> None:
        self.ssm = boto3.client("ssm", region_name=settings.AWS_REGION)
        self.credentials: Dict = credentials
        self.settings: GlobalSettings = settings

    def get_cred(self) -> Dict:
        if len(self.credentials) != 0:
            return self.credentials
        else:
            response = self.ssm.get_parameter(
                Name=self.settings.SSM_AUTH_PRM_KEY, WithDecryption=False
            )
            return json.loads(response["Parameter"]["Value"], strict=False)
