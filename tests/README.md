## SPEKE Reference Server Test Cases

This page documents test cases for the Lambdas and API Gateway resources. Each test cases uses static data
to generate a predictable response that can be used to check the SPEKE Reference Server for correct operation.


## Automated Tests

### Lambdas

The program named `lamda_tests.py` uses the Python unittest module. This program will run without any external dependencies. Open this file and modify it for the deployment specifics of your environment. **These tests assume you have AWS API keys configured for your environment that have adequate permissions to invoke the client and server Lambda functions.** See https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#config-settings-and-precedence to understand where the AWS CLI and SDKs look for API keys.

```
# SET THESE THREE CONSTANTS TO MATCH YOUR CONFIGURATION

# API_HOST = "lz9w9a2g89.execute-api.us-east-1.amazonaws.com"
# DEPLOYED_REGION = "us-east-1"
# SERVER_FUNCTION_NAME = "eke-server-EkeServerLambdaFunction-S68R3HGE8GTC"
# CLIENT_FUNCTION_NAME = "eke-server-EkeClientLambdaFunction-1K248YEWPTU0U"

API_HOST = "f8aix0vkl5.execute-api.us-east-1.amazonaws.com"
DEPLOYED_REGION = "us-east-1"
SERVER_FUNCTION_NAME = "eke-server-EkeServerLambdaFunction-15LUYRV00U6MP"
CLIENT_FUNCTION_NAME = "eke-server-EkeClientLambdaFunction-OK9F7TPIWV3L"
```

Run the program with your Python interpreter.

```
$ python lambda_tests.py 

test_client (__main__.TestSPEKELambdas) ... /usr/local/Cellar/python3/3.6.4_2/Frameworks/Python.framework/Versions/3.6/lib/python3.6/unittest/case.py:605: ResourceWarning: unclosed <ssl.SSLSocket fd=6, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('10.91.172.166', 61214), raddr=('34.204.159.19', 443)>
  testMethod()
ok
test_server (__main__.TestSPEKELambdas) ... /usr/local/Cellar/python3/3.6.4_2/Frameworks/Python.framework/Versions/3.6/lib/python3.6/unittest/case.py:605: ResourceWarning: unclosed <ssl.SSLSocket fd=6, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('10.91.172.166', 61215), raddr=('34.204.159.19', 443)>
  testMethod()
ok

----------------------------------------------------------------------
Ran 2 tests in 1.265s

OK

```

You can ignore the ResourceWarning about the unclosed socket. Both tests will report **ok** if the server and client Lambdas are functioning properly. 

### API Gateway

The program named `api_gateway_tests.py` uses the Python unittest module. This program requires an external module called `aws-requests-auth` that is installed using the `pip` tool. This module provides a tool to create Version 4 Signing Process (Python) headers for the API Gateway request. The file named `requirements.txt` contains the needed dependencies for `pip`. Install the depenencies into a virtual environment using `virtualenv` or into your global Python environment.

```
pip install -r requirements.txt
```

Open `api_gateway_tests.py` and modify it for the deployment specifics of your environment. 

```
# UPDATE THIS CONSTANT TO MATCH YOUR CONFIGURATION

#API_HOST = "lz9w9a2g89.execute-api.us-east-1.amazonaws.com"
API_HOST = "f8aix0vkl5.execute-api.us-east-1.amazonaws.com"
```

**These tests assume you have AWS API keys configured for your environment that have adequate permissions to invoke the client and server API endpoints.**

```
$ python api_gateway_tests.py

test_client (__main__.TestSPEKEGateway) ... ok
test_server (__main__.TestSPEKEGateway) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.664s

OK
```

Both tests will report **ok** if the server and client APIs are functioning properly. 

## Manual Tests

### Lambdas

#### Server Test

