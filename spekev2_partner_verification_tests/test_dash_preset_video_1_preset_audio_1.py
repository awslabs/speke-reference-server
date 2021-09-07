import xml.etree.ElementTree as ET
import pytest
import requests
from . import utils

@pytest.fixture(scope="session")
def widevine_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.GENERIC_WIDEVINE_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text
    

@pytest.fixture(scope="session")
def widevine_pssh_cpd_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.WIDEVINE_PSSH_CPD_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text

@pytest.fixture(scope="session")
def playready_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.GENERIC_PLAYREADY_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text
    

@pytest.fixture(scope="session")
def playready_pssh_cpd_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.PLAYREADY_PSSH_CPD_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text

@pytest.fixture(scope="session")
def widevine_playready_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.WIDEVINE_PLAYREADY_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text

def test_dash_widevine_no_rotation(widevine_response):
    root_cpix = ET.fromstring(widevine_response)
    assert all(attribute in root_cpix.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']), \
    f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']} for CPIX element are expected in the response"
    assert root_cpix.get('version') == '2.3', \
    "Attribute: version value for CPIX element is expected to be 2.3"

    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')
    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')
    assert content_key_elements

    assert content_key_elements[0].get('kid') != content_key_elements[1].get('kid'), \
    "kid attribute values for the different ContentKey elements under ContentKeyList are expected to be different"
    for content_key_element in content_key_elements:
        assert content_key_element.find('./{urn:dashif:org:cpix}Data/{urn:ietf:params:xml:ns:keyprov:pskc}Secret/{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue').text, \
        "PlainValue child element under Secret is expected to contain data for this request"
        assert content_key_element.get('commonEncryptionScheme') == 'cenc', \
        "commonEncryptionScheme attribute for ContentKey is expected to contain the value cenc"
    
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    assert len(drm_system_elements) == 2, \
    "Two DRMSystem elements are expected, one for Video and other for Audio in this response"
    
    assert drm_system_elements[0].get('kid') != drm_system_elements[1].get('kid')
    for drm_system_element in drm_system_elements:
        assert all(attribute in drm_system_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']} for DRMSystem element are expected in the response"
        assert drm_system_element.get('systemId') == utils.WIDEVINE_SYSTEM_ID, \
        "SystemID for Widevine is expected in the response and must remain unchanged and must remain unchanged from the request"

        pssh_data = drm_system_element.findall('./{urn:dashif:org:cpix}PSSH')
        assert len(pssh_data) == 1, \
        "Exactly 1 PSSH element is expected"
        assert pssh_data[0].text, \
        "PSSH element is expected to contain data"

        smooth_streaming_protection_header_data_element = drm_system_element.findall('./{urn:dashif:org:cpix}SmoothStreamingProtectionHeaderData')
        assert not smooth_streaming_protection_header_data_element, \
        "SmoothStreamingProtectionHeaderData is not expected in this response"

    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall('./{urn:dashif:org:cpix}ContentKeyUsageRule')
    assert len(content_key_usage_rule_elements) == 2, \
    "Exactly 2 ContentKeyUsageRule elements are expected under ContentKeyUsageRuleList in this response"
    assert content_key_usage_rule_elements[0].get('kid') != content_key_usage_rule_elements[1].get('kid'), \
    "kid attribute values for the different ContentKeyUsageRule are expected to be different"
    assert content_key_usage_rule_elements[0].get('intendedTrackType') != content_key_usage_rule_elements[1].get('intendedTrackType'), \
    "intendedTrackType attribute values for the different ContentKeyUsageRule are expected to be different"

    for content_key_usage_rule_element in content_key_usage_rule_elements:
        assert all(attribute in content_key_usage_rule_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']} are expected for ContentKeyUsageRule element"
        assert content_key_usage_rule_element.get('intendedTrackType') in utils.SPEKE_V2_SUPPORTED_INTENDED_TRACK_TYPES, \
        "intendedTrackType is a mandatory element for ContentKeyUsageRule"


def test_dash_playready_no_rotation(playready_response):
    root_cpix = ET.fromstring(playready_response)
    assert all(attribute in root_cpix.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']), \
    f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']} for CPIX element are expected in the response"
    assert root_cpix.get('version') == '2.3', \
    "Attribute: version value for CPIX element is expected to be 2.3"

    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')
    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')
    assert len(content_key_elements) == 2, \
    "2 ContentKey elements are expected under ContentKeyList"
    assert content_key_elements[0].get('kid') != content_key_elements[1].get('kid'), \
    "kid attribute values for the different ContentKey elements under ContentKeyList are expected to be different"
    for content_key_element in content_key_elements:
        assert content_key_element.find('./{urn:dashif:org:cpix}Data/{urn:ietf:params:xml:ns:keyprov:pskc}Secret/{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue').text, \
        "PlainValue child element under Secret is expected to contain data for this request"
        assert content_key_element.get('commonEncryptionScheme') == 'cenc', \
        "commonEncryptionScheme attribute for ContentKey is expected to contain the value cenc"
    
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    assert len(drm_system_elements) == 2, \
    "Two DRMSystem elements are expected, one for Video and other for Audio in this response"
    assert drm_system_elements[0].get('kid') != drm_system_elements[1].get('kid'), \
    "kid attribute values for the different DRMSystem elements are expected to be different"
    for drm_system_element in drm_system_elements:
        assert all(attribute in drm_system_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']} for DRMSystem element are expected in the response"
        assert drm_system_element.get('systemId') == utils.PLAYREADY_SYSTEM_ID, \
        "SystemID for PlayReady is expected in the response and must remain unchanged from the request"

        pssh_data = drm_system_element.findall('./{urn:dashif:org:cpix}PSSH')
        assert len(pssh_data) == 1, \
        "Exactly 1 PSSH element is expected in the response"
        assert pssh_data[0].text, \
        "PSSH element is expected to contain data"
    
    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall('./{urn:dashif:org:cpix}ContentKeyUsageRule')
    assert len(content_key_usage_rule_elements) == 2, \
    "Exactly 2 ContentKeyUsageRule elements are expected under ContentKeyUsageRuleList in this response"
    assert content_key_usage_rule_elements[0].get('kid') != content_key_usage_rule_elements[1].get('kid'), \
    "kid attribute values for the different ContentKeyUsageRule are expected to be different"
    assert content_key_usage_rule_elements[0].get('intendedTrackType') != content_key_usage_rule_elements[1].get('intendedTrackType'), \
    "intendedTrackType attribute values for the different ContentKeyUsageRule are expected to be different"

    for content_key_usage_rule_element in content_key_usage_rule_elements:
        assert all(attribute in content_key_usage_rule_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']} are expected for ContentKeyUsageRule element"
        assert content_key_usage_rule_element.get('intendedTrackType') in utils.SPEKE_V2_SUPPORTED_INTENDED_TRACK_TYPES, \
        "intendedTrackType is a mandatory element for ContentKeyUsageRule"

def test_dash_widevine_playready_no_rotation(widevine_playready_response):
    root_cpix = ET.fromstring(widevine_playready_response)
    assert all(attribute in root_cpix.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']), \
    f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']} for CPIX element are expected in the response"
    assert root_cpix.get('version') == '2.3', \
    "Attribute: version value for CPIX element is expected to be 2.3"

    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')
    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')
    assert len(content_key_elements) == 2, \
    "2 ContentKey elements are expected under ContentKeyList"
    assert content_key_elements[0].get('kid') != content_key_elements[1].get('kid'), \
    "kid attribute values for the different ContentKey elements under ContentKeyList are expected to be different"
    for content_key_element in content_key_elements:
        assert content_key_element.find('./{urn:dashif:org:cpix}Data/{urn:ietf:params:xml:ns:keyprov:pskc}Secret/{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue').text, \
        "PlainValue child element under Secret is expected to contain data for this request"
        assert content_key_element.get('commonEncryptionScheme') == 'cenc', \
        "commonEncryptionScheme attribute for ContentKey is expected to contain the value cenc"
    
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    assert len(drm_system_elements) == 4, \
    "4 DRMSystem elements are expected, 2 for Widewine and 2 for PlayReady and 1 each for Video and Audio"
    
    find_string_for_playready = "./{urn:dashif:org:cpix}DRMSystem[@systemId='" + utils.PLAYREADY_SYSTEM_ID + "']"
    drm_system_elements_for_playready = drm_system_list_element.findall(find_string_for_playready)
    assert len(drm_system_elements_for_playready) == 2, "Two DRMSystem elements for Playready are expected"
    assert drm_system_elements_for_playready[0].get('kid') != drm_system_elements_for_playready[1].get('kid'), \
    "kid attribute values for the 2 DRM elements for Playready are expected to be different"

    find_string_for_widevine = "./{urn:dashif:org:cpix}DRMSystem[@systemId='" + utils.WIDEVINE_SYSTEM_ID + "']"
    drm_system_elements_for_widevine = drm_system_list_element.findall(find_string_for_widevine)
    assert len(drm_system_elements_for_widevine) == 2, "Two DRMSystem elements for Widevine are expected"
    assert drm_system_elements_for_widevine[0].get('kid') != drm_system_elements_for_widevine[1].get('kid'), \
    "kid attribute values for the 2 DRM elements for Widevine are expected to be different"

    for drm_system_element in drm_system_elements:
        assert all(attribute in drm_system_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['DRMSystem']} for DRMSystem element are expected in the response"
        assert drm_system_element.get('systemId') in [utils.WIDEVINE_SYSTEM_ID, utils.PLAYREADY_SYSTEM_ID], \
        "systemId value is expected to be either Widevine or Playready"

    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall('./{urn:dashif:org:cpix}ContentKeyUsageRule')
    assert len(content_key_usage_rule_elements) == 2, \
    "Exactly 2 ContentKeyUsageRule elements are expected under ContentKeyUsageRuleList in this response"
    assert content_key_usage_rule_elements[0].get('kid') != content_key_usage_rule_elements[1].get('kid'), \
    "kid attribute values for the different ContentKeyUsageRule elements are expected to be different"
    assert content_key_usage_rule_elements[0].get('intendedTrackType') != content_key_usage_rule_elements[1].get('intendedTrackType')

    for content_key_usage_rule_element in content_key_usage_rule_elements:
        assert all(attribute in content_key_usage_rule_element.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['ContentKeyUsageRule']} are expected for ContentKeyUsageRule element"
        assert content_key_usage_rule_element.get('intendedTrackType') in utils.SPEKE_V2_SUPPORTED_INTENDED_TRACK_TYPES, \
        "intendedTrackType is a mandatory element for ContentKeyUsageRule"


def test_dash_widevine_pssh_cpd_no_rotation(widevine_pssh_cpd_response):
    root_cpix = ET.fromstring(widevine_pssh_cpd_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')
        
        content_protection_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}ContentProtectionData')
        content_protection_data_string = utils.decode_b64_bytes(content_protection_data_bytes.text)
        pssh_in_cpd = ET.fromstring(content_protection_data_string)

        #Assert pssh in cpd is same as pssh box
        assert pssh_data_bytes.text == pssh_in_cpd.text, \
        "Content in PSSH box and the requested content in ContentProtectionData are expected to be the same"

def test_dash_playready_pssh_cpd_no_rotation(playready_pssh_cpd_response):
    root_cpix = ET.fromstring(playready_pssh_cpd_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')
        
        content_protection_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}ContentProtectionData')
        content_protection_data_string = utils.decode_b64_bytes(content_protection_data_bytes.text)
        
        cpd_xml = '<cpd>' + content_protection_data_string + '</cpd>'

        cpd_root = ET.fromstring(cpd_xml)
        pssh_in_cpd = cpd_root.find("./{urn:mpeg:cenc:2013}pssh")

        #Assert pssh in cpd is same as pssh box
        assert pssh_data_bytes.text == pssh_in_cpd.text, \
        "Content in PSSH box and the requested content in ContentProtectionData are expected to be the same"
    