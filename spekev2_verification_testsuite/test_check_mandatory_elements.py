import pytest
import xml.etree.ElementTree as ET
from io import StringIO
import requests

from . import utils

@pytest.fixture(scope="session")
def basic_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.GENERIC_WIDEVINE_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text


def test_cpix_root_in_response(basic_response):
    required_namespaces = utils.SPEKE_V2_MANDATORY_NAMESPACES
    namespaces_in_response = dict([node for _, node in ET.iterparse(StringIO(basic_response), events=['start-ns'])])

    # Validate if required namespaces are present in the response
    assert all(ns in namespaces_in_response for ns in required_namespaces), \
    f"Requred namespaces must be present in response: {utils.SPEKE_V2_MANDATORY_NAMESPACES}"

    root_cpix = ET.fromstring(basic_response)

    # Validate if root element is CPIX
    assert root_cpix.tag == "{urn:dashif:org:cpix}CPIX", \
    "CPIX is a mandatory element"

    # Validate if CPIX has required attributes
    assert root_cpix.get('contentId'), \
    "contentId is a mandatory attribute for CPIX"

    assert root_cpix.get('version'), \
    "version is a mandatory attribute for CPIX"

    # Validate if CPIX has required attribute version and its value is 2.3
    assert root_cpix.get('version') == '2.3', \
    "version is a mandatory attribute for CPIX and its value must be 2.3 for Speke V2"

    # Validate if CPIX does not have attribute id as it was changed to contentId
    assert 'id' not in root_cpix.attrib, \
    "id is a deprecated attribute for CPIX and it is not expected in the response for Speke V2"
    cpix_elements_dict = utils.count_child_element_tags_for_element(root_cpix)

    # Validate if CPIX element has all mandatory child elements present and have only 1 instance
    assert '{urn:dashif:org:cpix}ContentKeyList' in cpix_elements_dict
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}ContentKeyList') == 1, \
    "Only one ContentKeyList element is expected"

    assert '{urn:dashif:org:cpix}DRMSystemList' in cpix_elements_dict
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}DRMSystemList') == 1, \
    "Only one DRMSystemList element is expected"

    assert '{urn:dashif:org:cpix}ContentKeyUsageRuleList' in cpix_elements_dict     
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}ContentKeyUsageRuleList') == 1, \
    "Only one ContentKeyUsageRuleList element is expected"


def test_cpix_content_key_list_in_response(basic_response):
    root_cpix = ET.fromstring(basic_response)

    # Validate attributes and elements for content_key_list element
    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')
    content_key_list_child_elements = utils.count_child_element_tags_for_element(content_key_list_element)
    
    # Validate presence of ContentKey element
    assert '{urn:dashif:org:cpix}ContentKey' in content_key_list_child_elements, \
    "Atleast one ContentKey element is expected in ContentKeyList"
    assert content_key_list_child_elements.get('{urn:dashif:org:cpix}ContentKey') >= 1, \
    "Atleast one ContentKey element is expected in ContentKeyList"
    
    # Validate mandatory attributes for ContentKey element
    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')

    for content_key_element in content_key_elements:
        assert content_key_element.get('kid'), \
        "kid is a mandatory attribute for ContentKey element"
        assert content_key_element.get('commonEncryptionScheme'), \
        "commonEncryptionScheme is a mandatory attribute for  ContentKey element"
        assert content_key_element.get('commonEncryptionScheme') in utils.SPEKE_V2_CONTENTKEY_COMMONENCRYPTIONSCHEME_ALLOWED_VALUES, \
        f"commonEncryptionScheme is a mandatory attribute for  ContentKey element and must be one of {utils.SPEKE_V2_CONTENTKEY_COMMONENCRYPTIONSCHEME_ALLOWED_VALUES}"
    
        # Validate ContentKey has Data element present. 
        # This element is not in the request but response is expected to have it.
        content_key_child_elements = utils.count_child_element_tags_for_element(content_key_element)
        assert '{urn:dashif:org:cpix}Data' in content_key_child_elements
        assert content_key_child_elements.get('{urn:dashif:org:cpix}Data') == 1, \
        "Data is a mandatory child element of ContentKey"

        # Validate Data has Secret element present
        data_elements = content_key_element.findall('{urn:dashif:org:cpix}Data')
        assert data_elements 

        for data_element in data_elements:
            data_child_elements = utils.count_child_element_tags_for_element(data_element)
            assert '{urn:ietf:params:xml:ns:keyprov:pskc}Secret' in data_child_elements
            assert data_child_elements.get('{urn:ietf:params:xml:ns:keyprov:pskc}Secret') == 1, \
            "Secret is a mandatory child element of Data"

            # Validate Secret has either PlainValue or EncryptedValue element present
            secret_elements = data_element.findall('{urn:ietf:params:xml:ns:keyprov:pskc}Secret')
            assert secret_elements 

            for secret_element in secret_elements:
                assert secret_element.find('{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue').text  or secret_element.find('{urn:ietf:params:xml:ns:keyprov:pskc}EncryptedValue').text, \
                "Either PlainValue or EncryptedValue child element is expected within Secret"
                
def test_drm_system_list_in_response(basic_response):
    root_cpix = ET.fromstring(basic_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_list_child_elements = utils.count_child_element_tags_for_element(drm_system_list_element)

    # Validate presence of DRMSystem in DRMSystemList
    assert '{urn:dashif:org:cpix}DRMSystem' in drm_system_list_child_elements
    assert drm_system_list_child_elements.get('{urn:dashif:org:cpix}DRMSystem') >= 1, \
    "DRMSystem is a mandatory child element of DRMSystemList"

    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    # Validate presence of required attributes in DRMSystem
    for drm_system_element in drm_system_elements:
        assert drm_system_element.get('kid'), \
        "kid is a mandatory attribute of DRMSystem"
        assert drm_system_element.get('systemId'), \
        "systemId is a mandatory attribute of DRMSystem"

def test_content_key_usage_rule_list_in_response(basic_response):
    root_cpix = ET.fromstring(basic_response)
    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_child_elements = utils.count_child_element_tags_for_element(content_key_usage_rule_list_element)

    # Validate presence of ContentKeyUsageRule in ContentKeyUsageRuleList
    assert content_key_usage_rule_child_elements 
    assert '{urn:dashif:org:cpix}ContentKeyUsageRule' in content_key_usage_rule_child_elements, \
    "ContentKeyUsageRule is a mandatory child element of ContentKeyUsageRuleList"
    assert content_key_usage_rule_child_elements.get('{urn:dashif:org:cpix}ContentKeyUsageRule') >= 1, \
    "Atleast 1 ContentKeyUsageRule is expected under ContentKeyUsageRuleList"
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall('./{urn:dashif:org:cpix}ContentKeyUsageRule')

    # Validate presence of of required attributes in ContentKeyUsageRule
    for content_key_usage_rule_element in content_key_usage_rule_elements: 
        assert content_key_usage_rule_element.get('kid'), \
        "kid is a mandatory attribute of ContentKeyUsageRule" 
        assert content_key_usage_rule_element.get('intendedTrackType'), \
        "intendedTrackType is a mandatory attribute of ContentKeyUsageRule"  

        content_key_usage_child_elements = utils.count_child_element_tags_for_element(content_key_usage_rule_element)
        assert any([elem in ['{urn:dashif:org:cpix}VideoFilter','{urn:dashif:org:cpix}AudioFilter'] for elem in content_key_usage_child_elements]), \
        "Either VideoFilter or AudioFilter element is expected within ContentKeyUsageRule"
