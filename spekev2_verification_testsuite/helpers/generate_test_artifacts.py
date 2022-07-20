import os
import shutil
import uuid
import xml.etree.ElementTree as ET
from . import utils

ns = {"cpix": "urn:dashif:org:cpix", "pksc": "urn:ietf:params:xml:ns:keyprov:pskc"}
ET.register_namespace('cpix', ns["cpix"])


def generate_key_id_list(num_keys):
    return [str(uuid.uuid4()) for _ in range(num_keys)]


def generate_random_content_id():
    return str("test_case_") + str(uuid.uuid4())


def generate_random_key_period_id():
    return str("keyPeriod_") + str(uuid.uuid4())


def add_xmlns_attrib_to_root(root, ns):
    if not ET.iselement(root):
        root = root.getroot()
    for prefix, uri in ns.items():
        if prefix != "cpix":
            root.attrib['xmlns:' + prefix] = uri


class TestFileGenerator:
    """
    Clean up existing test resources before each run
    Generate new test resources
    """
    test_artifacts_folder_name = "spekev2_requests"
    test_case_folders = [
        utils.TEST_CASE_1_P_V_1_A_1,
        utils.TEST_CASE_2_P_V_3_A_2,
        utils.TEST_CASE_3_P_V_5_A_3,
        utils.TEST_CASE_4_P_V_8_A_2,
        utils.TEST_CASE_5_P_V_2_A_UNENC,
        utils.TEST_CASE_6_P_V_UNENC_A_2
    ]
    test_file_names = [
        utils.PRESETS_WIDEVINE,
        utils.PRESETS_PLAYREADY,
        utils.PRESETS_FAIRPLAY,
        utils.PRESETS_WIDEVINE_PLAYREADY,
        utils.PRESETS_WIDEVINE_FAIRPLAY,
        utils.PRESETS_PLAYREADY_FAIRPLAY,
        utils.PRESETS_WIDEVINE_PLAYREADY_FAIRPLAY
    ]
    num_keys = 1
    intended_track_types = []
    common_encryption_scheme = "cbcs"
    key_period_id = "Key_Period_1"
    cpix_root = None

    def generate_artifacts(self, is_vod_suite=False):
        self.cleanup_before_run()
        self.create_folders()
        self.create_files(is_vod_suite)

    def create_folders(self):
        if os.path.isdir(self.test_artifacts_folder_name):
            folder_to_create = ""
            try:
                for folder in self.test_case_folders:
                    folder_to_create = str(self.test_artifacts_folder_name + "/" + folder)
                    if not os.path.isdir(folder_to_create):
                        os.makedirs(folder_to_create)
            except OSError as e:
                print("Error: %s : %s" % (folder_to_create, e.strerror))

    def create_files(self, is_vod_suite):
        for folder in self.test_case_folders:
            self.key_period_id = generate_random_key_period_id()
            if folder == utils.TEST_CASE_1_P_V_1_A_1:
                self.num_keys = 2
                self.intended_track_types = ["VIDEO", "AUDIO"]
            elif folder == utils.TEST_CASE_2_P_V_3_A_2:
                self.num_keys = 5
                self.intended_track_types = ["SD", "HD", "UHD", "STEREO_AUDIO", "MULTICHANNEL_AUDIO"]
            elif folder == utils.TEST_CASE_3_P_V_5_A_3:
                self.num_keys = 8
                self.intended_track_types = ["SD", "HD1", "HD2", "UHD1", "UHD2", "STEREO_AUDIO",
                                             "MULTICHANNEL_AUDIO_3_6", "MULTICHANNEL_AUDIO_7"]
            elif folder == utils.TEST_CASE_4_P_V_8_A_2:
                self.num_keys = 6
                self.intended_track_types = ["SD+HD1", "HD2", "UHD1", "UHD2", "STEREO_AUDIO",
                                             "MULTICHANNEL_AUDIO"]
            elif folder == utils.TEST_CASE_5_P_V_2_A_UNENC:
                self.num_keys = 2
                self.intended_track_types = ["SD", "HD"]
            elif folder == utils.TEST_CASE_6_P_V_UNENC_A_2:
                self.num_keys = 2
                self.intended_track_types = ["STEREO_AUDIO", "MULTICHANNEL_AUDIO"]

            for file in self.test_file_names:
                key_ids = generate_key_id_list(self.num_keys)
                self.generate_test_content(file, key_ids, is_vod_suite)
                self.generate_file(folder, file)

    def cleanup_before_run(self):
        print("Deleting test case folders (if already present) and recreating them")
        if os.path.isdir(self.test_artifacts_folder_name):
            folder_to_delete = ""
            try:
                for folder in self.test_case_folders:
                    folder_to_delete = str(self.test_artifacts_folder_name + "/" + folder)
                    if os.path.isdir(folder_to_delete):
                        shutil.rmtree(folder_to_delete)
                    else:
                        print(f"Folder to delete: {folder_to_delete} is not present")
            except OSError as e:
                print("Error: %s : %s" % (folder_to_delete, e.strerror))

    def generate_file(self, folder, file):
        file_name_with_path = self.get_file_name_and_path(folder, file)
        ET.indent(self.cpix_root, space="\t", level=0)
        ET.ElementTree(self.cpix_root).write(file_name_with_path, xml_declaration=True, encoding="utf-8")

    def generate_test_content(self, file_name, key_ids, is_vod_suite):
        """
        Generate xml contents for different test cases
        """

        self.cpix_root = None

        system_ids = []
        self.common_encryption_scheme = "cenc"

        # widevine
        if file_name == utils.PRESETS_WIDEVINE:
            system_ids.append(utils.WIDEVINE_SYSTEM_ID)

        # playready
        elif file_name == utils.PRESETS_PLAYREADY:
            system_ids.append(utils.PLAYREADY_SYSTEM_ID)

        # fairplay
        elif file_name == utils.PRESETS_FAIRPLAY:
            system_ids.append(utils.FAIRPLAY_SYSTEM_ID)
            self.common_encryption_scheme = "cbcs"

        # widevine + playready
        elif file_name == utils.PRESETS_WIDEVINE_PLAYREADY:
            system_ids.append(utils.WIDEVINE_SYSTEM_ID)
            system_ids.append(utils.PLAYREADY_SYSTEM_ID)

        # widevine + fairplay
        elif file_name == utils.PRESETS_WIDEVINE_FAIRPLAY:
            system_ids.append(utils.WIDEVINE_SYSTEM_ID)
            system_ids.append(utils.FAIRPLAY_SYSTEM_ID)
            self.common_encryption_scheme = "cbcs"

        # playready + fairplay
        elif file_name == utils.PRESETS_PLAYREADY_FAIRPLAY:
            system_ids.append(utils.PLAYREADY_SYSTEM_ID)
            system_ids.append(utils.FAIRPLAY_SYSTEM_ID)
            self.common_encryption_scheme = "cbcs"

        # widevine + playready + fairplay
        elif file_name == utils.PRESETS_WIDEVINE_PLAYREADY_FAIRPLAY:
            system_ids.append(utils.WIDEVINE_SYSTEM_ID)
            system_ids.append(utils.PLAYREADY_SYSTEM_ID)
            system_ids.append(utils.FAIRPLAY_SYSTEM_ID)
            self.common_encryption_scheme = "cbcs"

        self.generate_root()
        self.generate_content_key_list(key_ids)
        self.generate_drm_system_list(system_ids, key_ids)
        # See https://docs.aws.amazon.com/speke/latest/documentation/vod-workflow-method-v2.html for more details about VOD requests
        if not is_vod_suite:
            self.generate_content_key_period_list()
        self.generate_content_key_usage_rule_list(key_ids, is_vod_suite)

    def generate_root(self):
        root_attribs = {"contentId": generate_random_content_id(), "version": "2.3"}
        self.cpix_root = ET.Element(ET.QName(ns["cpix"], "CPIX"), root_attribs)
        add_xmlns_attrib_to_root(self.cpix_root, ns)

    def generate_content_key_list(self, key_ids):
        content_key_list = ET.SubElement(self.cpix_root, ET.QName(ns["cpix"], "ContentKeyList"))
        for k_id in key_ids:
            content_key_attribs = {"kid": k_id, "commonEncryptionScheme": self.common_encryption_scheme}
            ET.SubElement(content_key_list, ET.QName(ns["cpix"], "ContentKey"), content_key_attribs)

    def generate_drm_system_list(self, system_ids, key_ids):
        drm_system_list = ET.SubElement(self.cpix_root, ET.QName(ns["cpix"], "DRMSystemList"))
        for s_id in system_ids:
            for k_id in key_ids:
                drm_system_attribs = {"kid": k_id, "systemId": s_id}
                drm_system = ET.SubElement(drm_system_list, ET.QName(ns["cpix"], "DRMSystem"), drm_system_attribs)

                # Generate PSSH element
                ET.SubElement(drm_system, ET.QName(ns["cpix"], "PSSH"))

                # Generate ContentProtectionData element except for Fairplay
                if s_id != utils.FAIRPLAY_SYSTEM_ID:
                    ET.SubElement(drm_system, ET.QName(ns["cpix"], "ContentProtectionData"))

                # Generate HLSSignalingData element
                for playlist in ["media", "master"]:
                    hls_signaling_data_sttribs = {"playlist": playlist}
                    ET.SubElement(drm_system, ET.QName(ns["cpix"], "HLSSignalingData"), hls_signaling_data_sttribs)

    def generate_content_key_period_list(self):
        content_key_period_list = ET.SubElement(self.cpix_root, ET.QName(ns["cpix"], "ContentKeyPeriodList"))
        content_key_period_attribs = {"id": self.key_period_id, "index": "0"}
        ET.SubElement(content_key_period_list, ET.QName(ns["cpix"], "ContentKeyPeriod"), content_key_period_attribs)

    def generate_content_key_usage_rule_list(self, key_ids, is_vod_suite):
        content_key_usage_rule_list = ET.SubElement(self.cpix_root, ET.QName(ns["cpix"], "ContentKeyUsageRuleList"))
        for num, k_id in enumerate(key_ids):
            content_key_usage_rule_attribs = {"kid": k_id, "intendedTrackType": self.intended_track_types[num]}
            content_key_usage_rule = ET.SubElement(content_key_usage_rule_list,
                                                   ET.QName(ns["cpix"], "ContentKeyUsageRule"),
                                                   content_key_usage_rule_attribs)
            if not is_vod_suite:
                key_period_filter_attribs = {"periodId": self.key_period_id}
                ET.SubElement(content_key_usage_rule, ET.QName(ns["cpix"], "KeyPeriodFilter"),
                              key_period_filter_attribs)

            filter_name = "VideoFilter"
            if "AUDIO" in self.intended_track_types[num]:
                filter_name = "AudioFilter"

            filter_attribs = self.generate_filter_attribs(self.intended_track_types[num])
            ET.SubElement(content_key_usage_rule, ET.QName(ns["cpix"], filter_name), filter_attribs)

    def generate_filter_attribs(self, intended_track_type_value):
        if intended_track_type_value == "STEREO_AUDIO":
            filter_attribs = {"maxChannels": "2"}
        elif intended_track_type_value == "MULTICHANNEL_AUDIO":
            filter_attribs = {"minChannels": "3"}
        elif intended_track_type_value == "MULTICHANNEL_AUDIO_3_6":
            filter_attribs = {"minChannels": "3", "maxChannels": "6"}
        elif intended_track_type_value == "MULTICHANNEL_AUDIO_7":
            filter_attribs = {"minChannels": "7"}
        elif intended_track_type_value == "SD":
            filter_attribs = {"maxPixels": "589824"}
        elif intended_track_type_value == "HD":
            filter_attribs = {"minPixels": "589825"}
        elif intended_track_type_value == "HD1":
            filter_attribs = {"minPixels": "589825", "maxPixels": "921600"}
        elif intended_track_type_value == "HD2":
            filter_attribs = {"minPixels": "921601", "maxPixels": "2073600"}
        elif intended_track_type_value == "SD+HD1":
            filter_attribs = {"maxPixels": "921600"}
        elif intended_track_type_value == "UHD":
            filter_attribs = {"minPixels": "2073601"}
        elif intended_track_type_value == "UHD1":
            filter_attribs = {"minPixels": "2073601", "maxPixels": "8847360"}
        elif intended_track_type_value == "UHD2":
            filter_attribs = {"minPixels": "8847361"}
        else:
            filter_attribs = {}

        return filter_attribs

    def get_file_path(self, folder_name):
        return str(self.test_artifacts_folder_name + "/" + folder_name)

    def get_file_name_and_path(self, folder_name, file_name):
        return str(self.get_file_path(folder_name) + "/" + file_name)
