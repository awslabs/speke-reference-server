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
import boto3
import hashlib
import os
import xml.etree.ElementTree as ET


# The official system ids are documented here:-
# http://dashif.org/identifiers/protection/

# HLS_AES_128_SYSTEM_ID is not an official system id
HLS_AES_128_SYSTEM_ID = '81376844-f976-481e-a84e-cc25d39b0b33'
HLS_SAMPLE_AES_SYSTEM_ID = '94ce86fb-07ff-4f43-adb8-93d2fa968ca2'
DASH_CENC_SYSTEM_ID = 'edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'
PLAYREADY_SYSTEM_ID = '9a04f079-9840-4286-ab92-e65be0885f95'

HLS_AES_128_KEY_FORMAT = ''  # 'identity'
HLS_AES_128_KEY_FORMAT_VERSIONS = ''  # '1'

HLS_SAMPLE_AES_KEY_FORMAT = 'com.apple.streamingkeydelivery'
HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS = '1'

CENC_PSSH_BOX = os.environ["CENC_PSSH_BOX"]

PLAYREADY_PROTECTION_HEADER = os.environ["PLAYREADY_PROTECTION_HEADER"]
PLAYREADY_PSSH_BOX = os.environ["PLAYREADY_PSSH_BOX"]

KEY_STRING = os.environ["KEY_STRING"]


# additions for bucket
S3_CLIENT = boto3.client('s3')
KEYSTORE_BUCKET = os.environ["KEYSTORE_BUCKET"]
KEYSTORE_URL = os.environ["KEYSTORE_URL"]


def get_client_url(client_url_prefix, content_id, kid):
    return "%s/%s/%s" % (client_url_prefix, content_id, kid)


def get_digest(*args):
    m = hashlib.md5()
    for arg in args:
        m.update(arg.encode('utf-8'))
    return m.digest()


def store_key(content_id, key_id, key_value):
    try:
        key = "{cid}/{kid}".format(cid=content_id, kid=key_id)
        S3_CLIENT.put_object(Bucket=KEYSTORE_BUCKET, Key=key, Body=key_value)
    except Exception as e:
        print(e)


class ServerResponseBuilder:
    def __init__(self, client_url_prefix, request_body):
        self.error_message = ""
        self.client_url_prefix = client_url_prefix

        ET.register_namespace("cpix", "urn:dashif:org:cpix")
        ET.register_namespace("pskc", "urn:ietf:params:xml:ns:keyprov:pskc")
        ET.register_namespace("speke", "urn:aws:amazon:com:speke")
        self.root = ET.fromstring(request_body)

    def fill_request(self):
        content_id = self.root.get("id")
        system_ids = {}

        for drm_system in self.root.findall(
                "./{urn:dashif:org:cpix}DRMSystemList/{urn:dashif:org:cpix}DRMSystem"):
            kid = drm_system.get("kid")
            system_id = drm_system.get("systemId")
            system_ids[system_id] = kid

            if system_id == HLS_AES_128_SYSTEM_ID:
                ext_x_key = get_client_url(
                    self.client_url_prefix, content_id, kid)
                drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(
                    ext_x_key.encode('utf-8')).decode('utf-8')
                drm_system.find("{urn:aws:amazon:com:speke}KeyFormat").text = base64.b64encode(
                    HLS_AES_128_KEY_FORMAT.encode('utf-8')).decode('utf-8')
                drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions").text = base64.b64encode(
                    HLS_AES_128_KEY_FORMAT_VERSIONS.encode('utf-8')).decode('utf-8')
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}ContentProtectionData"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}ProtectionHeader"))
                drm_system.remove(drm_system.find("{urn:dashif:org:cpix}PSSH"))
            elif system_id == HLS_SAMPLE_AES_SYSTEM_ID:
                ext_x_key = get_client_url(
                    self.client_url_prefix, content_id, kid)
                drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(
                    ext_x_key.encode('utf-8')).decode('utf-8')
                drm_system.find("{urn:aws:amazon:com:speke}KeyFormat").text = base64.b64encode(
                    HLS_SAMPLE_AES_KEY_FORMAT.encode('utf-8')).decode('utf-8')
                drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions").text = base64.b64encode(
                    HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS.encode('utf-8')).decode('utf-8')
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}ContentProtectionData"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}ProtectionHeader"))
                drm_system.remove(drm_system.find("{urn:dashif:org:cpix}PSSH"))
            elif system_id == DASH_CENC_SYSTEM_ID:
                # uri = get_client_url(self.client_url_prefix, content_id, kid)
                drm_system.find(
                    "{urn:dashif:org:cpix}PSSH").text = CENC_PSSH_BOX
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}ContentProtectionData"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}KeyFormat"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}ProtectionHeader"))
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}URIExtXKey"))
            elif system_id == PLAYREADY_SYSTEM_ID:
                drm_system.find(
                    "{urn:aws:amazon:com:speke}ProtectionHeader").text = PLAYREADY_PROTECTION_HEADER
                drm_system.find(
                    "{urn:dashif:org:cpix}PSSH").text = PLAYREADY_PSSH_BOX
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}ContentProtectionData"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}KeyFormat"))
                drm_system.remove(
                    drm_system.find("{urn:aws:amazon:com:speke}KeyFormatVersions"))
                drm_system.remove(
                    drm_system.find("{urn:dashif:org:cpix}URIExtXKey"))
            else:
                self.error_message = "Invalid systemId %s" % system_id
                return

        for content_key in self.root.findall(
                "./{urn:dashif:org:cpix}ContentKeyList/{urn:dashif:org:cpix}ContentKey"):
            kid = content_key.get("kid")
            iv = content_key.get("explicitIV")
            data = ET.SubElement(content_key, "{urn:dashif:org:cpix}Data")
            secret = ET.SubElement(
                data, "{urn:ietf:params:xml:ns:keyprov:pskc}Secret")
            plain_value = ET.SubElement(
                secret, "{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue")
            # base64 encoded key
            encoded_key = base64.b64encode(
                get_digest(
                    KEY_STRING,
                    content_id,
                    kid)).decode('utf-8')
            # set on XML element
            plain_value.text = encoded_key
            # store to S3 bucket
            store_key(content_id, kid, base64.b64decode(encoded_key))
            if iv is None and system_ids.get(
                    HLS_SAMPLE_AES_SYSTEM_ID, False) == kid:
                content_key.set(
                    'explicitIV',
                    base64.b64encode(
                        get_digest(
                            'too much tuna!',
                            content_id,
                            kid)).decode('utf-8'))

    def get_response(self):
        self.fill_request()
        if self.error_message:
            return {
                "isBase64Encoded": False,
                "statusCode": 500,
                "headers": {
                    "Content-Type": "text/plain"},
                "body": self.error_message}
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/xml",
                "Speke-User-Agent": "AWSElementalMockKeyServer"},
            "body": ET.tostring(
                self.root).decode('utf-8')}


class ClientResponseBuilder:
    """
    This class is not used in the S3 SPEKE solution. Use this class to generate and return a key immediately.
    """

    def __init__(self, content_id, kid):
        self.error_message = ""
        self.content_id = content_id
        self.kid = kid

    def get_response(self):
        key = get_digest(KEY_STRING, self.content_id, self.kid)
        key_base64 = base64.b64encode(key).decode('utf-8')
        if self.error_message:
            return {
                "isBase64Encoded": False,
                "statusCode": 500,
                "headers": {
                    "Content-Type": "text/plain"},
                "body": self.error_message}
        return {"isBase64Encoded": True, "statusCode": 200, "headers": {
            "Content-Type": "application/octet-stream"}, "body": key_base64}
