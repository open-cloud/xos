
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


source /opt/xos/coreapi/tests/testconfig-chameleon.sh

# test modeldefs
curl -f --silent http://$HOSTNAME:8080/xosapi/v1/modeldefs > /dev/null
if [[ $? -ne 0 ]]; then
    echo fail modeldefs
fi

{% for object in generator.all() %}
curl -f --silent http://$HOSTNAME:8080/xosapi/v1/{{ object.app_name }}/{{ object.plural() }} > /dev/null
if [[ $? -ne 0 ]]; then
    echo fail {{ object.camel() }}
fi
{%- endfor %}

echo "okay"

