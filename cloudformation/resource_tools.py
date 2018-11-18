"""
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from botocore.vendored import requests
import boto3
import json
import string
import random
import re
import time


def send(event, context, response_status, response_data, physical_resource_id):
    response_url = event['ResponseURL']
    response_body = {
        'Status': response_status,
        'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
        'PhysicalResourceId': physical_resource_id or context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': response_data
    }
    json_response_body = json.dumps(response_body)
    print("Response body:\n" + json_response_body)
    headers = {'content-type': '', 'content-length': str(len(json_response_body))}
    try:
        response = requests.put(response_url, data=json_response_body, headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("EXCEPTION {}".format(e))
    return


def stack_name(event):
    try:
        response = event['ResourceProperties']['StackName']
    except Exception:
        response = None
    return response


def wait_for_channel_states(medialive, channel_id, states):
    current_state = ''
    while current_state not in states:
        time.sleep(5)
        current_state = medialive.describe_channel(ChannelId=channel_id)['State']
    return current_state


def wait_for_input_states(medialive, input_id, states):
    current_state = ''
    while current_state not in states:
        time.sleep(5)
        current_state = medialive.describe_input(InputId=input_id)['State']
    return current_state
