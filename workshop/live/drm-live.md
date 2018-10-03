# Module: Digital Rights Management (DRM) and Encryption

When working with videos for your service or Over the Top (OTT) platform, you will very likely need to secure and protect your live streams prior to delivering content to your end users. Approaches for securing content include basic content _encryption_ or by applying highly secure Digital Rights Management (DRM) to the content. Examples of DRM include Fairplay, Widevine and PlayReady.

In this module, you'll use AWS Elemental MediaPackage, to secure and encrypt your live channels. You'll learn about the Secure Packager and Encoder Key Exchange (SPEKE) API, deploy an AWS SPEKE reference server, and configure AWS Elemental MediaPackage to encrypt HLS  content using AES-128 encryption.

## Prerequisites
You'll need to have previously installed the Live Streaming Solution
<< LINK GOES HERE >>

You'll need to have previously deployed the AWS SPEKE Reference Server.<br/>
https://github.com/awslabs/speke-reference-server

Once you've installed the AWS SPEKE Reference Server retrieve the SPEKE API URL and MediaPackage Role from the output of your Cloudformation Stack Details. 

Goto CloudFormation-> Stacks -> **AWS SPEKE Reference Server Stack Name** -> Outputs
and make a  note of the below paramters

| Parameter | Example  |
|--------------------------|-------------------------------------------------------------------------------------------|
| SPEKEServerURL |``` https://{hostname}.execute-api.us-east-1.amazonaws.com/EkeStage/copyProtection ``` |
| MediaPackageSPEKERoleArn|``` arn:aws:iam::{AWS_ACCOUNT}:role/speke-reference-MediaPackageInvokeSPEKERole-{INSTANCE_ID} ``` |

Next, Goto CloudFormation -> **Live Streaming Solution Stack** -> Outouts and make a note of the parameters below.

| Parameter |  |
|--------------------------|-------------------------------------------------------------------------------------------|
| DemoConsole |``` https://{hostname}.execute-api.us-east-1.amazonaws.com/EkeStage/copyProtection ``` |
| CloudFrontHlsEnpoint |``` https://{hostname}.cloudfront.net/7b445d5fd31d447a8e233944747c7fb0/index.m3u8 ``` | 

**Make sure you replace the various values such as hostname, aws_account with your own deployment vaues**

## 1. Testing the SPEKE API...

### Lambdas

#### Server Test

1. Navigate to the AWS Lambda Console
1. Select the region deployed with the SPEKE Reference Server
1. Select the function that contains the name {STACKNAME}-SPEKEServerLambda-{}
1. Pull down the test events list at the top right
1. Choose Configure test events
1. Set the Saved Test Event name to **ServerKeyRequest**
1. Copy the following exactly into the text area for the event and replace the **hostname** with one from your SPEKEServerURL
```
{
  "resource": "/copyProtection",
  "path": "/copyProtection",
  "httpMethod": "POST",
  "headers": {
    "Accept": "*/*",
    "content-type": "application/xml",
    "Host": "hostname.execute-api.us-east-1.amazonaws.com"
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
8. Select the ServerKeyRequest saved test event
1. Click the Test button
1. Expand the details of the execution result
1. Find and verify the following XML data in the Log output compartment (formatted for readability); this data includes the encoded encryption key value and the key ID (kid)
```
<?xml version="1.0" encoding="UTF-8"?>
<cpix:CPIX xmlns:cpix="urn:dashif:org:cpix" xmlns:pskc="urn:ietf:params:xml:ns:keyprov:pskc" xmlns:speke="urn:aws:amazon:com:speke" id="5E99137A-BD6C-4ECC-A24D-A3EE04B4E011">
   <cpix:ContentKeyList>
      <cpix:ContentKey kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
         <cpix:Data>
            <pskc:Secret>
               <pskc:PlainValue>ALzP1aOTJvzfqg9I12k2Vw==</pskc:PlainValue>
            </pskc:Secret>
         </cpix:Data>
      </cpix:ContentKey>
   </cpix:ContentKeyList>
   <cpix:DRMSystemList>
      <cpix:DRMSystem kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe" systemId="81376844-f976-481e-a84e-cc25d39b0b33">
         <speke:KeyFormat />
         <speke:KeyFormatVersions />
         <cpix:URIExtXKey>aHR0cHM6Ly9kMnVod2Jqc3p1ejF2Ny5jbG91ZGZyb250Lm5ldC81RTk5MTM3QS1CRDZDLTRFQ0MtQTI0RC1BM0VFMDRCNEUwMTEvNmM1ZjUyMDYtN2Q5OC00ODA4LTg0ZDgtOTRmMTMyYzFlOWZl</cpix:URIExtXKey>
      </cpix:DRMSystem>
   </cpix:DRMSystemList>
   <cpix:ContentKeyPeriodList>
      <cpix:ContentKeyPeriod id="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622" index="11425" />
   </cpix:ContentKeyPeriodList>
   <cpix:ContentKeyUsageRuleList>
      <cpix:ContentKeyUsageRule kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
         <cpix:KeyPeriodFilter periodId="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622" />
      </cpix:ContentKeyUsageRule>
   </cpix:ContentKeyUsageRuleList>
