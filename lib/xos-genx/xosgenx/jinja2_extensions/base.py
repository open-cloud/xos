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

from __future__ import absolute_import, print_function
import pdb
import re
from jinja2.runtime import Undefined
from inflect import engine as inflect_engine_class

inflect_engine = inflect_engine_class()


class FieldNotFound(Exception):
    def __init__(self, message):
        super(FieldNotFound, self).__init__(message)


def xproto_debug(**kwargs):
    print(kwargs)
    pdb.set_trace()


def xproto_unquote(s):
    return unquote(s)


def unquote(s):
    if s and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    else:
        return s


def xproto_singularize(field):
    try:
        # The user has set a singular, as an exception that cannot be handled automatically
        singular = field["options"]["singular"]
        singular = unquote(singular)
    except KeyError:
        singular = inflect_engine.singular_noun(field["name"])
        if singular is False:
            # singular_noun returns False on a noun it can't singularize
            singular = field["name"]

    return singular


def xproto_singularize_pluralize(field):
    try:
        # The user has set a plural, as an exception that cannot be handled automatically
        plural = field["options"]["plural"]
        plural = unquote(plural)
    except KeyError:
        singular = inflect_engine.singular_noun(field["name"])
        if singular is False:
            # singular_noun returns False on a noun it can't singularize
            singular = field["name"]

        plural = inflect_engine.plural_noun(singular)

    return plural


def xproto_pluralize(field):
    try:
        # The user has set a plural, as an exception that cannot be handled automatically
        plural = field["options"]["plural"]
        plural = unquote(plural)
    except KeyError:
        plural = inflect_engine.plural_noun(field["name"])

    return plural


def xproto_base_def(model_name, base, suffix="", suffix_list=[]):
    if model_name == "XOSBase":
        return "(models.Model, PlModelMixIn)"
    elif not base:
        return ""
    else:
        int_base = [i["name"] + suffix for i in base if i["name"] in suffix_list]
        ext_base = [i["name"] for i in base if i["name"] not in suffix_list]
        return "(" + ",".join(int_base + ext_base) + ")"


def xproto_first_non_empty(lst):
    # Returns the first non-empty element in the list. Empty is interpreted to be either
    # None or the empty string or an instance of jinja2 Undefined(). The value False and the
    # string "False" are not considered empty, but are values.
    for item in lst:
        if (item is not None) and (item != "") and (not isinstance(item, Undefined)):
            return item


def xproto_api_type(field):
    try:
        if unquote(field["options"]["content_type"]) == "date":
            return "double"
    except KeyError:
        pass

    return field["type"]


def xproto_base_name(n):
    # Hack - Refactor NetworkParameter* to make this go away
    if n.startswith("NetworkParameter"):
        return "_"

    expr = r"^[A-Z]+[a-z]*"

    try:
        match = re.findall(expr, n)[0]
    except BaseException:
        return "_"

    return match


def xproto_base_fields(m, table):
    fields = []

    for b in m["bases"]:
        option1 = b["fqn"]
        try:
            option2 = m["package"] + "." + b["name"]
        except TypeError:
            option2 = option1

        accessor = None
        if option1 in table:
            accessor = option1
        elif option2 in table:
            accessor = option2

        if accessor:
            base_fields = xproto_base_fields(table[accessor], table)

            model_fields = [x.copy() for x in table[accessor]["fields"]]
            for field in model_fields:
                field["accessor"] = accessor

            fields.extend(base_fields)
            fields.extend(model_fields)

    if "no_sync" in m["options"] and m["options"]["no_sync"]:
        fields = [
            f
            for f in fields
            if f["name"] != "backend_status" and f["name"] != "backend_code"
        ]

    if "no_policy" in m["options"] and m["options"]["no_policy"]:
        fields = [
            f
            for f in fields
            if f["name"] != "policy_status" and f["name"] != "policy_code"
        ]

    return fields


