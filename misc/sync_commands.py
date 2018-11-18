#!/usr/bin/env python
"""
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import boto3

# this is a tool to generate all the s3 sync commands for mediapackage regions

bucket_base = "rodeolabz"
mediapackage_regions = boto3.session.Session().get_available_regions(service_name='mediapackage')

for region in mediapackage_regions:
    print("aws s3 sync . s3://rodeolabz-{region}/speke/ --delete".format(region=region))
