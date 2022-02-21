from . import utils


def check_cpix_version(root):
    """
    Check CPIX version is 2.3 for Speke v2. It is the only version currently supported
    """
    assert float(root.get('version').strip()) == 2.3, \
        "Attribute: version value for CPIX element is expected to be 2.3"


def validate_spekev2_response_headers(root):
    """
        Check X-Speke-Version and X-Speke-User-Agent in the headers
    """

    assert root.headers.get('X-Speke-Version') == '2.0', \
        "X-Speke-Version must be 2.0"
    assert root.headers.get('X-Speke-User-Agent'), \
        "X-Speke-User-Agent must be present in the response"


def validate_root_element(root_cpix):
    """
        1. Check CPIX tag exists
        2. Check all mandatory attributes of CPIX element exist
        3. Check if 'id' is not present, as it is deprecated in Speke v2
    """
    assert root_cpix.tag == "{urn:dashif:org:cpix}CPIX", \
        "CPIX is a mandatory element"

    assert all(attribute in root_cpix.attrib for attribute in utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']), \
        f"All mandatory attributes: {utils.SPEKE_V2_GENERIC_RESPONSE_ATTRIBS_DICT['CPIX']} for CPIX element are expected in the response"

    assert 'id' not in root_cpix.attrib, \
        "id is a deprecated attribute for CPIX and it is not expected in the response for Speke V2"


def validate_mandatory_cpix_child_elements(root_cpix):
    """
    Check all required elements within CPIX exist and only one instance is found
    """
    cpix_elements_dict = utils.count_child_element_tags_for_element(root_cpix)

    assert '{urn:dashif:org:cpix}ContentKeyList' in cpix_elements_dict
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}ContentKeyList') == 1, \
        "Only one ContentKeyList element is expected"

    assert '{urn:dashif:org:cpix}DRMSystemList' in cpix_elements_dict
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}DRMSystemList') == 1, \
        "Only one DRMSystemList element is expected"

    assert '{urn:dashif:org:cpix}ContentKeyUsageRuleList' in cpix_elements_dict
    assert cpix_elements_dict.get('{urn:dashif:org:cpix}ContentKeyUsageRuleList') == 1, \
        "Only one ContentKeyUsageRuleList element is expected"


def validate_content_key_list_element(root_cpix, expected_count, expected_common_encryption_scheme):
    """
        1. Check if ContentKey list contains atleast one ContentKey element
        2. Check if the expected count of ContentKey elements match
        3. Check if the kid values are unique
        4. Check that Secret/ PlainValue elements exist
        5. Check commonEncryptionScheme value is correct/ remains unchanged
    """
    content_key_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyList')
    content_key_elements = content_key_list_element.findall('{urn:dashif:org:cpix}ContentKey')
    assert content_key_elements

    assert len(content_key_elements) == expected_count, \
        f"Exactly {expected_count} ContentKey elements are expected in this response"

    for i in range(0, len(content_key_elements)):
        if i > 0:
            assert content_key_elements[i].get('kid') != content_key_elements[i - 1].get('kid'), \
                "kid attribute values for the different ContentKey elements under ContentKeyList are expected to be " \
                "different"

        assert content_key_elements[i].find(
            './{urn:dashif:org:cpix}Data/{urn:ietf:params:xml:ns:keyprov:pskc}Secret/{'
            'urn:ietf:params:xml:ns:keyprov:pskc}PlainValue').text, \
            "PlainValue child element under Secret is expected to contain data for this request"
        assert content_key_elements[i].get('commonEncryptionScheme') == expected_common_encryption_scheme, \
            f"commonEncryptionScheme attribute for ContentKey is expected to contain the value {expected_common_encryption_scheme}"


def validate_drm_system_element_mandatory_attributes(drm_system_element):
    # Validate presence of required attributes in DRMSystem
    assert drm_system_element.get('kid'), \
        "kid is a mandatory attribute of DRMSystem"
    assert drm_system_element.get('systemId'), \
        "systemId is a mandatory attribute of DRMSystem"


