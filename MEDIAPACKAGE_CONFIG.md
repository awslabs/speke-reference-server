## AWS Elemental MediaPackage Configuration for SPEKE Reference Server

The following page guides the user through configuration of AWS Elemental MediaPackage to utilize the SPEKE Reference Server. At the end of this page you will have created an HLS encrypted endpoint for an existing AWS MediaPackage channel that uses the SPEKE server deployed from this project.

## Prerequisites

- An AWS account with administrator rights and access to the AWS console.
- An AWS MediaPackage channel that is currently ingesting video from an encoder, such as AWS MediaLive.
- If you need to create a media workflow with AWS MediaLive and AWS MediaPackage quickly, consider deploying the LiveStreamingWorkshopResources.json template provided by this GitHub project as a first step: https://github.com/aws-samples/aws-media-services-simple-live-workflow.
- Note that this solution can be deployed to any region that supports API Gateway, Lambda, and S3 and Media Services. You need to consider the packager or encoder's location relative to the API Gateway endpoint used to create encryption keys. The encoder, packager and SPEKE services should be in the same region or as geographically close as possible to reduce the request/response latency in key generation.

## Required Information

- Channel ID of the AWS MediaPackage channel
- Role ARN of the `MediaPackageInvokeSPEKERole` previously created by the reference template
- Rotation Interval is the number seconds a new key is required during live play
- Server URL is the API Gateway URL of the SPEKE server that ends with the path /EkeStage/copyProtection

## CloudFormation Templates

1. Sign in to the AWS console.
1. Choose a region such as us-east-1 or us-west-2. You should have the SPEKE server, encoder and packager running in the same AWS Region.
1. Navigate to the AWS CloudFormation console.
1. Create a new stack.
1. On the `Select Template` page, provide the local or hosted copy of the template. The CloudFormation template is is named `mediapackage_speke_endpoint.json` and is available in the cloudformation folder in this project, and also hosted here by the project sponsors: `https://s3.amazonaws.com/rodeolabz-us-east-1/speke/mediapackage_speke_endpoint.json`
1. At the `Specify Details` pages, provide a stack name, like `ENDPOINT`.
1. Provide the information you collected from the `Required Information` section above.
2. The `Options` page does not require any input, although you can choose to be notified after the template completes.

When the template is complete you will have an operational reference SPEKE server that can be used for HLS encryption. You can review the Resources tab of the template to see what was created or updated.

Navigate to the AWS MediaPackage channel and look for the endpoint with `MediaPackageEncryptedEndpoint` in the name.

You can play the endpoint with Safari, QuickTime Player, or an HLS-compatible browser player such as Video.js.


## Manual Configuration


1. Create an HLS endpoint and select Encrypt content.
1. For Resource ID, enter any valid string.
1. For System ID, enter
```
81376844-f976-481e-a84e-cc25d39b0b33
```
1. The system ID is part of the DASH-IF CPIX standard, which we have adopted for our key exchange protocol. It defines the DRM system. System ID is defined for DASH Widevine, DASH PlayReady, and so on.  When setting up your own HLS DRM solution, you can configure whatever you want on the endpoint, as long as your key server knows what to do with it.
1. For URL, paste in the API Gateway URL of the SPEKE server that ends with the path /EkeStage/copyProtection, as in:
```
https://ayh8dwke5b.execute-api.us-west-2.amazonaws.com/EkeStage/copyProtection
```
1. For Role ARN, paste in the `MediaPackageInvokeSPEKERole` previously created by the reference template
1. Under Additional configuration, leave the Encryption Method at AES-128
2. Set the key rotation interval to 60 seconds
1. Save the endpoint

The output should now be encrypted (you can check by downloading the manifests). The endpoint should play back on Safari and Quicktime on a Mac. 


## HLS Manifest Check

The second-level HLS manifests will include key retrieval information in the EXT-X-KEY label for one or more segments.
```
#EXTM3U
#EXT-X-VERSION:4
#EXT-X-TARGETDURATION:7
#EXT-X-MEDIA-SEQUENCE:9922
#EXT-X-KEY:METHOD=AES-128,URI="https://d33vycj6dbbmzj.cloudfront.net/7e4de17c-a065-4ce8-874f-f3ed68c5c5f1/f50e4740-d16e-4374-a2e5-4f43134b3cf2"
#EXTINF:6.006,
index_9_9922.ts?m=1524544797
#EXTINF:6.006,
index_9_9923.ts?m=1524544797
#EXTINF:6.006,
index_9_9924.ts?m=1524544797
#EXTINF:6.006,
index_9_9925.ts?m=1524544797
#EXTINF:6.006,
index_9_9926.ts?m=1524544797
#EXTINF:6.006,
index_9_9927.ts?m=1524544797
#EXTINF:6.006,
index_9_9928.ts?m=1524544797
#EXTINF:6.006,
index_9_9929.ts?m=1524544797
#EXT-X-KEY:METHOD=AES-128,URI="https://d33vycj6dbbmzj.cloudfront.net/7e4de17c-a065-4ce8-874f-f3ed68c5c5f1/62e65271-1e30-4e0d-aed5-06a947028d99"
#EXTINF:6.006,
index_9_9930.ts?m=1524544797


```

[**Home**](README.md)