import pytest
from .helpers import utils, speke_element_assertions
import xml.etree.ElementTree as ET

elements_to_remove = [
    "{urn:dashif:org:cpix}ContentKey",
    "{urn:dashif:org:cpix}DRMSystem",
    "{urn:dashif:org:cpix}ContentKeyUsageRule"
]

video_kid = [
    "cff143cc-f7ba-4f45-b7dc-11e789c70c1c",
    "acd5dbee-1b29-451c-9125-4dbb7fd3f4b2"
]

audio_kid = [
    "faa20e04-b929-4959-85f7-3c2788cce887",
    "3aa729cd-b693-4377-960d-bd0c3c217897"
]


@pytest.fixture(scope="session")
def widevine_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_WIDEVINE)


@pytest.fixture(scope="session")
def playready_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_PLAYREADY)


@pytest.fixture(scope="session")
def fairplay_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_FAIRPLAY)


@pytest.fixture(scope="session")
def widevine_playready_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_WIDEVINE_PLAYREADY)


@pytest.fixture(scope="session")
def widevine_fairplay_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_WIDEVINE_FAIRPLAY)


@pytest.fixture(scope="session")
def playready_fairplay_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_PLAYREADY_FAIRPLAY)


@pytest.fixture(scope="session")
def widevine_playready_fairplay_response(spekev2_url):
    return utils.read_xml_file_contents(utils.TEST_CASE_5_6_P_V_2_A_2, utils.PRESETS_WIDEVINE_PLAYREADY_FAIRPLAY)


def test_case_5_widevine_preset_video_2_audio_unencrypted(widevine_response, spekev2_url):
    xml_request = widevine_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           audio_kid)


    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 2, 2, 2, 0, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the audio kid values are not present in the response
    assert response.text.find(audio_kid[0]) == -1 and response.text.find(audio_kid[1]) == -1


def test_case_5_widevine_playready_preset_video_2_audio_unencrypted(widevine_playready_response, spekev2_url):
    xml_request = widevine_playready_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           audio_kid)
    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 4, 2, 2, 2, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the audio kid values are not present in the response
    assert response.text.find(audio_kid[0]) == -1 and response.text.find(audio_kid[1]) == -1


def test_case_5_widevine_playready_fairplay_preset_video_2_audio_unencrypted(widevine_playready_fairplay_response, spekev2_url):
    xml_request = widevine_playready_fairplay_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           audio_kid)
    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 6, 2, 2, 2, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the audio kid values are not present in the response
    assert response.text.find(audio_kid[0]) == -1 and response.text.find(audio_kid[1]) == -1


def test_case_6_widevine_video_unencrypted_preset_audio_2(widevine_response, spekev2_url):
    xml_request = widevine_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           video_kid)
    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 2, 2, 2, 0, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the video kid values are not present in the response
    assert response.text.find(video_kid[0]) == -1 and response.text.find(video_kid[1]) == -1


def test_case_6_widevine_playready_video_unencrypted_preset_audio_2(widevine_playready_response, spekev2_url):
    xml_request = widevine_playready_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           video_kid)
    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 4, 2, 2, 2, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the video kid values are not present in the response
    assert response.text.find(video_kid[0]) == -1 and response.text.find(video_kid[1]) == -1


def test_case_6_widevine_playready_fairplay_video_unencrypted_preset_audio_2(widevine_playready_fairplay_response, spekev2_url):
    xml_request = widevine_playready_fairplay_response.decode('UTF-8')
    response = utils.send_modified_speke_request_with_matching_elements_kid_values_removed(spekev2_url,
                                                                                           xml_request.encode("UTF-8"),
                                                                                           elements_to_remove,
                                                                                           video_kid)
    root_cpix = ET.fromstring(response.text)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 6, 2, 2, 2, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)

    # Check the video kid values are not present in the response
    assert response.text.find(video_kid[0]) == -1 and response.text.find(video_kid[1]) == -1