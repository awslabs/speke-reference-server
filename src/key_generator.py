"""
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import hashlib
# import secrets

import boto3
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class KeyGenerator:
    """
    This class is responsible for symmetric key generation. Different
    functions are provided to generate keys. This class also manages the
    secret data used by each content ID in key generation.
    """

    def __init__(self):
        self.backend = default_backend()
        self.content_id_secret_length = 64
        self.derived_key_iterations = 5000
        self.derived_key_size = 16
        self.keyed_hash_digest_size = 16
        self.local_secret_folder = "/tmp"
        self.secrets_client = boto3.client('secretsmanager')

    def md5_key(self, secret, kid):
        """
        Generate a key using an MD5 digest function
        """
        md5 = hashlib.md5()
        md5.update(secret.encode('utf-8'))
        md5.update(kid.encode('utf-8'))
        return md5.digest()

    def blake2b_key(self, secret, kid):
        """
        Generate a key using the Blake2B variable-length digest function
        """
        blake_hash = hashlib.blake2b(digest_size=self.keyed_hash_digest_size)
        blake_hash.update(secret.encode('utf-8'))
        blake_hash.update(kid.encode('utf-8'))
        return blake_hash.digest()

    def derived_key(self, secret, kid):
        """
        Generate a key using a key derivation function (default)
        """
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=self.derived_key_size, salt=secret.encode('utf-8'), iterations=self.derived_key_iterations, backend=self.backend)
        return kdf.derive(kid.encode('utf-8'))

    def local_secret_path(self, content_id):
        """
        Create a path for a content ID secret file stored locally in the Lambda filesystem
        """
        return '{}/speke.{}'.format(self.local_secret_folder, content_id)

    def store_local_secret(self, content_id, secret):
        """
        Store a content ID secret file
        """
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, 'w')
        secret_file.write(secret)
        secret_file.close()

    def retrieve_local_secret(self, content_id):
        """
        Retrieve a content ID secret file
        """
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, 'r')
        secret = secret_file.read()
        secret_file.close()
        return secret

    def generate_content_id_secret(self):
        """
        Create a string of random text used in generating a key for a content ID/key ID
        """
        # return secrets.token_hex(self.content_id_secret_length)
        return self.secrets_client.get_random_password(PasswordLength=self.content_id_secret_length)['RandomPassword']

    def retrieve_content_id_secret(self, content_id):
        """
        Retrieve the secret value by content ID used for generating keys
        """
        try:
            # cached locally?
            secret = self.retrieve_local_secret(content_id)
            print("CACHED-SECRET {}".format(content_id))
        except IOError:
            # try secrets manager
            secret_id = "speke/{}".format(content_id)
            try:
                response = self.secrets_client.get_secret_value(SecretId=secret_id)
                secret = response['SecretString']
                self.store_local_secret(content_id, secret)
                print("RETRIEVE-SECRET {}".format(content_id))
            except ClientError as error:
                if error.response['Error']['Code'] == 'ResourceNotFoundException':
                    # we need a new secret value
                    print("CREATE-SECRET {}".format(content_id))
                    secret = self.generate_content_id_secret()
                    self.secrets_client.create_secret(Name=secret_id, SecretString=secret, Description='SPEKE content ID secret value for key generation')
                    self.store_local_secret(content_id, secret)
                else:
                    # we're done trying
                    raise error
        return secret

    def key(self, content_id, key_id):
        """
        Return a symmetric key based on a content ID and key ID
        """
        return self.derived_key(self.retrieve_content_id_secret(content_id), key_id)