</cpix:CPIX>
```
### API Gateway

#### Server Test

1. Navigate to the AWS API Gateway Console
1. Select the region deployed with the SPEKE Reference Server
1. Select the SPEKEReferenceAPI
1. Select the POST method on the /copyProtection resource
1. Click the Test link on the left side of the main compartment
1. Replace the **hostname** and copy the following into the Headers {copyProtection} compartment
```
Host:hostname.execute-api.us-west-2.amazonaws.com
```
1. Copy the following into the Request Body compartment
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
6. Click the Test button
1. Review the Response Body for the encoded key value
```
<cpix:CPIX xmlns:cpix="urn:dashif:org:cpix" xmlns:pskc="urn:ietf:params:xml:ns:keyprov:pskc" xmlns:speke="urn:aws:amazon:com:speke" id="5E99137A-BD6C-4ECC-A24D-A3EE04B4E011">
    <cpix:ContentKeyList>
        <cpix:ContentKey kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe"><cpix:Data><pskc:Secret><pskc:PlainValue>ALzP1aOTJvzfqg9I12k2Vw==</pskc:PlainValue></pskc:Secret></cpix:Data></cpix:ContentKey>
    </cpix:ContentKeyList>
    <cpix:DRMSystemList>
        <cpix:DRMSystem kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe" systemId="81376844-f976-481e-a84e-cc25d39b0b33">
            <speke:KeyFormat />
            <speke:KeyFormatVersions />
            <cpix:URIExtXKey>aHR0cHM6Ly9kMnVod2Jqc3p1ejF2Ny5jbG91ZGZyb250Lm5ldC81RTk5MTM3QS1CRDZDLTRFQ0MtQTI0RC1BM0VFMDRCNEUwMTEvNmM1ZjUyMDYtN2Q5OC00ODA4LTg0ZDgtOTRmMTMyYzFlOWZl</cpix:URIExtXKey>
        </cpix:DRMSystem>
    </cpix:DRMSystemList>
    <cpix:ContentKeyPeriodList>
        <cpix:ContentKeyPeriod id="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622" index="11425" />
    </cpix:ContentKeyPeriodList>
    <cpix:ContentKeyUsageRuleList>
        <cpix:ContentKeyUsageRule kid="6c5f5206-7d98-4808-84d8-94f132c1e9fe">
            <cpix:KeyPeriodFilter periodId="keyPeriod_e64248f6-f307-4b99-aa67-b35a78253622" />
        </cpix:ContentKeyUsageRule>
    </cpix:ContentKeyUsageRuleList>
</cpix:CPIX>
```
## 2. Configuring DRM on a MediaPackage EndPoint

1. Login to the AWS Console
1. Navigate to *MediaPackage*
1. Select the **live-livestream** channel
1. Scroll down to *Endpoints* section of the channel detals

![s3 link](/images/live_mediapackage-endpoints.png)

5. Select the **live-livestream-hls** endpoint and *edit* the endpoint
1. Scroll down to the *Package encryption* section of the endpoint details
1. Select the **Encrypt Content** radio button
1. Fill in the following encryption details
ResourceID : ```6c5f5206-7d98-4808-84d8-94f132c1e9fe``` <br>
DRM System ID :  ```81376844-f976-481e-a84e-cc25d39b0b33``` <br>
URL : ``` { SPEKEServerURL }``` <br>
MediaPackage Role : ```{MediaPackage Role from the Stack Output }```
1. Expand the *additional configuration*  
1. Select `AES 128` for the Encryption method.

![s3 link](/images/live_mediapackage_drm_config.png)
1. Click on **Save** to update your changes.

## 3. Play the videos

![s3 link](/images/live_mediapackage-encryption_config.png)

You can play the AES-128 encrypted HLS endpoint  using:
* Safari browser by clicking on the **Link** for the object.

* Open up the URL from the **DemoConsole** outlined in the Live Solution Stack.
* Copy the URL outlined in  **CloudFrontHlsEnpoint**  into the player

![s3 link](/images/live_mediapackage-preview-hls.png)

## Completion

Congratulations!  You have successfully created an encrypted live stream using  AWS Elemental MediaPackage. 
