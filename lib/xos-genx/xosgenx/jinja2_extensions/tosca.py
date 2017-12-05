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

def xproto_tosca_required(null, blank, default=None):

    if null == 'True' or blank == 'True' or default != 'False':
        return "false"
    return "true"

def xproto_tosca_field_type(type):
    """
    TOSCA requires fields of type 'bool' to be 'boolean'
    TOSCA requires fields of type 'int32' to be 'integer'
    """

    if type == "bool":
        return "boolean"
    elif type == "int32":
        return "integer"
    else:
        return type

def xproto_fields_to_tosca_keys(fields):
	keys = []
	# look for explicit keys
	for f in fields:
		if 'tosca_key' in f['options'] and f['options']['tosca_key'] and 'link' not in f:
			keys.append(f['name'])
		if 'tosca_key' in f['options'] and f['options']['tosca_key'] and ('link' in f and f['link']):
			keys.append("%s_id" % f['name'])
	# if not keys are specified and there is a name field, use that as key.
	if len(keys) == 0 and 'name' in map(lambda f: f['name'], fields):
		keys.append('name')
	return keys