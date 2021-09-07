import base64
import copy
import xml.etree.ElementTree as ET
import pytest
import requests
from . import utils

import m3u8


@pytest.fixture(scope="session")
def playready_pssh_hlssignallingdata_response(spekev2_url):
    test_request_data = utils.read_xml_file_contents(utils.PLAYREADY_PSSH_HLSSIGNALINGDATA_TEST_FILE)
    response = utils.speke_v2_request(spekev2_url, test_request_data)
    return response.text

# Validate presence of HLSSignalingData and PSSH when those elements are present in the request
def test_cmaf_playready_pssh_hlssignallingdata_no_rotation(playready_pssh_hlssignallingdata_response):
    root_cpix = ET.fromstring(playready_pssh_hlssignallingdata_response)
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')

    for drm_system_element in drm_system_elements:
        pssh_data_bytes = drm_system_element.find('./{urn:dashif:org:cpix}PSSH')
        assert pssh_data_bytes.text, \
        "PSSH must not be empty"
        
        hls_signalling_data_elems = drm_system_element.findall('./{urn:dashif:org:cpix}HLSSignalingData')
        # Two elements are expected, one for media and other for master
        assert len(hls_signalling_data_elems) == 2, \
        "Two HLSSignalingData elements are expected for this request: media and master, received {}".format(hls_signalling_data_elems)

        # Check if HLSSignalingData text is present in the response
        hls_signalling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
        assert drm_system_element.find(hls_signalling_data_media).text, \
        "One HLSSignalingData element is expected to have a playlist value of media"
        hls_signalling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
        assert drm_system_element.find(hls_signalling_data_master).text, \
        "One HLSSignalingData element is expected to have a playlist value of master"

        received_playlist_atrrib_values = [hls_signalling_data.get('playlist') for hls_signalling_data in hls_signalling_data_elems]

        # Check both media and master attribs are present in the response
        assert all(attribute in received_playlist_atrrib_values for attribute in utils.SPEKE_V2_HLS_SIGNALING_DATA_PLAYLIST_MANDATORY_ATTRIBS), \
        "Two HLSSignalingData elements, with playlist values of media and master are expected"
        
        str_ext_x_key = utils.parse_ext_x_key_contents(drm_system_element.find(hls_signalling_data_media).text)
        # Treat ext-x-session-key as ext-x-key for purposes of this validation
        str_ext_x_session_key = utils.parse_ext_x_session_key_contents(drm_system_element.find(hls_signalling_data_master).text)

        # Assert that str_ext_x_key and str_ext_x_session_key contents are present and parsed correctly
        assert str_ext_x_key.keys, \
        "EXT-X-KEY was not parsed correctly"
        assert str_ext_x_session_key.keys, \
        "EXT-X-SESSION-KEY was not parsed correctly"

        #Value of (EXT-X-SESSION-KEY) METHOD attribute MUST NOT be NONE
        assert str_ext_x_session_key.keys[0].method, \
        "EXT-X-SESSION-KEY METHOD must not be NONE"

        # If an EXT-X-SESSION-KEY is used, the values of the METHOD, KEYFORMAT, and KEYFORMATVERSIONS attributes MUST match any EXT-X-KEY with the same URI value
        assert str_ext_x_key.keys[0].method == str_ext_x_session_key.keys[0].method, \
        "METHOD for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformat == str_ext_x_session_key.keys[0].keyformat, \
        "KEYFORMAT for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].keyformatversions == str_ext_x_session_key.keys[0].keyformatversions, \
        "KEYFORMATVERSIONS for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
        assert str_ext_x_key.keys[0].uri == str_ext_x_session_key.keys[0].uri, \
        "URI for #EXT-X-KEY and EXT-X-SESSION-KEY must match for this request"