def validate_drm_system_list_element(root_cpix, expected_count, expected_unique_kid_count, expected_widevine_id_count,
                                     expected_playready_system_id_count, expected_fairplay_system_id_count):
    """
        1. Check if DRMSystem list contains atleast one DRMSystem element
        2. Check if the expected count of DRMSystem elements match
        3. Check if the kid values are unique
        4. Check that each DRMSystem element contain mandatory attributes
        5. Check if expected DRM system ids are present
        6. Check if expected values are all present within the DRMSystem element
    """
    drm_system_list_element = root_cpix.find('./{urn:dashif:org:cpix}DRMSystemList')
    drm_system_elements = drm_system_list_element.findall('./{urn:dashif:org:cpix}DRMSystem')
    assert drm_system_elements

    kid_list = []

    actual_widevine_system_id_count = 0
    actual_playready_system_id_count = 0
    actual_fairplay_system_id_count = 0

    assert len(drm_system_elements) == expected_count, \
        f"Exactly {expected_count} DRMSystem elements are expected in this response"

    for drm_system_element in drm_system_elements:
        kid_list.append(drm_system_element.get('kid'))
        validate_drm_system_element_mandatory_attributes(drm_system_element)

        if drm_system_element.get('systemId') == utils.WIDEVINE_SYSTEM_ID:
            actual_widevine_system_id_count += 1
            validate_drm_system_element_widevine(drm_system_element)

        if drm_system_element.get('systemId') == utils.PLAYREADY_SYSTEM_ID:
            actual_playready_system_id_count += 1
            validate_drm_system_element_playready(drm_system_element)

        if drm_system_element.get('systemId') == utils.FAIRPLAY_SYSTEM_ID:
            actual_fairplay_system_id_count += 1
            validate_drm_system_element_fairplay(drm_system_element)

        # # Smooth streaming protection header should not be present in any request
        # smooth_streaming_protection_header_data_element = drm_system_elements[i].findall(
        #     './{urn:dashif:org:cpix}SmoothStreamingProtectionHeaderData')
        # assert not smooth_streaming_protection_header_data_element, \
        #     "SmoothStreamingProtectionHeaderData is not expected in this response"

    len_actual_unique_kid_list = len(list(set(kid_list)))
    assert expected_unique_kid_count == len_actual_unique_kid_list, \
        f"{expected_unique_kid_count} unique kid values for the number of keys requested, found: {len_actual_unique_kid_list} "

    assert (expected_widevine_id_count == actual_widevine_system_id_count
            and expected_playready_system_id_count == actual_playready_system_id_count
            and expected_fairplay_system_id_count == actual_fairplay_system_id_count)


def validate_drm_system_element_widevine(drm_system_element):
    validate_drm_system_element_mandatory_attributes(drm_system_element)

    pssh_data = drm_system_element.findall('./{urn:dashif:org:cpix}PSSH')
    assert len(pssh_data) == 1, \
        "Exactly 1 PSSH element is expected in the response"
    assert pssh_data[0].text, \
        "PSSH element is expected to contain data"

    content_protection_data = drm_system_element.findall('./{urn:dashif:org:cpix}ContentProtectionData')
    assert len(content_protection_data) == 1, \
        "Exactly 1 ContentProtectionData element is expected in the response"
    assert content_protection_data[0].text, \
        "ContentProtectionData element is expected to contain data"

    hls_signaling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
    len_hls_signaling_data_media = len(drm_system_element.findall(hls_signaling_data_media))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value media is expected in the response, found: {len_hls_signaling_data_media}"
    assert drm_system_element.find(hls_signaling_data_media).text, \
        "One HLSSignalingData element is expected to have a playlist value of media"

    hls_signaling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']"
    len_hls_signaling_data_master = len(drm_system_element.findall(hls_signaling_data_master))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value master is expected in the response, found: {len_hls_signaling_data_master}"
    assert drm_system_element.find(hls_signaling_data_master).text, \
        "One HLSSignalingData element is expected to have a playlist value of master"


