"""
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import base64
import os
import xml.etree.ElementTree as element_tree
import secrets
import uuid

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# HLS_AES_128_SYSTEM_ID is not an official system ID
HLS_AES_128_SYSTEM_ID = '81376844-f976-481e-a84e-cc25d39b0b33'
HLS_SAMPLE_AES_SYSTEM_ID = '94ce86fb-07ff-4f43-adb8-93d2fa968ca2'
COMMON_PSSH_SYSTEM_ID = '1077efec-c0b2-4d02-ace3-3c1e52e2fb4b'
DASH_CENC_SYSTEM_ID = 'edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'
PLAYREADY_SYSTEM_ID = '9a04f079-9840-4286-ab92-e65be0885f95'
CLEAR_KEY_AES_128_SYSTEM_ID = '3ea8778f-7742-4bf9-b18b-e834b2acbd47'

# settings for HLS
HLS_AES_128_KEY_FORMAT = ''  # 'identity'
HLS_AES_128_KEY_FORMAT_VERSIONS = '1'  # '1'
HLS_SAMPLE_AES_KEY_FORMAT = 'com.apple.streamingkeydelivery'
HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS = '1'
# speke v2.0 settings for fairplay drm
FAIRPLAY_HLS_SIGNALING_DATA_MEDIA = os.environ["FAIRPLAY_HLS_SIGNALING_DATA_MEDIA"]
FAIRPLAY_HLS_SIGNALING_DATA_MASTER = os.environ["FAIRPLAY_HLS_SIGNALING_DATA_MASTER"]

# settings for widevine drm
WIDEVINE_PSSH_BOX = os.environ["WIDEVINE_PSSH_BOX"]
WIDEVINE_PROTECTION_HEADER = os.environ["WIDEVINE_PROTECTION_HEADER"]
# speke v2.0 settings for widevine drm
WIDEVINE_CONTENT_PROTECTION_DATA = os.environ["WIDEVINE_CONTENT_PROTECTION_DATA"]
WIDEVINE_HLS_SIGNALING_DATA_MEDIA = os.environ["WIDEVINE_HLS_SIGNALING_DATA_MEDIA"]
WIDEVINE_HLS_SIGNALING_DATA_MASTER = os.environ["WIDEVINE_HLS_SIGNALING_DATA_MASTER"]

# settings for playready drm
PLAYREADY_PSSH_BOX = os.environ["PLAYREADY_PSSH_BOX"]
PLAYREADY_PROTECTION_HEADER = os.environ["PLAYREADY_PROTECTION_HEADER"]
PLAYREADY_CONTENT_KEY = os.environ["PLAYREADY_CONTENT_KEY"]
# speke v2.0 settings for playready drm
PLAYREADY_CONTENT_PROTECTION_DATA = os.environ["PLAYREADY_CONTENT_PROTECTION_DATA"]
PLAYREADY_HLS_SIGNALING_DATA_MEDIA = os.environ["PLAYREADY_HLS_SIGNALING_DATA_MEDIA"]
PLAYREADY_HLS_SIGNALING_DATA_MASTER = os.environ["PLAYREADY_HLS_SIGNALING_DATA_MASTER"]

# globals for encrypted document responses
DOCUMENT_KEY_SIZE = 32
HMAC_KEY_SIZE = 64
RANDOM_IV_SIZE = 16


class ServerResponseBuilder:
    """
    This class is responsible generating and returning the
    XML document response to the requesting encryptor
    """

    def __init__(self, request_body, cache, generator):
        self.error_message = ""
        self.cache = cache
        self.generator = generator
        self.root = element_tree.fromstring(request_body)
        self.document_key = None
        self.hmac_key = None
        self.public_key = None
        self.use_playready_content_key = False
        element_tree.register_namespace("cpix", "urn:dashif:org:cpix")
        element_tree.register_namespace("pskc", "urn:ietf:params:xml:ns:keyprov:pskc")
        element_tree.register_namespace("speke", "urn:aws:amazon:com:speke")
        element_tree.register_namespace("ds", "http://www.w3.org/2000/09/xmldsig#")
        element_tree.register_namespace("enc", "http://www.w3.org/2001/04/xmlenc#")

    def fixup_document(self, drm_system, system_id, content_id, kid):
        """
        Update the returned XML document based on the specified system ID
        """
        if system_id.lower() == HLS_AES_128_SYSTEM_ID.lower():
            ext_x_key = self.cache.url(content_id, kid)
            drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(ext_x_key.encode('utf-8')).decode('utf-8')
            drm_system.find("{urn:aws:amazon:com:speke}KeyFormat").text = base64.b64encode(HLS_AES_128_KEY_FORMAT.encode('utf-8')).decode('utf-8')
            drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions").text = base64.b64encode(HLS_AES_128_KEY_FORMAT_VERSIONS.encode('utf-8')).decode('utf-8')
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
        elif system_id.lower() == HLS_SAMPLE_AES_SYSTEM_ID.lower():
            ext_x_key = self.cache.url(content_id, kid)
            drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(ext_x_key.encode('utf-8')).decode('utf-8')
            drm_system.find("{urn:aws:amazon:com:speke}KeyFormat").text = base64.b64encode(HLS_SAMPLE_AES_KEY_FORMAT.encode('utf-8')).decode('utf-8')
            drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions").text = base64.b64encode(HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS.encode('utf-8')).decode('utf-8')
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
        elif system_id.lower() == COMMON_PSSH_SYSTEM_ID.lower():
            pssh = bytearray([
                # BMFF box header(52 bytes, 'pssh')
                0x00, 0x00, 0x00, 0x34, 0x70, 0x73, 0x73, 0x68,
                0x01, 0x00, 0x00, 0x00,  # Full box header(version=1, flags=0)
                0x10, 0x77, 0xef, 0xec, 0xc0, 0xb2, 0x4d, 0x02,  # SystemID
                0xac, 0xe3, 0x3c, 0x1e, 0x52, 0xe2, 0xfb, 0x4b,
                0x00, 0x00, 0x00, 0x01,  # KID_count(1)
                # First KID("0123456789012345")
                0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35,
                0x00, 0x00, 0x00, 0x00,  # Size of Data(0)
            ])
            pssh[32:48] = uuid.UUID(kid).bytes
            base64pssh = base64.b64encode(pssh).decode('utf-8')
            drm_system.find(
                "{urn:dashif:org:cpix}PSSH").text = base64pssh
            content_protection_data = '<pssh xmlns="urn:mpeg:cenc:2013">' + base64pssh + '</pssh>'
            drm_system.find(
                "{urn:dashif:org:cpix}ContentProtectionData").text = base64.b64encode(content_protection_data.encode('utf-8')).decode('utf-8')
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}KeyFormat")
            self.safe_remove(
                drm_system, "{urn:aws:amazon:com:speke}KeyFormatVersions")
            self.safe_remove(
                drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}URIExtXKey")
        elif system_id.lower() == DASH_CENC_SYSTEM_ID.lower():
            drm_system.find("{urn:dashif:org:cpix}PSSH").text = WIDEVINE_PSSH_BOX
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}KeyFormat")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}KeyFormatVersions")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}URIExtXKey")
        elif system_id.lower() == PLAYREADY_SYSTEM_ID.lower():
            drm_system.find("{urn:aws:amazon:com:speke}ProtectionHeader").text = PLAYREADY_PROTECTION_HEADER
            drm_system.find("{urn:dashif:org:cpix}PSSH").text = PLAYREADY_PSSH_BOX
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}KeyFormat")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}KeyFormatVersions")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}URIExtXKey")
            self.use_playready_content_key = True
        else:
            raise Exception("Invalid system ID {}".format(system_id))

    def get_content_id(self):
        return self.root.get("id")

    def fill_request(self):
        """
        Fill the XML document with data about the requested keys.
        """
        content_id = self.get_content_id()
        # self.use_playready_content_key = False
        system_ids = {}
        # check whether to perform CPIX 2.0 document encryption
        encrypted_response_recipients = self.root.findall("./{urn:dashif:org:cpix}DeliveryDataList/{urn:dashif:org:cpix}DeliveryData")
        if encrypted_response_recipients:
            print("ENCRYPTED-RESPONSE")
            # generate a random document key and HMAC key
            self.document_key = secrets.token_bytes(DOCUMENT_KEY_SIZE)
            self.hmac_key = secrets.token_bytes(HMAC_KEY_SIZE)
            backend = default_backend()
            for delivery_data in encrypted_response_recipients:
                delivery_key = delivery_data.find("./{urn:dashif:org:cpix}DeliveryKey")
                x509data = delivery_key.find("./{http://www.w3.org/2000/09/xmldsig#}X509Data")
                x509cert = x509data.find("./{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
                cert = x509.load_der_x509_certificate(base64.b64decode(x509cert.text), backend)
                public_key = cert.public_key()
                self.public_key = x509cert.text
                asym_padder = asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)
                # encrypt the document and HMAC keys using the x509 public key
                encoded_document_key = public_key.encrypt(self.document_key, asym_padder)
                encoded_hmac_key = public_key.encrypt(self.hmac_key, asym_padder)
                # insert document key
                document_key_leaf = element_tree.SubElement(delivery_data, "{urn:dashif:org:cpix}DocumentKey")
                document_key_leaf.set("Algorithm", "http://www.w3.org/2001/04/xmlenc#aes256-cbc")
                data_leaf = element_tree.SubElement(document_key_leaf, "{urn:dashif:org:cpix}Data")
                secret_leaf = element_tree.SubElement(data_leaf, "{urn:ietf:params:xml:ns:keyprov:pskc}Secret")
                self.insert_encrypted_value(secret_leaf, "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p", base64.b64encode(encoded_document_key).decode('utf-8'))
                # insert HMAC key
                mac_method = element_tree.SubElement(delivery_data, "{urn:dashif:org:cpix}MACMethod")
                mac_method.set("Algorithm", "http://www.w3.org/2001/04/xmldsig-more#hmac-sha512")
                mac_method_key = element_tree.SubElement(mac_method, "{urn:dashif:org:cpix}Key")
                self.insert_encrypted_value(mac_method_key, "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p", base64.b64encode(encoded_hmac_key).decode('utf-8'))
        else:
            print("CLEAR-RESPONSE")

        for drm_system in self.root.findall("./{urn:dashif:org:cpix}DRMSystemList/{urn:dashif:org:cpix}DRMSystem"):
            kid = drm_system.get("kid")
            system_id = drm_system.get("systemId")
            system_ids[system_id] = kid
            print("SYSTEM-ID {}".format(system_id.lower()))
            self.fixup_document(drm_system, system_id, content_id, kid)

        for content_key in self.root.findall("./{urn:dashif:org:cpix}ContentKeyList/{urn:dashif:org:cpix}ContentKey"):
            kid = content_key.get("kid")
            init_vector = content_key.get("explicitIV")
            data = element_tree.SubElement(content_key, "{urn:dashif:org:cpix}Data")
            secret = element_tree.SubElement(data, "{urn:ietf:params:xml:ns:keyprov:pskc}Secret")
            # HLS SAMPLE AES Only
            if init_vector is None and system_ids.get(HLS_SAMPLE_AES_SYSTEM_ID, False) == kid:
                content_key.set('explicitIV', base64.b64encode(self.generator.key(content_id, kid)).decode('utf-8'))
            # generate the key
            key_bytes = self.generator.key(content_id, kid)
            # store to the key in the cache
            self.cache.store(content_id, kid, key_bytes)
            # log
            print("NEW-KEY {} {}".format(content_id, kid))
            # update the encrypted response
            if encrypted_response_recipients:
                # store the key encrypted
                padder = padding.PKCS7(algorithms.AES.block_size).padder()
                padded_data = padder.update(key_bytes) + padder.finalize()
                random_iv = secrets.token_bytes(RANDOM_IV_SIZE)
                cipher = Cipher(algorithms.AES(self.document_key), modes.CBC(random_iv), backend=backend)
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                cipher_data = random_iv + encrypted_data
                encrypted_string = base64.b64encode(cipher_data).decode('utf-8')
                self.insert_encrypted_value(secret, "http://www.w3.org/2001/04/xmlenc#aes256-cbc", encrypted_string)
            else:
                plain_value = element_tree.SubElement(secret, "{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue")
                # PLAYREADY ONLY
                if self.use_playready_content_key:
                    plain_value.text = PLAYREADY_CONTENT_KEY
                else:
                    plain_value.text = base64.b64encode(key_bytes).decode('utf-8')

    def get_response(self):
        """
        Get the key request response as an HTTP response.
        """
        self.fill_request()
        if self.error_message:
            return {"isBase64Encoded": False, "statusCode": 500, "headers": {"Content-Type": "text/plain"}, "body": self.error_message}
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/xml",
                "Speke-User-Agent": "SPEKE Reference Server (https://github.com/awslabs/speke-reference-server)"
            },
            "body": element_tree.tostring(self.root).decode('utf-8')
        }

    def insert_encrypted_value(self, element, encryption_algorithm, encrypted_string):
        """
        Add an encrypted value (key) to the document.
        """
        encrypted_value = element_tree.SubElement(element, "{urn:ietf:params:xml:ns:keyprov:pskc}EncryptedValue")
        encryption_method = element_tree.SubElement(encrypted_value, "{http://www.w3.org/2001/04/xmlenc#}EncryptionMethod")
        encryption_method.set("Algorithm", encryption_algorithm)
        cipher_data = element_tree.SubElement(encrypted_value, "{http://www.w3.org/2001/04/xmlenc#}CipherData")
        cipher_value = element_tree.SubElement(cipher_data, "{http://www.w3.org/2001/04/xmlenc#}CipherValue")
        cipher_value.text = encrypted_string
        # calculate and set MAC using HMAC-SHA512 over data in CipherValue
        if not self.hmac_key:
            raise Exception("Missing HMAC key")
        value_mac = element_tree.SubElement(element, "{urn:ietf:params:xml:ns:keyprov:pskc}ValueMAC")
        hmac_instance = hmac.HMAC(self.hmac_key, hashes.SHA512(), backend=default_backend())
        hmac_instance.update(base64.b64decode(encrypted_string))
        value_mac.text = base64.b64encode(hmac_instance.finalize()).decode('utf-8')

    def safe_remove(self, element, match):
        """
        Helper to remove an element only if it exists.
        """
        if element.find(match):
            element.remove(match)

class ServerResponseBuilderV2(ServerResponseBuilder):
    def get_content_id(self):
        return self.root.get("contentId")

    def fixup_document(self, drm_system, system_id, content_id, kid):
        """
        Update the returned XML document based on the specified system ID
        """
        # DRMSystem for WIDEVINE_SYSTEM_ID
        if system_id.lower() == DASH_CENC_SYSTEM_ID.lower():
            pssh_box = drm_system.find("{urn:dashif:org:cpix}PSSH")
            if pssh_box is not None:
                pssh_box.text = WIDEVINE_PSSH_BOX
            
            content_protection_data = drm_system.find("{urn:dashif:org:cpix}ContentProtectionData")
            if content_protection_data is not None:
                content_protection_data.text = WIDEVINE_CONTENT_PROTECTION_DATA

            hls_signalling_data_elems = drm_system.findall("{urn:dashif:org:cpix}HLSSignalingData")
            if hls_signalling_data_elems:
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']").text = WIDEVINE_HLS_SIGNALING_DATA_MEDIA
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']").text = WIDEVINE_HLS_SIGNALING_DATA_MASTER

        # DRMSystem for PLAYREADY_SYSTEM_ID
        elif system_id.lower() == PLAYREADY_SYSTEM_ID.lower():
            pssh_box = drm_system.find("{urn:dashif:org:cpix}PSSH")
            if pssh_box is not None:
                pssh_box.text = PLAYREADY_PSSH_BOX

            content_protection_data = drm_system.find("{urn:dashif:org:cpix}ContentProtectionData")
            if content_protection_data is not None:
                content_protection_data.text = PLAYREADY_CONTENT_PROTECTION_DATA
            
            hls_signalling_data_elems = drm_system.findall("{urn:dashif:org:cpix}HLSSignalingData")
            if hls_signalling_data_elems:
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']").text = PLAYREADY_HLS_SIGNALING_DATA_MEDIA
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']").text = PLAYREADY_HLS_SIGNALING_DATA_MASTER
            
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}SmoothStreamingProtectionHeaderData")
            self.use_playready_content_key = True

        # DRMSystem for FAIRPLAY_SYSTEM_ID
        elif system_id.lower() == HLS_SAMPLE_AES_SYSTEM_ID.lower():
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}SmoothStreamingProtectionHeaderData")
            hls_signalling_data_elems = drm_system.findall("{urn:dashif:org:cpix}HLSSignalingData")
            if hls_signalling_data_elems:
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']").text = FAIRPLAY_HLS_SIGNALING_DATA_MEDIA
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']").text = FAIRPLAY_HLS_SIGNALING_DATA_MASTER

        elif system_id.lower() == CLEAR_KEY_AES_128_SYSTEM_ID.lower():
            ext_x_key_uri = self.cache.url(content_id, kid)
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}SmoothStreamingProtectionHeaderData")

            ext_x_session_key, ext_x_key = self.clearkey_aes_128_hls_signaling_data(ext_x_key_uri)

            hls_signalling_data_elems = drm_system.findall("{urn:dashif:org:cpix}HLSSignalingData")
            if hls_signalling_data_elems:
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='media']").text = ext_x_key
                drm_system.find("{urn:dashif:org:cpix}HLSSignalingData[@playlist='master']").text = ext_x_session_key

        else:
            raise Exception("Invalid system ID {}".format(system_id))

    def get_response(self):
        """
        Get the key request response as an HTTP response.
        """
        self.fill_request()
        if self.error_message:
            return {"isBase64Encoded": False, "statusCode": 500, "headers": {"Content-Type": "text/plain"}, "body": self.error_message}
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/xml",
                "X-Speke-User-Agent": "SPEKE Reference Server (https://github.com/awslabs/speke-reference-server)",
                "X-Speke-Version": "2.0"
            },
            "body": element_tree.tostring(self.root).decode('utf-8')
        }

    def clearkey_aes_128_hls_signaling_data(self, ext_x_key_uri):
        method = "AES-128"
        uri = ext_x_key_uri
        key_format = HLS_AES_128_KEY_FORMAT
        key_format_versions = HLS_AES_128_KEY_FORMAT_VERSIONS

        # need to fix
        ext_x_session_key = '#EXT-X-SESSION-KEY:METHOD={},URI="{}",KEYFORMAT="{}",KEYFORMATVERSIONS="{}"'.format(method, uri, key_format, key_format_versions)
        ext_x_key = '#EXT-X-KEY:METHOD={},URI="{}",KEYFORMAT="{}",KEYFORMATVERSIONS="{}"'.format(method, uri, key_format, key_format_versions)

        encoded_session_key = base64.b64encode(ext_x_session_key.encode('utf-8')).decode('utf-8')
        encoded_key = base64.b64encode(ext_x_key.encode('utf-8')).decode('utf-8')

        return encoded_session_key, encoded_key