1. Navigate to the AWS Lambda Console
2. Select the region deployed with the SPEKE Reference Server
3. Select the function that contains the name EkeServerLambdaFunction
4. Pull down the test events list at the top right
5. Choose Configure test events
6. Set the Saved Test Event name to ServerKeyRequest
7. Copy the following exactly into the text area for the event
```
{
  "resource": "/copyProtection",
  "path": "/copyProtection",
  "httpMethod": "POST",
  "headers": {
    "Accept": "*/*",
    "content-type": "application/xml",
    "Host": "lz9w9a2g89.execute-api.us-east-1.amazonaws.com"
  },
  "requestContext": {
    "path": "/EkeStage/copyProtection",
    "stage": "EkeStage",
    "resourcePath": "/copyProtection",
    "httpMethod": "POST"
  },
  "body": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48Y3BpeDpDUElYIGlkPSI1RTk5MTM3QS1CRDZDLTRFQ0MtQTI0RC1BM0VFMDRCNEUwMTEiIHhtbG5zOmNwaXg9InVybjpkYXNoaWY6b3JnOmNwaXgiIHhtbG5zOnBza2M9InVybjppZXRmOnBhcmFtczp4bWw6bnM6a2V5cHJvdjpwc2tjIiB4bWxuczpzcGVrZT0idXJuOmF3czphbWF6b246Y29tOnNwZWtlIj48Y3BpeDpDb250ZW50S2V5TGlzdD48Y3BpeDpDb250ZW50S2V5IGtpZD0iNmM1ZjUyMDYtN2Q5OC00ODA4LTg0ZDgtOTRmMTMyYzFlOWZlIj48L2NwaXg6Q29udGVudEtleT48L2NwaXg6Q29udGVudEtleUxpc3Q+PGNwaXg6RFJNU3lzdGVtTGlzdD48Y3BpeDpEUk1TeXN0ZW0ga2lkPSI2YzVmNTIwNi03ZDk4LTQ4MDgtODRkOC05NGYxMzJjMWU5ZmUiIHN5c3RlbUlkPSI4MTM3Njg0NC1mOTc2LTQ4MWUtYTg0ZS1jYzI1ZDM5YjBiMzMiPiAgICA8Y3BpeDpDb250ZW50UHJvdGVjdGlvbkRhdGEgLz4gICAgPHNwZWtlOktleUZvcm1hdCAvPiAgICA8c3Bla2U6S2V5Rm9ybWF0VmVyc2lvbnMgLz4gICAgPHNwZWtlOlByb3RlY3Rpb25IZWFkZXIgLz4gICAgPGNwaXg6UFNTSCAvPiAgICA8Y3BpeDpVUklFeHRYS2V5IC8+PC9jcGl4OkRSTVN5c3RlbT48L2NwaXg6RFJNU3lzdGVtTGlzdD48Y3BpeDpDb250ZW50S2V5UGVyaW9kTGlzdD48Y3BpeDpDb250ZW50S2V5UGVyaW9kIGlkPSJrZXlQZXJpb2RfZTY0MjQ4ZjYtZjMwNy00Yjk5LWFhNjctYjM1YTc4MjUzNjIyIiBpbmRleD0iMTE0MjUiLz48L2NwaXg6Q29udGVudEtleVBlcmlvZExpc3Q+PGNwaXg6Q29udGVudEtleVVzYWdlUnVsZUxpc3Q+PGNwaXg6Q29udGVudEtleVVzYWdlUnVsZSBraWQ9IjZjNWY1MjA2LTdkOTgtNDgwOC04NGQ4LTk0ZjEzMmMxZTlmZSI+PGNwaXg6S2V5UGVyaW9kRmlsdGVyIHBlcmlvZElkPSJrZXlQZXJpb2RfZTY0MjQ4ZjYtZjMwNy00Yjk5LWFhNjctYjM1YTc4MjUzNjIyIi8+PC9jcGl4OkNvbnRlbnRLZXlVc2FnZVJ1bGU+PC9jcGl4OkNvbnRlbnRLZXlVc2FnZVJ1bGVMaXN0PjwvY3BpeDpDUElYPg==",
  "isBase64Encoded": true
}
```
2. Select the ServerKeyRequest saved test event
3. Click the Test button
4. Expand the details of the execution result
5. Find and verify the following XML data in the Log output compartment (formatted for readability); this data includes the encoded encryption key value and the key ID (kid)
```
<cpix:ContentKey kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
    <cpix:Data>
        <pskc:Secret>
            <pskc:PlainValue>ALzP1aOTJvzfqg9I12k2Vw==</pskc:PlainValue>
        </pskc:Secret>
    </cpix:Data>
</cpix:ContentKey>
```

#### Client Test

