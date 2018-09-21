#!/usr/bin/env python

# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/

import base64
import boto3
import json
import logging
import unittest
import time
from contextlib import closing
import xml.etree.ElementTree as ET

# SET THESE THREE CONSTANTS TO MATCH YOUR CONFIGURATION

# API_HOST = "lz9w9a2g89.execute-api.us-east-1.amazonaws.com"
# DEPLOYED_REGION = "us-east-1"
# SERVER_FUNCTION_NAME = "eke-server-EkeServerLambdaFunction-S68R3HGE8GTC"
# CLIENT_FUNCTION_NAME = "eke-server-EkeClientLambdaFunction-1K248YEWPTU0U"

API_HOST = "f8aix0vkl5.execute-api.us-east-1.amazonaws.com"
DEPLOYED_REGION = "us-east-1"
SERVER_FUNCTION_NAME = "eke-server-EkeServerLambdaFunction-15LUYRV00U6MP"
CLIENT_FUNCTION_NAME = "eke-server-EkeClientLambdaFunction-OK9F7TPIWV3L"

# static server test data -- no changes needed
SERVER_FUNCTION_PAYLOAD = {
    "resource": "/copyProtection",
    "path": "/copyProtection",
    "httpMethod": "POST",
    "headers": {
            "Accept": "*/*",
            "content-type": "application/xml",
            "Host": API_HOST
    },
    "requestContext": {
        "path": "/EkeStage/copyProtection",
        "stage": "EkeStage",
        "resourcePath": "/copyProtection",
        "httpMethod": "POST"
    },
    "body": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48Y3BpeDpDUElYIGlkPSI1RTk5MTM3QS1CRDZDLTRFQ0MtQTI0RC1BM0VFMDRCNEUwMTEiIHhtbG5zOmNwaXg9InVybjpkYXNoaWY6b3JnOmNwaXgiIHhtbG5zOnBza2M9InVybjppZXRmOnBhcmFtczp4bWw6bnM6a2V5cHJvdjpwc2tjIiB4bWxuczpzcGVrZT0idXJuOmF3czphbWF6b246Y29tOnNwZWtlIj48Y3BpeDpDb250ZW50S2V5TGlzdD48Y3BpeDpDb250ZW50S2V5IGtpZD0iNmM1ZjUyMDYtN2Q5OC00ODA4LTg0ZDgtOTRmMTMyYzFlOWZlIj48L2NwaXg6Q29udGVudEtleT48L2NwaXg6Q29udGVudEtleUxpc3Q+PGNwaXg6RFJNU3lzdGVtTGlzdD48Y3BpeDpEUk1TeXN0ZW0ga2lkPSI2YzVmNTIwNi03ZDk4LTQ4MDgtODRkOC05NGYxMzJjMWU5ZmUiIHN5c3RlbUlkPSI4MTM3Njg0NC1mOTc2LTQ4MWUtYTg0ZS1jYzI1ZDM5YjBiMzMiPiAgICA8Y3BpeDpDb250ZW50UHJvdGVjdGlvbkRhdGEgLz4gICAgPHNwZWtlOktleUZvcm1hdCAvPiAgICA8c3Bla2U6S2V5Rm9ybWF0VmVyc2lvbnMgLz4gICAgPHNwZWtlOlByb3RlY3Rpb25IZWFkZXIgLz4gICAgPGNwaXg6UFNTSCAvPiAgICA8Y3BpeDpVUklFeHRYS2V5IC8+PC9jcGl4OkRSTVN5c3RlbT48L2NwaXg6RFJNU3lzdGVtTGlzdD48Y3BpeDpDb250ZW50S2V5UGVyaW9kTGlzdD48Y3BpeDpDb250ZW50S2V5UGVyaW9kIGlkPSJrZXlQZXJpb2RfZTY0MjQ4ZjYtZjMwNy00Yjk5LWFhNjctYjM1YTc4MjUzNjIyIiBpbmRleD0iMTE0MjUiLz48L2NwaXg6Q29udGVudEtleVBlcmlvZExpc3Q+PGNwaXg6Q29udGVudEtleVVzYWdlUnVsZUxpc3Q+PGNwaXg6Q29udGVudEtleVVzYWdlUnVsZSBraWQ9IjZjNWY1MjA2LTdkOTgtNDgwOC04NGQ4LTk0ZjEzMmMxZTlmZSI+PGNwaXg6S2V5UGVyaW9kRmlsdGVyIHBlcmlvZElkPSJrZXlQZXJpb2RfZTY0MjQ4ZjYtZjMwNy00Yjk5LWFhNjctYjM1YTc4MjUzNjIyIi8+PC9jcGl4OkNvbnRlbnRLZXlVc2FnZVJ1bGU+PC9jcGl4OkNvbnRlbnRLZXlVc2FnZVJ1bGVMaXN0PjwvY3BpeDpDUElYPg==",
    "isBase64Encoded": True
}