def validate_drm_system_element_playready(drm_system_element):
    pssh_data = drm_system_element.findall('./{urn:dashif:org:cpix}PSSH')
    assert len(pssh_data) == 1, \
        "Exactly 1 PSSH element is expected in the response"
    assert pssh_data[0].text, \
        "PSSH element is expected to contain data"

    content_protection_data = drm_system_element.findall('./{urn:dashif:org:cpix}ContentProtectionData')
    assert len(content_protection_data) == 1, \
        "Exactly 1 ContentProtectionData element is expected in the response"
    assert content_protection_data[0].text, \
        "ContentProtectionData element is expected to contain data"

    hls_signaling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
    len_hls_signaling_data_media = len(drm_system_element.findall(hls_signaling_data_media))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value media is expected in the response, found: {len_hls_signaling_data_media}"
    assert drm_system_element.find(hls_signaling_data_media).text, \
        "One HLSSignalingData element is expected to have a playlist value of media"

    hls_signaling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']"
    len_hls_signaling_data_master = len(drm_system_element.findall(hls_signaling_data_master))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value master is expected in the response, found: {len_hls_signaling_data_master}"
    assert drm_system_element.find(hls_signaling_data_master).text, \
        "One HLSSignalingData element is expected to have a playlist value of master"


def validate_drm_system_element_fairplay(drm_system_element):
    pssh_data = drm_system_element.findall(
        './{urn:dashif:org:cpix}PSSH')
    assert not pssh_data, \
        "PSSH is not expected in this response"

    content_protection_data = drm_system_element.findall(
        './{urn:dashif:org:cpix}ContentProtectionData')
    assert not content_protection_data, \
        "ContentProtectionData is not expected in this response"

    hls_signaling_data_media = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']"
    len_hls_signaling_data_media = len(drm_system_element.findall(hls_signaling_data_media))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value media is expected in the response, found: {len_hls_signaling_data_media}"
    assert drm_system_element.find(hls_signaling_data_media).text, \
        "One HLSSignalingData element is expected to have a playlist value of media"

    hls_signaling_data_master = "{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']"
    len_hls_signaling_data_master = len(drm_system_element.findall(hls_signaling_data_master))
    assert len_hls_signaling_data_media == 1, \
        f"Exactly 1 HLS SignalingData element with playlist value master is expected in the response, found: {len_hls_signaling_data_master}"
    assert drm_system_element.find(hls_signaling_data_master).text, \
        "One HLSSignalingData element is expected to have a playlist value of master"


def validate_drm_system_id(drm_system_element, expected_system_id):
    assert drm_system_element.get('systemId') == expected_system_id, \
        f"DRM SystemID: {expected_system_id} is expected in the response and must remain unchanged" \
        f"from the request"


def validate_content_key_usage_rule_mandatory_attributes(content_key_usage_rule_element):
    # Validate presence of required attributes in DRMSystem
    assert content_key_usage_rule_element.get('kid'), \
        "kid is a mandatory attribute of ContentKeyUsageRule"
    assert content_key_usage_rule_element.get('intendedTrackType'), \
        "intendedTrackType is a mandatory attribute of ContentKeyUsageRule"


def validate_content_key_usage_rule_list_element(root_cpix, expected_count):
    """
        1. Check if ContentKeyUsageRule list contains atleast one ContentKeyUsageRule element
        2. Check if the expected count of ContentKeyUsageRule elements match
        3. Check if the kid values are unique
        4. Check that each ContentKeyUsageRule element contain mandatory attributes
        5. Check if intendedTrackType is present and are unique
        6. Check if expected values are all present within the DRMSystem element
    """
    content_key_usage_rule_list_element = root_cpix.find('./{urn:dashif:org:cpix}ContentKeyUsageRuleList')
    content_key_usage_rule_elements = content_key_usage_rule_list_element.findall('./{urn:dashif:org:cpix}ContentKeyUsageRule')
    assert content_key_usage_rule_elements

    assert len(content_key_usage_rule_elements) == expected_count, \
        f"Exactly {expected_count} ContentKeyUsageRule elements are expected in this response"

    for i in range(0, len(content_key_usage_rule_elements)):
        validate_content_key_usage_rule_mandatory_attributes(content_key_usage_rule_elements[i])

        if i > 0:
            assert content_key_usage_rule_elements[i-1].get('kid') != content_key_usage_rule_elements[i].get('kid'), \
                "kid attribute values for the different ContentKeyUsageRule are expected to be different"
            assert content_key_usage_rule_elements[0].get('intendedTrackType') != content_key_usage_rule_elements[1].get(
                'intendedTrackType'), \
                "intendedTrackType attribute values for the different ContentKeyUsageRule are expected to be different"
