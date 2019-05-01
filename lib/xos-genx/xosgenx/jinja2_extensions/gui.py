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
from .base import xproto_string_type, unquote


def xproto_type_to_ui_type(f):
    try:
        content_type = f["options"]["content_type"]
        content_type = eval(content_type)
    except BaseException:
        content_type = None
        pass

    if "choices" in f["options"]:
        return "select"
    elif content_type == "date":
        return "date"
    elif f["type"] == "bool":
        return "boolean"
    elif f["type"] == "string":
        return xproto_string_type(f["options"])
    elif f["type"] in ["int", "uint32", "int32"] or "link" in f:
        return "number"
    elif f["type"] in ["double", "float"]:
        return "string"


def xproto_options_choices_to_dict(choices):
    list = []

    for c in eval(choices):
        list.append({"id": c[0], "label": c[1]})
    if len(list) > 0:
        return list
    else:
        return None


def xproto_dict_to_sorted_string(d):
    """
    sorts the dict by key and returns a string representation, which makes
    for better consistency when testing
    """
    ft = []  # formatted tuples
    for k, v in sorted(d.items(), key=lambda t: t[0]):  # sorted by key
        if v is not None:
            ft.append("'%s': '%s'" % (k, v))
        else:
            ft.append("'%s': None" % k)
    return "{%s}" % ", ".join(ft)


def xproto_validators(f):

    # To be cleaned up when we formalize validation in xproto
    validators = []

    # bound-based validators
    bound_validators = [("max_length", "maxlength"), ("min", "min"), ("max", "max")]

    for v0, v1 in bound_validators:
        try:
            validators.append({"name": v1, "int_value": int(f["options"][v0])})
        except KeyError:
            pass

    # validators based on content_type
    content_type_validators = ["ip", "url", "email"]

    for v in content_type_validators:
        # if f['name']=='ip': pdb.set_trace()
        try:
            val = unquote(f["options"]["content_type"]) == v
            if not val:
                raise KeyError

            validators.append({"name": v, "bool_value": True})
        except KeyError:
            pass

    # required validator
    try:
        required = f["modifier"] == "required"
        if required:
            validators.append({"name": "required", "bool_value": required})
    except KeyError:
        pass

    return validators


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def xproto_default_to_gui(default):
    # TODO: Using `eval` here is potentially dangerous as it may allow code injection
    val = "null"
    try:
        if is_number(default):
            val = str(default)
        elif eval(default) is True:
            val = "true"
        elif eval(default) is False:
            val = "false"
        elif eval(default) is None:
            val = "null"
        else:
            val = str(default)
    except NameError:
        # val was a function call, and we can't pass those to the GUI
        val = "null"

    return val


def xproto_links_to_modeldef_relations(llst):
    outlist = []
    seen = []
    for l in llst:
        try:
            t = l["link_type"]
        except KeyError as e:
            raise e

        if l["peer"]["fqn"] not in seen and t != "manytomany":
            on_field = "null"
            if l["link_type"] == "manytoone":
                on_field = l["src_port"]
            elif l["link_type"] == "onetomany":
                on_field = l["dst_port"]
            outlist.append(
                "{model: %s, type: %s, on_field: %s}"
                % (l["peer"]["name"], l["link_type"], on_field)
            )
        seen.append(l["peer"])

    return outlist
