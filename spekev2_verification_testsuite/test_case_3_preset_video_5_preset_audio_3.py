import pytest
from .helpers import utils, speke_element_assertions
import xml.etree.ElementTree as ET


@pytest.fixture(scope="session")
def widevine_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_WIDEVINE, spekev2_url)


@pytest.fixture(scope="session")
def playready_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_PLAYREADY, spekev2_url)


@pytest.fixture(scope="session")
def fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_playready_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_WIDEVINE_PLAYREADY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_WIDEVINE_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def playready_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_PLAYREADY_FAIRPLAY, spekev2_url)


@pytest.fixture(scope="session")
def widevine_playready_fairplay_response(spekev2_url):
    return utils.send_speke_request(utils.TEST_CASE_3_P_V_5_A_3, utils.PRESETS_WIDEVINE_PLAYREADY_FAIRPLAY, spekev2_url)


def test_case_3_widevine(widevine_response):
    root_cpix = ET.fromstring(widevine_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 8, 8, 8, 0, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_playready(playready_response):
    root_cpix = ET.fromstring(playready_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 8, 8, 0, 8, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_fairplay(fairplay_response):
    root_cpix = ET.fromstring(fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 8, 8, 0, 0, 8)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_widevine_playready(widevine_playready_response):
    root_cpix = ET.fromstring(widevine_playready_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cenc")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 16, 8, 8, 8, 0)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_widevine_fairplay(widevine_fairplay_response):
    root_cpix = ET.fromstring(widevine_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 16, 8, 8, 0, 8)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_playready_fairplay(playready_fairplay_response):
    root_cpix = ET.fromstring(playready_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 16, 8, 0, 8, 8)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)


def test_case_3_widevine_playready_fairplay(widevine_playready_fairplay_response):
    root_cpix = ET.fromstring(widevine_playready_fairplay_response)

    speke_element_assertions.check_cpix_version(root_cpix)
    speke_element_assertions.validate_root_element(root_cpix)
    speke_element_assertions.validate_mandatory_cpix_child_elements(root_cpix)
    speke_element_assertions.validate_content_key_list_element(root_cpix, 8, "cbcs")
    speke_element_assertions.validate_drm_system_list_element(root_cpix, 24, 8, 8, 8, 8)
    speke_element_assertions.validate_content_key_usage_rule_list_element(root_cpix, 8)