# static client test data -- no changes needed
CLIENT_FUNCTION_PAYLOAD = {
    "resource": "/client/{content_id}/{kid}",
    "path": "/client/5E99137A-BD6C-4ECC-A24D-A3EE04B4E011/e2201617-57c2-4d9b-adc5-cd87b7c01944",
    "httpMethod": "GET",
    "headers": {
        "Accept": "*/*",
        "Host": API_HOST,
        "Referer": "https://cf98fa7b2ee4450e.mediapackage.us-east-1.amazonaws.com/out/v1/5b7bf83cb49a4671aa3d6d23ad2fcacf/index.m3u8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4"
    },
    "pathParameters": {
        "content_id": "5E99137A-BD6C-4ECC-A24D-A3EE04B4E011",
        "kid": "e2201617-57c2-4d9b-adc5-cd87b7c01944"
    },
    "requestContext": {
        "path": "/EkeStage/client/5E99137A-BD6C-4ECC-A24D-A3EE04B4E011/e2201617-57c2-4d9b-adc5-cd87b7c01944",
        "protocol": "HTTP/1.1",
        "stage": "EkeStage",
        "resourcePath": "/client/{content_id}/{kid}",
        "httpMethod": "GET"
    },
    "body": "",
    "isBase64Encoded": False
}

# keys expected from above test data
EXPECTED_SERVER_KEY = b'\x00\xbc\xcf\xd5\xa3\x93&\xfc\xdf\xaa\x0fH\xd7i6W'
EXPECTED_CLIENT_KEY = b':t\x81m\xad5u\x87\xb7\x9c\x97q\xec\x07\xb0S'


class TestSPEKELambdas(unittest.TestCase):

    def test_server(self):
        client = boto3.client('lambda', region_name=DEPLOYED_REGION)
        response = client.invoke(
            FunctionName=SERVER_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(SERVER_FUNCTION_PAYLOAD),
        )
        # get the json-encoded payload
        stream = response["Payload"]
        decoded = json.loads(stream.read())
        stream.close()
        # get the XML embedded inside
        root_element = ET.fromstring(decoded["body"])
        # get the key element
        key = root_element.find(
            ".//{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue")
        # test the key against expected
        self.assertEqual(EXPECTED_SERVER_KEY, base64.b64decode(key.text))

    def test_client(self):
        client = boto3.client('lambda', region_name=DEPLOYED_REGION)
        response = client.invoke(
            FunctionName=CLIENT_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(CLIENT_FUNCTION_PAYLOAD),
        )
        # get the json-encoded payload
        stream = response["Payload"]
        decoded = json.loads(stream.read())
        stream.close()
        # get the key
        key = decoded["body"]
        # test the key against expected
        self.assertEqual(EXPECTED_CLIENT_KEY, base64.b64decode(key))


if __name__ == '__main__':
    unittest.main(verbosity=2)
