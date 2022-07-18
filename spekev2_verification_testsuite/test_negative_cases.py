import pytest
import xml.etree.ElementTree as ET
from io import StringIO
from .helpers import utils, speke_element_assertions


@pytest.fixture
def generic_request(spekev2_url, test_suite_dir):
    return utils.read_xml_file_contents(test_suite_dir, utils.GENERIC_WIDEVINE_TEST_FILE)

@pytest.fixture
def fairplay_request(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_1_P_V_1_A_1, utils.PRESETS_FAIRPLAY)


@pytest.fixture
def preset_negative_preset_shared_video(spekev2_url, test_suite_dir):
    return utils.read_xml_file_contents(test_suite_dir, utils.NEGATIVE_PRESET_SHARED_VIDEO)


@pytest.fixture
def preset_negative_preset_shared_audio(spekev2_url, test_suite_dir):
    return utils.read_xml_file_contents(test_suite_dir, utils.NEGATIVE_PRESET_SHARED_AUDIO)


@pytest.fixture
def empty_xml_response(spekev2_url):
    response = utils.speke_v2_request(spekev2_url, "")
    return response


@pytest.fixture
def wrong_version_response(spekev2_url, test_suite_dir):
    test_request_data = utils.read_xml_file_contents(test_suite_dir, utils.WRONG_VERSION_TEST_FILE)
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
    response = utils.send_modified_speke_request_with_element_removed(spekev2_url, generic_request, mandatory_element)
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
        f"Mandatory filter elements: {utils.SPEKE_V2_MANDATORY_FILTER_ELEMENTS_LIST} not present in request but " \
        f"response was a 200 OK "


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
        f"Mandatory attribute(s): {mandatory_attribute[1]} for element: {mandatory_attribute[0]} not present in " \
        f"request but response was a 200 OK "


def test_common_encryption_scheme_for_fairplay_should_not_be_cenc(spekev2_url, fairplay_request):
    xml_request = fairplay_request.decode('UTF-8').replace("cbcs", "cenc")
    response = utils.speke_v2_request(spekev2_url, xml_request.encode('UTF-8'))

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
        f"Requests for Fairplay DRM system ID should not include cenc as common encryption. Status code returned was {response.status_code}"


def test_video_preset_2_and_shared_audio_preset_request_expect_4xx(spekev2_url, preset_negative_preset_shared_audio):
    """
    Intended track type(s) used in this test are SD, ALL, STEREO_AUDIO, MULTICHANNEL_AUDIO
    Expected to return HTTP 4xx error
    """

    xml_request = preset_negative_preset_shared_audio.decode('UTF-8')
    response = utils.speke_v2_request(spekev2_url, xml_request.encode('UTF-8'))

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
        f"If intendedTrackType with ALL is requested, there cannot be other ContentKeyUsageRule elements with " \
        f"different intendedTrackType values "


def test_shared_video_preset_and_audio_preset_2_request_expect_4xx(spekev2_url, preset_negative_preset_shared_video):
    """
    Intended track type(s) used in this test are SD, HD, ALL, MULTICHANNEL_AUDIO
    :returns: HTTP 4xx error
    """

    xml_request = preset_negative_preset_shared_video.decode('UTF-8')
    response = utils.speke_v2_request(spekev2_url, xml_request.encode('UTF-8'))

    assert response.status_code != 200 and (400 <= response.status_code < 600), \
        f"If intendedTrackType with ALL is requested, there cannot be other ContentKeyUsageRule elements with " \
        f"different intendedTrackType values "
