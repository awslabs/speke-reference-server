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

# date stamp for this deploy
STAMP=`date +%s`
echo build stamp is $STAMP

# clear the build folder
rm -f $BUILD/*

# create the reference server zip with a unique name
SERVZIP=speke-reference-lambda-$STAMP.zip
cd $ORIGIN/src
# using zappa for help in packaging
zappa package --output $BUILD/$SERVZIP

# create the custom resource zip with a unique name
RESZIP=cloudformation-resources-$STAMP.zip
cd $ORIGIN/cloudformation
zip -r $BUILD/$RESZIP mediapackage_endpoint_common.py mediapackage_speke_endpoint.py resource_tools.py

# update templates with the new zip filenames
sed -e "s/DEV_0_0_0/$STAMP/g" speke_reference.json >$BUILD/speke_reference.json
sed -e "s/DEV_0_0_0/$STAMP/g" mediapackage_speke_endpoint.json >$BUILD/mediapackage_speke_endpoint.json

cd $BUILD

# regional buckets hosting the pre-built cloudformation templates and resources

# primary bucket
aws s3 sync . s3://rodeolabz-us-west-2/speke --acl public-read --delete

# sync'd buckets
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-ap-northeast-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-ap-northeast-2/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-ap-south-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-ap-southeast-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-ap-southeast-2/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-eu-central-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-eu-west-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-eu-west-3/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-sa-east-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-us-east-1/speke --acl public-read --delete
aws s3 sync s3://rodeolabz-us-west-2/speke s3://rodeolabz-us-west-1/speke --acl public-read --delete

cd $ORIGIN