def xproto_fields(m, table):
    """ Generate the full list of models for the xproto message `m` including fields from the classes it inherits.

        Inserts the special field "id" at the very beginning.

        Each time we descend a new level of inheritance, increment the offset field numbers by 100. The base
        class's fields will be numbered from 1-99, the first descendant will be number 100-199, the second
        descdendant numbered from 200-299, and so on. This assumes any particular model as at most 100
        fields.
    """

    model_fields = [x.copy() for x in m["fields"]]
    for field in model_fields:
        field["accessor"] = m["fqn"]

    fields = xproto_base_fields(m, table) + model_fields

    # The "id" field is a special field. Every model has one. Put it up front and pretend it's part of the

    if not fields:
        raise Exception(
            "Model %s has no fields. Check for missing base class." % m["name"]
        )

    id_field = {
        "type": "int32",
        "name": "id",
        "options": {},
        "id": "1",
        "accessor": fields[0]["accessor"],
    }

    fields = [id_field] + fields

    # Walk through the list of fields. They will be in depth-first search order from the base model forward. Each time
    # the model changes, offset the protobuf field numbers by 100.
    offset = 0
    last_accessor = fields[0]["accessor"]
    for field in fields:
        if field["accessor"] != last_accessor:
            last_accessor = field["accessor"]
            offset += 100
        field_id = int(field["id"])
        if (field_id < 1) or (field_id >= 100):
            raise Exception(
                "Only field numbers from 1 to 99 are permitted, field %s in model %s"
                % (field["name"], field["accessor"])
            )
        field["id"] = int(field["id"]) + offset

    # Check for duplicates
    fields_by_number = {}
    for field in fields:
        id = field["id"]
        dup = fields_by_number.get(id)
        if dup:
            raise Exception(
                "Field %s has duplicate number %d with field %s in model %s"
                % (field["name"], id, dup["name"], field["accessor"])
            )
        fields_by_number[id] = field

    return fields


def xproto_base_rlinks(m, table):
    links = []

    for base in m["bases"]:
        b = base["name"]
        if b in table:
            base_rlinks = xproto_base_rlinks(table[b], table)

            model_rlinks = [x.copy() for x in table[b]["rlinks"]]
            for link in model_rlinks:
                link["accessor"] = b

            links.extend(base_rlinks)
            links.extend(model_rlinks)

    return links


def xproto_rlinks(m, table):
    """ Return the reverse links for the xproto message `m`.

        If the link includes a reverse_id, then it will be used for the protobuf field id. Each level of inheritance
        will add an offset of 100 to the supplied reverse_id.

        If there is no reverse_id, then one will automatically be allocated started at id 1900. It is encouraged that
        all links include reverse_ids, so that field identifiers are deterministic across all protobuf messages.
    """

    model_rlinks = [x.copy() for x in m["rlinks"]]
    for link in model_rlinks:
        link["accessor"] = m["fqn"]

    links = xproto_base_rlinks(m, table) + model_rlinks

    links = [
        x for x in links if ("+" not in x["src_port"]) and ("+" not in x["dst_port"])
    ]

    if links:
        last_accessor = links[0]["accessor"]
        offset = 0
        index = 1900
        for link in links:
            if link["accessor"] != last_accessor:
                last_accessor = link["accessor"]
                offset += 100

            if link["reverse_id"]:
                # Statically numbered reverse links. Use the id that the developer supplied, adding the offset based on
                # inheritance depth.
                link["id"] = int(link["reverse_id"]) + offset
            else:
                # Automatically numbered reverse links. These will eventually go away.
                link["id"] = index
                index += 1

        # check for duplicates
        links_by_number = {}
        for link in links:
            id = link["id"]
            dup = links_by_number.get(id)
            if dup:
                raise Exception(
                    "Field %s has duplicate number %d in model %s with reverse field %s"
                    % (link["src_port"], id, m["name"], dup["src_port"])
                )
            links_by_number[id] = link

    return links


def xproto_base_links(m, table):
    links = []

    for base in m["bases"]:
        b = base["name"]
        if b in table:
            base_links = xproto_base_links(table[b], table)

            model_links = table[b]["links"]
            links.extend(base_links)
            links.extend(model_links)
    return links


def xproto_string_type(xptags):
    if "text" not in xptags:
        # String fields have a mandatory maximum length.
        # They are intended for relatively short strings.
        return "string"
    else:
        # Text fields have an optional maximuim length.
        # They are intended for long, potentially multiline strings.
        return "text"


