#!/bin/sh

# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

find . -iname '*.py' -print0 | \
xargs -0 yapf -i --style='{based_on_style: pep8, join_multiple_lines: true, column_limit: 200, indent_width: 4}'
