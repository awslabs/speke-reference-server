import pytest
import xml.etree.ElementTree as ET
import time
import re
from .helpers import utils, speke_element_assertions


@pytest.fixture(scope="session")
def basic_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents("general", utils.GENERIC_WIDEVINE_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response


@pytest.fixture(scope="session")
def duplicate_responses(spekev2_url, request_count=2):
    responses = []
    for request in range(0, request_count):
        test_request_data = utils.read_xml_file_contents("general", utils.GENERIC_WIDEVINE_TEST_FILE)
        responses.append(utils.speke_v2_request(spekev2_url, test_request_data).text)
        time.sleep(5)
    return responses[0] if request_count == 1 else responses


def test_status_code(basic_response):
    assert basic_response.status_code == 200


def test_speke_v2_headers(basic_response):
    content_type = basic_response.headers.get('Content-Type').lower()
    assert 'application/xml' in content_type, \
        "Content-Type must contain application/xml"

    if 'charset' in content_type:
        assert 'charset=utf-8' in content_type, \
            "Charset value, if present, must be 'utf-8'"

    assert basic_response.headers.get('X-Speke-Version') == '2.0', \
        "X-Speke-Version must be 2.0"
    assert basic_response.headers.get('X-Speke-User-Agent'), \
        "X-Speke-User-Agent must be present in the response"


def test_speke_v2_elements_have_not_changed(basic_response):
    # Validate no new elements were added
    elements_in_response = list(utils.count_tags(basic_response.text).keys())
    assert all(element in elements_in_response for element in utils.SPEKE_V2_GENERIC_RESPONSE_ELEMENT_LIST), \
        "Response must not remove any elements present in the request"

    # Validate no new attribs added apart other than the ones in the request
    root_cpix = ET.fromstring(basic_response.text)
    assert all(attribute in root_cpix.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX'])

    # Validate CPIX version is 2.3
    speke_element_assertions.check_cpix_version(root_cpix)

    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')

    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')
    for content_key_element in content_key_elements:
        assert all(attribute in content_key_element.attrib for attribute in
                   utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKey']), \
            "Response must contain values for all mandatory attributes for ContentKey element"
        assert content_key_element.get('commonEncryptionScheme') == 'cenc'

    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    for drm_system_element in drm_system_elements:
        assert all(attribute in drm_system_element.attrib for attribute in
                   utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']), \
            "Response must contain values for all mandatory attributes for DRMSystem element"
        assert drm_system_element.get('systemId') == utils.WIDEVINE_SYSTEM_ID, \
            "Request had Widevine SystemID which must remain unchanged"

    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall(
        './{urn:dashif:org:cpix}ContentKeyUsageRule')
    for content_key_usage_rule_element in content_key_usage_rule_elements:
        assert all(attribute in content_key_usage_rule_element.attrib for attribute in
                   utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']), \
            "Response must contain values for all mandatory attributes for ContentKeyUsageRule element"
        assert content_key_usage_rule_element.get('intendedTrackType') in utils.SPEKE_V2_SUPPORTED_INTENDED_TRACK_TYPES, \
            f"intendedTrackType value must be one of {utils.SPEKE_V2_SUPPORTED_INTENDED_TRACK_TYPES}"


def test_sending_same_request_sent_twice_to_keyserver_without_key_rotation(duplicate_responses):
    test_responses = [response.replace("\n", "").replace("\r", "") for response in duplicate_responses]
    regex_pattern = "<pskc:PlainValue>(.*)</pskc:PlainValue>(.*)<pskc:PlainValue>(.*)</pskc:PlainValue>"
    results = []
    for response in test_responses:
        results.append(re.search(regex_pattern, response))

    if results[0] is not None:
        assert results[0].group(1) == results[1].group(1) and results[0].group(3) == results[1].group(3), \
            "Keys returned for duplicate responses must be the same with key rotation turned off"
    else:
        assert False, \
            "Pattern matching failed"