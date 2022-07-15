import xml.etree.ElementTree as ET
import pytest
from .helpers import utils


@pytest.fixture(scope="session")
def playready_pssh_cpd_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents("test_case_1_p_v_1_a_1", utils.PRESETS_PLAYREADY)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text


@pytest.fixture(scope="session")
def widevine_pssh_cpd_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents("test_case_1_p_v_1_a_1", utils.PRESETS_WIDEVINE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text


@pytest.fixture(scope="session")
def fairplay_hls_signalingdata_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents("test_case_1_p_v_1_a_1", utils.PRESETS_FAIRPLAY)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text


def test_widevine_pssh_cpd_no_rotation(widevine_pssh_cpd_response):
    root_cpix = ET.fromstring(widevine_pssh_cpd_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')

        content_protection_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}ContentProtectionData')
        content_protection_data_string = utils.decode_b64_bytes(content_protection_data_bytes.text)
        pssh_in_cpd = ET.fromstring(content_protection_data_string)

        # Assert pssh in cpd is same as pssh box
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

        # Assert pssh in cpd is same as pssh box
        assert pssh_data_bytes.text == pssh_in_cpd.text, \
            "Content in PSSH box and the requested content in ContentProtectionData are expected to be the same"


# Validate presence of HLSSignalingData and PSSH when those elements are present in the request
def test_playready_pssh_hlssignalingdata_no_rotation(playready_pssh_cpd_response):
    root_cpix = ET.fromstring(playready_pssh_cpd_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')
        assert pssh_data_bytes.text, \
            "PSSH must not be empty"

        hls_signalling_data_elems = drm_system_element.findall('./{urn:dashif:org:cpix}HLSSignalingData')
        # Two elements are expected, one for media and other for master
        assert len(hls_signalling_data_elems) == 2, \
            "Two HLSSignalingData elements are expected for this request: media and master, received {}".format(
                hls_signalling_data_elems)

        # Check if HLSSignalingData text is present in the response
        hls_signalling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
        assert drm_system_element.find(hls_signalling_data_media).text, \
            "One HLSSignalingData element is expected to have a playlist value of media"
        hls_signalling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']"
        assert drm_system_element.find(hls_signalling_data_master).text, \
            "One HLSSignalingData element is expected to have a playlist value of master"

        received_playlist_atrrib_values = [hls_signalling_data.get('playlist') for hls_signalling_data in
                                           hls_signalling_data_elems]

        # Check both media and master attributes are present in the response
        assert all(attribute in received_playlist_atrrib_values for attribute in
                   utils.SPEKE_V2_HLS_SIGNALING_DATA_PLAYLIST_MANDATORY_ATTRIBS), \
            "Two HLSSignalingData elements, with playlist values of media and master are expected"

        str_ext_x_key = utils.parse_ext_x_key_contents(drm_system_element.find(hls_signalling_data_media).text)
        # Treat ext-x-session-key as ext-x-key for purposes of this validation
        str_ext_x_session_key = utils.parse_ext_x_session_key_contents(
            drm_system_element.find(hls_signalling_data_master).text)

        # Assert that str_ext_x_key and str_ext_x_session_key contents are present and parsed correctly
        assert str_ext_x_key.keys, \
            "EXT-X-KEY was not parsed correctly"
        assert str_ext_x_session_key.keys, \
            "EXT-X-SESSION-KEY was not parsed correctly"

        # Value of (EXT-X-SESSION-KEY) METHOD attribute MUST NOT be NONE
        assert str_ext_x_session_key.keys[0].method, \
            "EXT-X-SESSION-KEY METHOD must not be NONE"

        # If an EXT-X-SESSION-KEY is used, the values of the METHOD, KEYFORMAT, and KEYFORMATVERSIONS attributes MUST
        # match any EXT-X-KEY with the same URI value
        assert str_ext_x_key.keys[0].method == str_ext_x_session_key.keys[0].method, \
            "METHOD for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformat == str_ext_x_session_key.keys[0].keyformat, \
            "KEYFORMAT for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformatversions == str_ext_x_session_key.keys[0].keyformatversions, \
            "KEYFORMATVERSIONS for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"

        # Relaxing this requirement, this was originally added as we do not currently support different values
        # for the two signaling levels.
        # assert str_ext_x_key.keys[0].uri == str_ext_x_session_key.keys[0].uri, \
        #     "URI for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"

        assert str_ext_x_key.keys[0].keyformat == str_ext_x_session_key.keys[
            0].keyformat == utils.HLS_SIGNALING_DATA_KEYFORMAT.get("playready"), \
            f"KEYFORMAT value is expected to be com.microsoft.playready for playready"


def test_fairplay_hlssignalingdata_no_rotation(fairplay_hls_signalingdata_response):
    root_cpix = ET.fromstring(fairplay_hls_signalingdata_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')
        assert not pssh_data_bytes, \
            "PSSH must not be empty"

        hls_signalling_data_elems = drm_system_element.findall('./{urn:dashif:org:cpix}HLSSignalingData')
        # Two elements are expected, one for media and other for master
        assert len(hls_signalling_data_elems) == 2, \
            "Two HLSSignalingData elements are expected for this request: media and master, received {}".format(
                hls_signalling_data_elems)

        # Check if HLSSignalingData text is present in the response
        hls_signalling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
        assert drm_system_element.find(hls_signalling_data_media).text, \
            "One HLSSignalingData element is expected to have a playlist value of media"
        hls_signalling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']"
        assert drm_system_element.find(hls_signalling_data_master).text, \
            "One HLSSignalingData element is expected to have a playlist value of master"

        received_playlist_atrrib_values = [hls_signalling_data.get('playlist') for hls_signalling_data in
                                           hls_signalling_data_elems]

        # Check both media and master attributes are present in the response
        assert all(attribute in received_playlist_atrrib_values for attribute in
                   utils.SPEKE_V2_HLS_SIGNALING_DATA_PLAYLIST_MANDATORY_ATTRIBS), \
            "Two HLSSignalingData elements, with playlist values of media and master are expected"

        str_ext_x_key = utils.parse_ext_x_key_contents(drm_system_element.find(hls_signalling_data_media).text)
        # Treat ext-x-session-key as ext-x-key for purposes of this validation
        str_ext_x_session_key = utils.parse_ext_x_session_key_contents(
            drm_system_element.find(hls_signalling_data_master).text)

        # Assert that str_ext_x_key and str_ext_x_session_key contents are present and parsed correctly
        assert str_ext_x_key.keys, \
            "EXT-X-KEY was not parsed correctly"
        assert str_ext_x_session_key.keys, \
            "EXT-X-SESSION-KEY was not parsed correctly"

        # Value of (EXT-X-SESSION-KEY) METHOD attribute MUST NOT be NONE
        assert str_ext_x_session_key.keys[0].method, \
            "EXT-X-SESSION-KEY METHOD must not be NONE"

        # If an EXT-X-SESSION-KEY is used, the values of the METHOD, KEYFORMAT, and KEYFORMATVERSIONS attributes MUST
        # match any EXT-X-KEY with the same URI value
        assert str_ext_x_key.keys[0].method == str_ext_x_session_key.keys[0].method, \
            "METHOD for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformat == str_ext_x_session_key.keys[0].keyformat, \
            "KEYFORMAT for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformatversions == str_ext_x_session_key.keys[0].keyformatversions, \
            "KEYFORMATVERSIONS for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].uri == str_ext_x_session_key.keys[0].uri, \
            "URI for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"

        assert str_ext_x_key.keys[0].keyformat == str_ext_x_session_key.keys[
            0].keyformat == utils.HLS_SIGNALING_DATA_KEYFORMAT.get("fairplay"), \
            f"KEYFORMAT value is expected to be com.apple.streamingkeydelivery for Fairplay"