def xproto_tuplify(nested_list_or_set):
    if not isinstance(nested_list_or_set, list) and not isinstance(
        nested_list_or_set, set
    ):
        return nested_list_or_set
    else:
        return tuple([xproto_tuplify(i) for i in nested_list_or_set])


def xproto_field_graph_components(fields, model, tag="unique_with"):
    """
    NOTE: Don't use set theory operators if you want repeatable tests - many
    of them have non-deterministic behavior
    """

    def find_components(graph):

        # 'graph' dict structure:
        #   - keys are strings
        #   - values are sets containing strings that are names of other keys in 'graph'

        # take keys from 'graph' dict and put in 'pending' set
        pending = set(graph.keys())

        # create an empty list named 'components'
        components = []

        # loop while 'pending' is true - while there are still items in the 'pending' set
        while pending:

            # remove a random item from pending set, and put in 'front'
            # this is the primary source of nondeterminism
            front = {pending.pop()}

            # create an empty set named 'component'
            component = set()

            # loop while 'front' is true. Front is modified below
            while front:

                # take the (only?) item out of the 'front' dict, and put in 'node'
                node = front.pop()

                # from 'graph' dict take set with key of 'node' and put into 'neighbors'
                neighbours = graph[node]

                # remove the set of items in components from neighbors
                neighbours -= component  # These we have already visited

                # add all remaining neighbors to front
                front |= neighbours

                # remove neighbors from pending
                pending -= neighbours

                # add neighbors to component
                component |= neighbours

            # append component set to components list, sorted
            components.append(sorted(component))

        # return 'components', which is a list of sets
        return sorted(components)

    field_graph = {}
    field_names = {f["name"] for f in fields}

    for f in fields:
        try:
            tagged_str = unquote(f["options"][tag])
            tagged_fields = tagged_str.split(",")

            for uf in tagged_fields:
                if uf not in field_names:
                    raise FieldNotFound(
                        'Field "%s" not found in model "%s", referenced from field "%s" by option "%s"'
                        % (uf, model["name"], f["name"], tag)
                    )

                field_graph.setdefault(f["name"], set()).add(uf)
                field_graph.setdefault(uf, set()).add(f["name"])

        except KeyError:
            pass

    return find_components(field_graph)


def xproto_api_opts(field):
    options = []
    if "max_length" in field["options"] and field["type"] == "string":
        options.append("(val).maxLength = %s" % field["options"]["max_length"])

    if field["options"].get("feedback_state"):
        options.append("(feedbackState) = true")

    if field["options"].get("gui_hidden"):
        options.append("(guiHidden) = true")

    if field["options"].get("bookkeeping_state"):
        options.append("(bookkeepingState) = true")

    try:
        if field["options"]["null"] == "False":
            options.append("(val).nonNull = true")
    except KeyError:
        pass

    if "link" in field and "model" in field["options"]:
        options.append('(foreignKey).modelName = "%s"' % field["options"]["model"])
        if ("options" in field) and ("port" in field["options"]):
            options.append(
                '(foreignKey).reverseFieldName = "%s"' % field["options"]["port"]
            )

    if options:
        options_str = "[" + ", ".join(options) + "]"
    else:
        options_str = ""

    return options_str


def xproto_type_to_swagger_type(f):
    try:
        content_type = f["options"]["content_type"]
        content_type = eval(content_type)
    except BaseException:
        content_type = None
        pass

    if "choices" in f["options"]:
        return "string"
    elif content_type == "date":
        return "string"
    elif f["type"] == "bool":
        return "boolean"
    elif f["type"] == "string":
        return "string"
    elif f["type"] in ["int", "uint32", "int32"] or "link" in f:
        return "integer"
    elif f["type"] in ["double", "float"]:
        return "string"


def xproto_field_to_swagger_enum(f):
    if "choices" in f["options"]:
        c_list = []

        for c in eval(xproto_unquote(f["options"]["choices"])):
            c_list.append(c[0])

        return sorted(c_list)
    else:
        return False


def xproto_is_true(x):
    # TODO: Audit xproto and make specification of trueness more uniform
    if x is True or (x == "True") or (x == '"True"'):
        return True
    return False


def xproto_list_evaluates_true(lst):
    # Returns True if the first non-empty item in the list is interpreted
    # as True.
    x = xproto_first_non_empty(lst)
    return xproto_is_true(x)
