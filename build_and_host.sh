#!/bin/sh

# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

ORIGIN=`pwd`
BUILD=$ORIGIN/build

rm -f $BUILD/*

ZIP=speke-reference-lambda.zip

cd $ORIGIN/src
# using zappa for help in packaging
zappa package --output $BUILD/$ZIP

ZIP=cloudformation-resources.zip

cd $ORIGIN/cloudformation
cp *.json $BUILD
zip -r $BUILD/$ZIP mediapackage_endpoint_common.py mediapackage_speke_endpoint.py resource_tools.py

cd $BUILD

# regional buckets hosting the pre-built cloudformation templates

aws s3 sync . s3://rodeolabz-ap-northeast-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-ap-northeast-2/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-ap-south-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-ap-southeast-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-ap-southeast-2/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-eu-central-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-eu-west-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-eu-west-3/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-sa-east-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-us-east-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-us-west-1/speke/ --acl public-read --delete
aws s3 sync . s3://rodeolabz-us-west-2/speke/ --acl public-read --delete

cd $ORIGIN
