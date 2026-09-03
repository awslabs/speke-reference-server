import pytest
from .helpers import utils, speke_element_assertions
import xml.etree.ElementTree as ET


@pytest.fixture(scope="session")
def v2_1_widevine_request_and_response(spekev2_url):
    """
    Send the SPEKE v2.1 live request (ContentKeyPeriod with start/end) using the
    x-speke-version: 2.1 header and return both the request bytes and the full
    response object so the test can parse both trees and inspect response headers.
    """
    return utils.send_speke_request_full(
        utils.TEST_CASE_7_V2_1_CONTENT_KEY_PERIOD,
        utils.V2_1_WIDEVINE_LIVE_START_END,
        spekev2_url,
        utils.SPEKE_V2_1_REQUEST_HEADERS,
    )


def test_v2_1_content_key_period_start_end(v2_1_widevine_request_and_response):
    request_data, response = v2_1_widevine_request_and_response

    # SPEKE v2.1 signals itself via the response header and CPIX 2.4.
    speke_element_assertions.validate_spekev2_response_headers(response, expected_speke_version='2.1')

    request_root = ET.fromstring(request_data)
    response_root = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(response_root, expected=2.4)
    speke_element_assertions.validate_root_element(response_root)

    # The rotation window is authoritative: each ContentKeyPeriod's start/end must be
    # echoed back unchanged (compared as UTC instants).
    speke_element_assertions.validate_content_key_period_start_end_echoed(request_root, response_root)
