import sys
import json
import boto3

sys.path.append('../')
import global_settings

class Ssm:
        
    credentials:dict
        
    def __init__(self, credentials:dict={}):
        self.ssm = boto3.client('ssm', region_name='ap-northeast-1')
        self.credentials = credentials
    
    def get_cred(self):
        if len(self.credentials) == 0:
            response = self.ssm.get_parameter(
                Name=global_settings.SSM_AUTH_PRM_KEY,
                WithDecryption=False
            )        
            return json.loads(response['Parameter']['Value'], strict=False)
        else:
            return self.credentials
