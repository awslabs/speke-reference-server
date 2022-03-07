import pytest
from .helpers import utils, speke_element_assertions
import xml.etree.ElementTree as ET


@pytest.fixture(scope="session")
def widevine_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_WIDEVINE, spekev2_url)


@pytest.fixture(scope="session")
def playready_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_PLAYREADY, spekev2_url)


@pytest.fixture(scope="session")
def fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_playready_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_WIDEVINE_PLAYREADY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_WIDEVINE_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def playready_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_PLAYREADY_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_playready_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_6_P_V_UNENC_A_2, utils.PRESETS_WIDEVINE_PLAYREADY_FAIRPLAY, spekev2_url)


def test_case_6_widevine(widevine_response):
    root_cpix = ET.fromstring(widevine_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 2, 2, 2, 0, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_playready(playready_response):
    root_cpix = ET.fromstring(playready_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 2, 2, 0, 2, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_fairplay(fairplay_response):
    root_cpix = ET.fromstring(fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 2, 2, 0, 0, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_widevine_playready(widevine_playready_response):
    root_cpix = ET.fromstring(widevine_playready_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 4, 2, 2, 2, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_widevine_fairplay(widevine_fairplay_response):
    root_cpix = ET.fromstring(widevine_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 4, 2, 2, 0, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_playready_fairplay(playready_fairplay_response):
    root_cpix = ET.fromstring(playready_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 4, 2, 0, 2, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")


def test_case_6_widevine_playready_fairplay(widevine_playready_fairplay_response):
    root_cpix = ET.fromstring(widevine_playready_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 2, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 6, 2, 2, 2, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 2)
    speke_element_assertions.validate_content_key_usage_rule_list_for_unencrypted_presets(root_cpix, "video")