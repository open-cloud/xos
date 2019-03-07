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

from __future__ import absolute_import
from xosgenx.jinja2_extensions import xproto_field_graph_components


def xproto_tosca_required(null, blank, default=None, modifier=None):
    # `null` is not currently considered. `blank` is deprecated.
    if (modifier == "optional") or (blank == "True") or (default is not None):
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


def xproto_fields_to_tosca_keys(fields, m):
    keys = []

    # look for one_of keys
    _one_of = xproto_field_graph_components(fields, m, "tosca_key_one_of")
    one_of = [list(i) for i in _one_of]

    # look for explicit keys
    for f in fields:
        if (
            "tosca_key" in f["options"]
            and f["options"]["tosca_key"]
            and "link" not in f
        ):
            keys.append(f["name"])
        if (
            "tosca_key" in f["options"]
            and f["options"]["tosca_key"]
            and ("link" in f and f["link"])
        ):
            keys.append("%s_id" % f["name"])
    # if not keys are specified and there is a name field, use that as key.
    if len(keys) == 0 and "name" in [f["name"] for f in fields]:
        keys.append("name")

    for of in sorted(one_of):
        # check if the field is a link, and in case add _id
        for index, f in enumerate(of):
            try:
                # FIXME: the 'field' var appears to be dead code, but exists to cause the IndexError?
                field = [  # noqa: F841
                    x for x in fields if x["name"] == f and ("link" in x and x["link"])
                ][0]
                of[index] = "%s_id" % f
            except IndexError:
                # the field is not a link
                pass

        keys.append(of)

    return keys
