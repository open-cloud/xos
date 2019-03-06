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

import copy
import sys

import plyxproto.model as m
from plyxproto.helpers import Visitor
from six.moves import map, range


class MissingPolicyException(Exception):
    pass


def find_missing_policy_calls(name, policies, policy):
    if isinstance(policy, dict):
        (k, lst), = policy.items()
        if k == "policy":
            policy_name = lst[0]
            if policy_name not in policies:
                raise MissingPolicyException(
                    "Policy %s invoked missing policy %s" % (name, policy_name)
                )
        else:
            for p in lst:
                find_missing_policy_calls(name, policies, p)
    elif isinstance(policy, list):
        for p in lst:
            find_missing_policy_calls(name, policies, p)


def dotname_to_fqn(dotname):
    b_names = [part.pval for part in dotname]
    package = ".".join(b_names[:-1])
    name = b_names[-1]
    if package:
        fqn = package + "." + name
    else:
        fqn = name
    return {"name": name, "fqn": fqn, "package": package}


def dotname_to_name(dotname):
    b_names = [part.pval for part in dotname]
    return ".".join(b_names)


def count_messages(body):
    count = 0
    for e in body:
        if isinstance(e, m.MessageDefinition):
            count += 1
    return count


def count_fields(body):
    count = 0
    for e in body:
        if type(e) in [m.LinkDefinition, m.FieldDefinition, m.LinkSpec]:
            count += 1
    return count


def name_to_value(obj):
    try:
        value = obj.value.value.pval
    except AttributeError:
        try:
            value = obj.value.value
        except AttributeError:
            value = obj.value.pval

    return value


class Stack(list):
    def push(self, x):
        self.append(x)


""" XOS2Jinja overrides the underlying visitor pattern to transform the tree
    in addition to traversing it """


