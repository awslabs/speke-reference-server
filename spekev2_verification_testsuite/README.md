## Setting up an env and invoking the test suite

1. Install a pipenv environment
    - Reference: https://pipenv-fork.readthedocs.io/en/latest/install.html
2. Navigate to the test suite folder and run: `pipenv install`
3. Setup credentials to invoke the AWS resources using: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
4. Run the test suite using: `pipenv run pytest --speke-url <<SPEKE-API-GATEWAY-URL>>`
5. The test suite generates a report with name as: `report_timestamp.html` under a new folder named `reports`.

## Additional notes
- The test suite generates xml request files under `spekev2_requests`. This step is run every time the test suite is invoked.
- Existing folders and files are deleted if present and new ones are generated.
- To skip this step (when re-running the test suite, for example), use `--skip-artifact-generation`.
- To test on VOD suite, use `--test-vod`.
- Usage: `pipenv run pytest --speke-url <<SPEKE-API-GATEWAY-URL>> --skip-artifact-generation`

## SPEKE v2.1 coverage

`test_v2_1_content_key_period.py` covers SPEKE v2.1 `ContentKeyPeriod` start/end
signalling for live content with key rotation. The key provider signals the
wall-clock window a key period covers via the `start` and `end` attributes
(`xs:dateTime`) on `ContentKeyPeriod`, in addition to `@index`. Requests use the
`x-speke-version: 2.1` header; responses use CPIX `version="2.4"` and the
`X-Speke-Version: 2.1` header, and must echo back the same `start`/`end`.

The test runs like the rest of the suite and requires a v2.1-capable SPEKE gateway.
To run only this test:

```
pipenv run pytest --speke-url <<SPEKE-API-GATEWAY-URL>> test_v2_1_content_key_period.py
```

The request is generated under `spekev2_requests/test_case_7_v2_1_content_key_period/`
and is live-only (not generated with `--test-vod`).