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

from key_server_common import ServerResponseBuilder


def server_handler(event, context):
    print(event)
    client_url_prefix = os.environ["KEYSTORE_URL"]
    body = event['body']
    if event['isBase64Encoded']:
        body = base64.b64decode(body)
    r = ServerResponseBuilder(client_url_prefix, body)
    response = r.get_response()
    print(response)
    return response
