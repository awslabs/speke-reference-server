## SPEKE Reference Server Installation

The following page guides the user through deployment and configuration of the SPEKE Reference Server.

## Prerequisites

- An AWS account with administrator rights and access to the AWS console
- Note that this solution can be deployed to any region that supports API Gateway, Lambda, and S3. You need to consider the packager or encoder's location relative to the API Gateway endpoint used to create encryption keys. The encoder, packager and SPEKE services should be in the same region or as geographically close as possible to reduce the request/response latency in key generation.

## Note

For ease of deployment, please use the pre-built template and Lambda binaries hosted by the project sponsors. The CloudFormation template located in the `src/` folder cannot be deployed to a stack without modification. Review the the `build_and_host.sh` to understand how to prepare the template for deployment with dependencies. 

## Setup CloudFormation Template

**The hosted template is supported in regions: ap-northeast-1 ap-northeast-2 ap-south-1 ap-southeast-1 ap-southeast-2 eu-central-1 eu-west-1 eu-west-3 sa-east-1 us-east-1 us-west-1 us-west-2**

1. Sign in to the AWS console.
1. Choose a region such as us-east-1 or us-west-2 to start.
1. Navigate to the AWS CloudFormation console.
1. Create a new stack.
1. On the `Select Template` page, provide the hosted copy of the CloudFormation template. The prepared CloudFormation template is hosted here by the project sponsors: `https://s3.amazonaws.com/rodeolabz-us-east-1/speke/speke_reference.json` and and can be launched in several AWS regions.
1. At the `Specify Details` pages, provide a stack name, like `SPEKE`.
1. Provide a value for the `KeyRetentionDays` parameter. This is the amount of time to retain a key in the S3 bucket for client playback. Keys older than this amount will be automatically removed by S3. The default is 2 days, which is usually enough for live content across multiple time zones.
2. The `Options` page does not require any input, although you can choose to be notified after the template completes.


When the template is complete you will have an operational reference SPEKE server that can be used for HLS encryption. You can review the Resources tab of the template to see what was created or updated, and the Outputs tab for the URL of the SPEKE server  and the role ARN that permits MediaPackage access.

[**Home**](README.md)
