import pytest
import xml.etree.ElementTree as ET
import time
import re
from .helpers import utils, speke_element_assertions


@pytest.fixture(scope="session")
def basic_response(spekev2_url, test_suite_dir):
    test_request_data = utils.read_xml_file_contents(test_suite_dir, utils.GENERIC_WIDEVINE_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response


@pytest.fixture(scope="session")
def duplicate_responses(spekev2_url, test_suite_dir, request_count=2):
    responses = []
    for request in range(0, request_count):
        test_request_data = utils.read_xml_file_contents(test_suite_dir, utils.GENERIC_WIDEVINE_TEST_FILE)
        responses.append(utils.speke_v2_request(spekev2_url, test_request_data).text)
        time.sleep(5)
    return responses[0] if request_count == 1 else responses


@pytest.fixture(scope="session")
def spekev1_style_request(spekev2_url, test_suite_dir):
    test_request_data = utils.read_xml_file_contents(test_suite_dir, utils.SPEKEV1_STYLE_REQUEST_WITH_SPEKEV2_HEADERS)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response


def test_status_code(basic_response):
    assert basic_response.status_code == 200


def test_speke_v2_headers(basic_response):
    content_type = basic_response.headers.get('Content-Type').lower()
    assert 'application/xml' in content_type, \
        "Content-Type must contain application/xml"

    if 'charset' in content_type:
        assert 'charset=utf-8' in content_type, \
            "Charset value, if present, must be 'utf-8'"

    speke_element_assertions.validate_spekev2_response_headers(basic_response)


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


# Check if this is to be included or we invalidate this request as incorrect in the API
def test_speke_v1_style_request_with_proper_response_received(spekev1_style_request):
    speke_element_assertions.validate_spekev2_response_headers(spekev1_style_request)
    root_cpix = ET.fromstring(spekev1_style_request.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 1, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 1, 1, 1, 0, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 1)
