#!/bin/sh

# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# regional buckets hosting the pre-built cloudformation templates
# use us-west-2 as source bucket

aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-ap-northeast-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-ap-northeast-2/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-ap-south-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-ap-southeast-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-ap-southeast-2/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-eu-central-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-eu-west-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-eu-west-3/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-sa-east-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-us-east-1/speke/ --acl public-read
aws s3 sync s3://rodeolabz-us-west-2/speke/ s3://rodeolabz-us-west-1/speke/ --acl public-read
