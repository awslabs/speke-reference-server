## SPEKE Reference Server Installation

The following page guides the user through deployment and configuration of the SPEKE Reference Server.

## Prerequisites

- An AWS account with administrator rights and access to the AWS console
- Note that this solution can be deployed to any region that supports API Gateway, Lambda, and S3. You need to consider the packager or encoder's location relative to the API Gateway endpoint used to create encryption keys. The encoder, packager and SPEKE services should be in the same region or as geographically close as possible to reduce the request/response latency in key generation.

## Note

For ease of deployment, please use the pre-built template and Lambda binaries hosted by the project sponsors. The CloudFormation template located in the `src/` folder cannot be deployed to a stack without modification. Review the `build_and_host.sh` to understand how to prepare the template for deployment with dependencies. 

## Deploy changes to CloudFormation template and lambda function

1. Create a virtual environment for this project using python3.
1. Install dependencies within the virtual environment using `pip3 install -r requirements.txt`.
1. In `zappa_settings.json` under `src`, replace `aws_region` with the region this lambda will be deployed.
1. Create a `build` folder if it doesn't exist and then run `local_build.sh`.
1. The script will generate required artifacts under `build` folder.
1. Create a new bucket in S3 (For example: `speke-us-east-1`). Create a folder called `speke` and upload the generated `speke-reference` lambda zip file.
1. In the generated `speke_reference.json`, replace `rodeolabz` with the name of your created bucket (`speke` is used in this example).
1. Use the `speke_reference.json` template in CloudFormation to deploy the speke reference server following the instructions give below.

### Deploying from Mac/Windows
On platforms other than AmazonLinux, one of the required dependencies: `cffi` is generated differently and so running the reference server might result in an error: `No module named '_cffi_backend'`. To resolve this, create a `requirements.txt` file with `cffi==<version>`, replacing version with the desired version number and follow the steps outlined [here](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-layer-simulated-docker/) to create a layer and update the speke reference lambda function.

## Deploy using prepared CloudFormation template

**The hosted template is supported in regions: ap-northeast-1 ap-northeast-2 ap-south-1 ap-southeast-1 ap-southeast-2 eu-central-1 eu-west-1 eu-west-3 sa-east-1 us-east-1 us-west-1 us-west-2**

1. Sign in to the AWS console.
1. Choose a region such as us-east-1 or us-west-2 to start.
1. Navigate to the AWS CloudFormation console.
1. Create a new stack.
1. On the `Select Template` page, provide the hosted copy of the CloudFormation template. The prepared CloudFormation template is hosted here by the project sponsors: `https://s3.amazonaws.com/rodeolabz-us-east-1/speke/speke_reference.json` and and can be launched in several AWS regions.
1. At the `Specify Details` pages, provide a stack name, like `SPEKE`.
1. Provide a value for the `KeyRetentionDays` parameter. This is the amount of time to retain a key in the S3 bucket for client playback. Keys older than this amount will be automatically removed by S3. The default is 2 days, which is usually enough for live content across multiple time zones.
1. The `Options` page does not require any input, although you can choose to be notified after the template completes.


When the template is complete you will have an operational reference SPEKE server that can be used for HLS encryption. You can review the Resources tab of the template to see what was created or updated, and the Outputs tab for the URL of the SPEKE server  and the role ARN that permits MediaPackage access.

[**Home**](README.md)
