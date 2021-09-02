import pytest
import xml.etree.ElementTree as ET
from io import StringIO
from . import utils

@pytest.fixture
def generic_request(spekev2_url):
    return utils.read_xml_file_contents(utils.GENERIC_WIDEVINE_TEST_FILE)

@pytest.fixture
def empty_xml_response(spekev2_url):
    response = utils.speke_v2_request(spekev2_url, "")
    return response

@pytest.fixture
def wrong_version_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.WRONG_VERSION_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response

def test_empty_request(empty_xml_response):
    assert empty_xml_response.status_code != 200 and (400 <= empty_xml_response.status_code < 600), \
    "Empty request is expected to return an error"

def test_wrong_version_status_code(wrong_version_response):
    assert wrong_version_response.status_code != 200 and (400 <= wrong_version_response.status_code < 600), \
    "Wrong version in the request is expected to return an error"

@pytest.mark.parametrize("mandatory_element", utils.SPEKE_V2_MANDATORY_ELEMENTS_LIST)
def test_mandatory_elements_missing_in_request(spekev2_url, generic_request, mandatory_element):
    request_cpix = ET.fromstring(generic_request)
    for node in request_cpix.iter():
        for child in node.findall(mandatory_element):
                node.remove(child)
            
    request_xml_data = ET.tostring(request_cpix, method="xml")    
    response = utils.speke_v2_request(spekev2_url, request_xml_data)

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
    f"Mandatory element: {mandatory_element} not present in request but response was a 200 OK"

def test_both_mandatory_filter_elements_missing_in_request(spekev2_url, generic_request):
    request_cpix = ET.fromstring(generic_request)
    for node in request_cpix.iter():
        for elem in utils.SPEKE_V2_MANDATORY_FILTER_ELEMENTS_LIST:
            for child in node.findall(elem):
                    node.remove(child)
            
    request_xml_data = ET.tostring(request_cpix, method="xml")    
    response = utils.speke_v2_request(spekev2_url, request_xml_data)

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
    f"Mandatory filter elements: {utils.SPEKE_V2_MANDATORY_FILTER_ELEMENTS_LIST} not present in request but response was a 200 OK"

@pytest.mark.parametrize("mandatory_attribute", utils.SPEKE_V2_MANDATORY_ATTRIBUTES_LIST)
def test_missing_mandatory_attributes_in_request(spekev2_url, generic_request, mandatory_attribute):
    request_cpix = ET.fromstring(generic_request)
    for node in request_cpix.iter():
        for child in node.findall(mandatory_attribute[0]):
            for attribute in [x for x in mandatory_attribute[1] if x in child.attrib]:
                child.attrib.pop(attribute)
    
    
    request_xml_data = ET.tostring(request_cpix, method="xml")
    response = utils.speke_v2_request(spekev2_url, request_xml_data)

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
    f"Mandatory attribute(s): {mandatory_attribute[1]} for element: {mandatory_attribute[0]} not present in request but response was a 200 OK"