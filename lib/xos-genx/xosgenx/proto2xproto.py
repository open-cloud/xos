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

import ply.lex as lex
import ply.yacc as yacc
import plyxproto.model as m
from plyxproto.helpers import Visitor
from plyxproto.logicparser import FOLLexer, FOLParser
from six.moves import map


class Stack(list):
    def push(self, x):
        self.append(x)


def str_to_dict(s):
    lst = s.rsplit(".", 1)
    name = lst[-1]

    if len(lst) == 2:
        package = lst[0]
    else:
        package = ""

    return {"name": name, "package": package, "fqn": s}


def replace_link(obj):
    try:
        link = obj.link
        try:
            through = link["through"]
        except KeyError:
            through = None

        try:
            through_str = through[1:-1]
        except TypeError:
            through_str = None

        if through_str:
            through_dict = str_to_dict(through_str)
        else:
            through_dict = {}

        model_dict = str_to_dict(link["model"][1:-1])

        ls = m.LinkSpec(
            obj,
            m.LinkDefinition(
                link["link"][1:-1],
                obj.name,
                model_dict,
                link["port"][1:-1],
                through_dict,
            ),
        )
        return ls
    except BaseException:
        return obj


class Proto2XProto(Visitor):
    fol_lexer = lex.lex(module=FOLLexer())
    fol_parser = yacc.yacc(module=FOLParser(), start="goal", debug=0, outputdir="/tmp")

    def __init__(self):
        super(Proto2XProto, self).__init__()

        self.stack = Stack()
        self.count_stack = Stack()
        self.content = ""
        self.offset = 0
        self.statementsChanged = 0
        self.message_options = {}
        self.options = {}
        self.current_message_name = None

        self.xproto_message_options = ["bases"]
        self.xproto_field_options = ["model"]
        self.verbose = 0
        self.first_field = True
        self.first_method = True

    def replace_policy(self, obj):
        if isinstance(obj, m.OptionStatement):
            rhs = obj.value.value.pval
            if rhs.startswith('"') and rhs.endswith('"'):
                rhs = rhs[1:-1]

            if rhs.startswith("policy:"):
                str = rhs.split(":", 1)[1]
                val = self.fol_parser.parse(str, lexer=self.fol_lexer)

                return m.PolicyDefinition(obj.name, val)

        return obj

    def proto_to_xproto_field(self, obj):
        try:
            opts = {}
            for fd in obj.fieldDirective:
                k = fd.pval.name.value.pval
                v = fd.pval.value.value.pval
                opts[k] = v

            if "model" in opts and "link" in opts and "port" in opts:
                obj.link = opts
            pass
        except KeyError:
            raise

    def proto_to_xproto_message(self, obj):
        try:
            try:
                bases = self.message_options["bases"].split(",")
            except KeyError:
                bases = []

            bases = [str_to_dict(x[1:-1]) for x in bases]
            obj.bases = bases
        except KeyError:
            raise

    def map_field(self, obj, s):
        if "model" in s:
            link = m.LinkDefinition(
                "onetoone", "src", "name", "dst", obj.linespan, obj.lexspan, obj.p
            )
            lspec = m.LinkSpec(link, obj)
        else:
            lspec = obj
        return lspec

    def get_stack(self):
        return self.stack

    def visit_PackageStatement(self, obj):
        """Ignore"""
        return True

    def visit_ImportStatement(self, obj):
        """Ignore"""
        return True

    def visit_OptionStatement(self, obj):
        if self.current_message_name:
            k = obj.name.value.pval
            self.message_options[k] = obj.value.value.pval
            if k in self.xproto_message_options:
                obj.mark_for_deletion = True
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
        return True

    def visit_FieldType(self, obj):
        return True

    def visit_LinkDefinition(self, obj):
        return True

    def visit_FieldDefinition(self, obj):
        return True

    def visit_FieldDefinition_post(self, obj):
        self.proto_to_xproto_field(obj)
        return True

    def visit_EnumFieldDefinition(self, obj):
        return True

    def visit_EnumDefinition(self, obj):
        return True

    def visit_MessageDefinition(self, obj):
        self.current_message_name = obj.name.value.pval
        self.message_options = {}

        return True

    def visit_MessageDefinition_post(self, obj):
        self.proto_to_xproto_message(obj)
        obj.body = [x for x in obj.body if not hasattr(x, "mark_for_deletion")]
        obj.body = list(map(replace_link, obj.body))

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
        self.count_stack.push(len(obj.body))
        return True

    def visit_Proto_post(self, obj):

        obj.body = [self.replace_policy(o) for o in obj.body]
        return True

    def visit_LinkSpec(self, obj):
        return False