class XOS2Jinja(Visitor):
    def __init__(self, args):
        super(XOS2Jinja, self).__init__()

        self.stack = Stack()
        self.models = {}
        self.options = {}
        self.package = None
        self.message_options = {}
        self.count_stack = Stack()
        self.policies = {}
        self.content = ""
        self.offset = 0
        self.current_message_name = None
        self.verbose = 0
        self.first_field = True
        self.first_method = True
        self.args = args

    def visit_PolicyDefinition(self, obj):
        if self.package:
            pname = ".".join([self.package, obj.name.value.pval])
        else:
            pname = obj.name.value.pval

        self.policies[pname] = obj.body
        find_missing_policy_calls(pname, self.policies, obj.body)

        return True

    def visit_PackageStatement(self, obj):
        dotlist = obj.name.value
        dotlist2 = [f.pval for f in dotlist]
        dotstr = ".".join(dotlist2)
        self.package = dotstr
        return True

    def visit_ImportStatement(self, obj):
        """Ignore"""
        return True

    def visit_OptionStatement(self, obj):
        if not hasattr(obj, "mark_for_deletion"):
            if self.current_message_name:
                self.message_options[obj.name.value.pval] = obj.value.value.pval
            else:
                self.options[obj.name.value.pval] = obj.value.value.pval

        return True

    def visit_LU(self, obj):
        return True

    def visit_default(self, obj):
        return True

    def visit_FieldDirective(self, obj):
        return True

    def visit_FieldDirective_post(self, obj):

        try:
            name = obj.name.value.pval
        except AttributeError:
            name = obj.name.value

        if isinstance(obj.value, list):
            value = dotname_to_name(obj.value)
        else:
            value = name_to_value(obj)

        self.stack.push([name, value])
        return True

    def visit_FieldType(self, obj):
        """
        Field type, if type is name, then it may need refactoring consistent
        with refactoring rules according to the table
        """
        return True

    def visit_LinkDefinition(self, obj):
        s = {}

        try:
            s["link_type"] = obj.link_type.pval
        except AttributeError:
            s["link_type"] = obj.link_type

        s["src_port"] = obj.src_port.value.pval
        s["name"] = obj.src_port.value.pval
        try:
            s["policy"] = obj.policy.pval
        except AttributeError:
            s["policy"] = None

        try:
            s["dst_port"] = obj.dst_port.value.pval
        except AttributeError:
            s["dst_port"] = obj.dst_port

        if isinstance(obj.through, list):
            s["through"] = dotname_to_fqn(obj.through)
        else:
            try:
                s["through"] = obj.through.pval
            except AttributeError:
                s["through"] = obj.through

        if isinstance(obj.name, list):
            s["peer"] = dotname_to_fqn(obj.name)
        else:
            try:
                s["peer"] = obj.name.pval
            except AttributeError:
                s["peer"] = obj.name

        try:
            s["reverse_id"] = obj.reverse_id.pval
        except AttributeError:
            s["reverse_id"] = obj.reverse_id

        s["_type"] = "link"
        s["options"] = {"modifier": "optional"}

        self.stack.push(s)
        return True

    def visit_FieldDefinition(self, obj):
        self.count_stack.push(len(obj.fieldDirective))
        return True

    def visit_FieldDefinition_post(self, obj):
        s = {}

        if isinstance(obj.ftype, m.Name):
            s["type"] = obj.ftype.value
        else:
            s["type"] = obj.ftype.name.pval

        s["name"] = obj.name.value.pval

        try:
            s["policy"] = obj.policy.pval
        except AttributeError:
            s["policy"] = None

        s["modifier"] = obj.field_modifier.pval
        s["id"] = obj.fieldId.pval

        opts = {"modifier": s["modifier"]}
        n = self.count_stack.pop()
        for i in range(0, n):
            k, v = self.stack.pop()

            # The two lines below may be added to eliminate "" around an option.
            # Right now, this is handled in targets. FIXME
            #
            # if (v.startswith('"') and v.endswith('"')):
            #    v = v[1:-1]

            opts[k] = v

        s["options"] = opts
        try:
            last_link = self.stack[-1]["_type"]
            if last_link == "link":
                s["link"] = True
        except BaseException:
            pass
        s["_type"] = "field"
        s["_linespan"] = obj.linespan

        self.stack.push(s)
        return True

    def visit_EnumFieldDefinition(self, obj):
        if self.verbose > 4:
            print("\tEnumField: name=%s, %s" % (obj.name, obj))

        return True

    def visit_EnumDefinition(self, obj):
        """New enum definition, refactor name"""
        if self.verbose > 3:
            print("Enum, [%s] body=%s\n\n" % (obj.name, obj.body))

        return True

    def visit_MessageDefinition(self, obj):
        self.current_message_name = obj.name.value.pval
        self.message_options = {}
        self.count_stack.push(count_fields(obj.body))
        return True

    def visit_MessageDefinition_post(self, obj):
        stack_num = self.count_stack.pop()
        fields = []
        links = []
        last_field = {}
        try:
            obj.bases = list(map(dotname_to_fqn, obj.bases))
        except AttributeError:
            pass

        for i in range(0, stack_num):
            f = self.stack.pop()
            if f["_type"] == "link":
                f["options"] = {
                    i: d[i] for d in [f["options"], last_field["options"]] for i in d
                }
                assert last_field == fields[0]
                fields[0].setdefault("options", {})["link_type"] = f["link_type"]
                links.insert(0, f)
            else:
                fields.insert(0, f)
                last_field = f

        if self.package:
            model_name = ".".join([self.package, obj.name.value.pval])
        else:
            model_name = obj.name.value.pval

        model_def = {
            "name": obj.name.value.pval,
            "fields": fields,
            "links": links,
            "bases": obj.bases,
            "options": self.message_options,
            "package": self.package,
            "fqn": model_name,
            "rlinks": [],
            "_linespan": obj.linespan,       # first and last line number
        }
        try:
            model_def["policy"] = obj.policy.pval
        except AttributeError:
            model_def["policy"] = None

        self.stack.push(model_def)

        self.models[model_name] = model_def

        # Set message options
        for k, v in sorted(self.options.items(), key=lambda t: t[0]):  # sorted by key
            try:
                if k not in self.message_options:
                    self.message_options[k] = v
            except KeyError:
                pass

        self.current_message_name = None
        return True

    def visit_MessageExtension(self, obj):
        return True

    def visit_MethodDefinition(self, obj):
        return True

    def visit_ServiceDefinition(self, obj):
        return True

    def visit_ExtensionsDirective(self, obj):
        return True

    def visit_Literal(self, obj):
        return True

    def visit_Name(self, obj):
        return True

    def visit_DotName(self, obj):
        return True

    def visit_Proto(self, obj):
        self.count_stack.push(count_messages(obj.body))
        return True

    def visit_Proto_post(self, obj):
        count = self.count_stack.pop()
        messages = []
        for i in range(0, count):
            try:
                m = self.stack.pop()
            except IndexError:
                pass

            messages.insert(0, m)

        self.compute_rlinks(messages, self.models)

        self.messages = messages
        return True

    def visit_LinkSpec(self, obj):
        count = self.count_stack.pop()
        self.count_stack.push(count + 1)
        return True

    def compute_rlinks(self, messages, message_dict):
        rev_links = {}

        link_opposite = {
            "manytomany": "manytomany",
            "manytoone": "onetomany",
            "onetoone": "onetoone",
            "onetomany": "manytoone",
        }

        for msg in messages:
            for lnk in msg["links"]:
                rlink = copy.deepcopy(lnk)

                rlink["_type"] = "rlink"  # An implicit link, not declared in the model
                rlink["src_port"] = lnk["dst_port"]
                rlink["dst_port"] = lnk["src_port"]
                rlink["peer"] = {
                    "name": msg["name"],
                    "package": msg["package"],
                    "fqn": msg["fqn"],
                }
                rlink["link_type"] = link_opposite[lnk["link_type"]]
                rlink["reverse_id"] = lnk["reverse_id"]

                if (not lnk["reverse_id"]) and (self.args.verbosity >= 1):
                    print(
                        "WARNING: Field %s in model %s has no reverse_id"
                        % (lnk["src_port"], msg["name"]),
                        file=sys.stderr,
                    )

                if lnk["reverse_id"] and (
                    (int(lnk["reverse_id"]) < 1000) or (int(lnk["reverse_id"]) >= 1900)
                ):
                    raise Exception(
                        "reverse id for field %s in model %s should be between 1000 and 1899"
                        % (lnk["src_port"], msg["name"])
                    )

                try:
                    try:
                        rev_links[lnk["peer"]["fqn"]].append(rlink)
                    except TypeError:
                        pass
                except KeyError:
                    rev_links[lnk["peer"]["fqn"]] = [rlink]

        for msg in messages:
            try:
                msg["rlinks"] = rev_links[msg["name"]]
                message_dict[msg["name"]]["rlinks"] = msg["rlinks"]
            except KeyError:
                pass
