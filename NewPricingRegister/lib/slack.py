import sys
import json
import os
import requests

sys.path.append('../')
import global_settings

def notify(text):
    """ Slackへメッセージ通知を行う
        Parameters
            text: 通知したいメッセージ
    """
    payload_json = json.dumps({'text': text})
    headers = {'Content-type': 'application/json'}
    requests.post(global_settings.SLACK_WEBHOOK_URL, data=payload_json, headers=headers)