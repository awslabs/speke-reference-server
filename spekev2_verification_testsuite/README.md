## Setting up an env and invoking the test suite

1. Install a pipenv environment
    - Reference: https://pipenv-fork.readthedocs.io/en/latest/install.html
2. Navigate to the test suite folder and run: `pipenv install`
3. Setup credentials to invoke the AWS resources using: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
4. Run the test suite using: `pipenv run pytest --speke-url <<SPEKE-API-GATEWAY-URL>>`
5. The test suite generates a report with name as: `report_timestamp.html` under a new folder named `reports`.