1. Navigate to the AWS Lambda Console
2. Select the region deployed with the SPEKE Reference Server
3. Select the function that contains the name EkeClientLambdaFunction
4. Pull down the test events list at the top right
5. Choose Configure test events
6. Set the Saved Test Event name to ClientKeyRequest
7. Copy the following exactly into the text area for the event
```
{
    "resource": "/client/{content_id}/{kid}",
    "path": "/client/5E99137A-BD6C-4ECC-A24D-A3EE04B4E011/e2201617-57c2-4d9b-adc5-cd87b7c01944",
    "httpMethod": "GET",
    "headers": { "Accept": "*/*", "Host": "lz9w9a2g89.execute-api.us-east-1.amazonaws.com", "Referer": "https://cf98fa7b2ee4450e.mediapackage.us-east-1.amazonaws.com/out/v1/5b7bf83cb49a4671aa3d6d23ad2fcacf/index.m3u8", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4" },
    "pathParameters": { "content_id": "5E99137A-BD6C-4ECC-A24D-A3EE04B4E011", "kid": "e2201617-57c2-4d9b-adc5-cd87b7c01944" },
    "requestContext": { "path": "/EkeStage/client/5E99137A-BD6C-4ECC-A24D-A3EE04B4E011/e2201617-57c2-4d9b-adc5-cd87b7c01944", "protocol": "HTTP/1.1", "stage": "EkeStage", "resourcePath": "/client/{content_id}/{kid}", "httpMethod": "GET" },
    "body": "",
    "isBase64Encoded": false
}
```
2. Select the ClientKeyRequest saved test event
3. Click the Test button
4. Expand the details of the execution result
5. Find and verify the following XML data in the Log output compartment (formatted for readability); the body attribute contains the encoded descryption key value
```
{
  "isBase64Encoded": true,
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/octet-stream"
  },
  "body": "OnSBba01dYe3nJdx7AewUw=="
}
```


### API Gateway

#### Server Test

1. Navigate to the AWS API Gateway Console
2. Select the region deployed with the SPEKE Reference Server
3. Select the EkeRestAPI
4. Select the POST method on the /copyProtection resource
5. Click the Test link on the left side of the main compartment
6. Copy the following into the Headers compartment
```
Host:lz9w9a2g89.execute-api.us-east-1.amazonaws.com
```
7. Copy the following into the Request Body compartment
```
<?xml version="1.0" encoding="UTF-8"?>
<cpix:CPIX id="5E99137A-BD6C-4ECC-A24D-A3EE04B4E011" 
    xmlns:cpix="urn:dashif:org:cpix" 
    xmlns:pskc="urn:ietf:params:xml:ns:keyprov:pskc" 
    xmlns:speke="urn:aws:amazon:com:speke">
    <cpix:ContentKeyList>
        <cpix:ContentKey kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe"></cpix:ContentKey>
    </cpix:ContentKeyList>
    <cpix:DRMSystemList>
        <cpix:DRMSystem kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe" systemId="81376844-f976-481e-a84e-cc25d39b0b33">
            <cpix:ContentProtectionData />
            <speke:KeyFormat />
            <speke:KeyFormatVersions />
            <speke:ProtectionHeader />
            <cpix:PSSH />
            <cpix:URIExtXKey />
        </cpix:DRMSystem>
    </cpix:DRMSystemList>
    <cpix:ContentKeyPeriodList>
        <cpix:ContentKeyPeriod id="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622" index="11425"/>
    </cpix:ContentKeyPeriodList>
    <cpix:ContentKeyUsageRuleList>
        <cpix:ContentKeyUsageRule kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
            <cpix:KeyPeriodFilter periodId="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622"/>
        </cpix:ContentKeyUsageRule>
    </cpix:ContentKeyUsageRuleList>
</cpix:CPIX>
```
8. Click the Test button
9. Review the Response Body for the encoded key value
```
<cpix:ContentKey kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
    <cpix:Data>
        <pskc:Secret>
            <pskc:PlainValue>ALzP1aOTJvzfqg9I12k2Vw==</pskc:PlainValue>
        </pskc:Secret>
    </cpix:Data>
</cpix:ContentKey>
```


#### Client Test

1. Navigate to the AWS API Gateway Console
2. Select the region deployed with the SPEKE Reference Server
3. Select the EkeRestAPI
4. Select the GET method on the /client/{content_id}/{kid} resource
5. Click the Test link on the left side of the main compartment
6. Copy the following into the {content_id} compartment
```
5E99137A-BD6C-4ECC-A24D-A3EE04B4E011
```
7. Copy the following into the {kid} compartment
```
e2201617-57c2-4d9b-adc5-cd87b7c01944
```
8. Copy the following into the Headers compartment
```
Host:lz9w9a2g89.execute-api.us-east-1.amazonaws.com
```
9. Click the Test button
10. Review the execution result for the encoded key value
```
OnSBba01dYe3nJdx7AewUw==
```


[**Home**](README.md)