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
import astunparse
import ast
import random
import string
import jinja2
from plyxproto.parser import lex, yacc
from plyxproto.logicparser import FOLParser, FOLLexer
from six.moves import range
from six.moves import input

BINOPS = ["|", "&", "->"]
QUANTS = ["exists", "forall"]


class PolicyException(Exception):
    pass


class ConstructNotHandled(Exception):
    pass


class TrivialPolicy(Exception):
    pass


class AutoVariable:
    def __init__(self, base):
        self.base = base

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        var = "i%d" % self.idx
        self.idx += 1
        return var

    next = __next__  # 2to3


def gen_random_string():
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(5)
    )


class FOL2Python:
    def __init__(self, context_map=None):
        # This will produce i0, i1, i2 etc.
        self.loopvar = iter(AutoVariable("i"))
        self.verdictvar = iter(AutoVariable("result"))

        self.loop_variable = next(self.loopvar)
        self.verdict_variable = next(self.verdictvar)
        self.context_map = context_map

        if not self.context_map:
            self.context_map = {"user": "self", "obj": "obj"}

    def loop_next(self):
        self.loop_variable = next(self.loopvar)

    def verdict_next(self):
        self.verdict_variable = next(self.verdictvar)

    def gen_enumerate(self, fol):
        pass

    def format_term_for_query(self, model, term, django=False):
        if term.startswith(model + "."):
            term = term[len(model) + 1:]
            if django:
                term = term.replace(".", "__")
            else:
                term = "__elt" + "." + term
        return term

    def fol_to_python_filter(self, model, e, django=False, negate=False):
        try:
            (k, v), = e.items()
        except AttributeError:
            return [self.format_term_for_query(model, e)]

        if django:
            if negate:
                # De Morgan's negation
                q_bracket = "~Q(%s)"
                or_expr = ","
                and_expr = "|"
            else:
                q_bracket = "Q(%s)"
                or_expr = "|"
                and_expr = ","
        else:
            if negate:
                # De Morgan's negation
                q_bracket = "not %s"
                or_expr = " and "
                and_expr = " or "
            else:
                q_bracket = "%s"
                or_expr = " or "
                and_expr = " and "

        if k in ["=", "in"]:
            v = [self.format_term_for_query(model, term, django=django) for term in v]
            if django:
                operator_map = {"=": " = ", "in": "__in"}
            else:
                operator_map = {"=": " == ", "in": "in"}
            operator = operator_map[k]
            return [q_bracket % operator.join(v)]
        elif k == "|":
            components = [
                self.fol_to_python_filter(model, x, django=django).pop() for x in v
            ]
            return [or_expr.join(components)]
        elif k == "&":
            components = [
                self.fol_to_python_filter(model, x, django=django).pop() for x in v
            ]
            return [and_expr.join(components)]
        elif k == "->":
            components = [
                self.fol_to_python_filter(model, x, django=django).pop() for x in v
            ]
            return ["~%s | %s" % (components[0], components[1])]

    """ Convert a single leaf node from a string
        to an AST"""

    def str_to_ast(self, s):
        ast_module = ast.parse(s)
        return ast_module.body[0]

    def reduce_operands(self, operands):
        if operands[0] in ["True", "False"]:
            return (operands[0], operands[1])
        elif operands[1] in ["True", "False"]:
            return (operands[1], operands[0])
        else:
            return None

    """ Simplify binops with constants """

    def simplify_binop(self, binop):
        (k, v), = binop.items()
        if k == "->":
            lhs, rhs = v
            if lhs == "True":
                return rhs
            elif rhs == "True":
                return "True"
            elif lhs == "False":
                return "True"
            elif rhs == "False":
                return {"not": lhs}

        var_expr = self.reduce_operands(v)

        if not var_expr:
            return binop
        else:
            constant, var = var_expr
            if k == "|":
                if constant == "True":
                    return "True"
                elif constant == "False":
                    return var
                else:
                    raise Exception("Internal error - variable read as constant")
            elif k == "&":
                if constant == "True":
                    return var
                elif constant == "False":
                    return "False"

    def is_constant(self, var, fol):
        try:
            (k, v), = fol.items()
        except AttributeError:
            k = "term"
            v = fol

        if k in ["python", "policy"]:
            # Treat as a constant and hoist, since it cannot be quantified
            return True
        elif k == "term":
            return not v.startswith(var)
        elif k == "not":
            return self.is_constant(var, fol)
        elif k in ["in", "="]:
            lhs, rhs = v
            return self.is_constant(var, lhs) and self.is_constant(var, rhs)
        elif k in BINOPS:
            lhs, rhs = v
            return self.is_constant(lhs, var) and self.is_constant(rhs, var)
        elif k in QUANTS:
            is_constant = self.is_constant(var, fol[1])
            return is_constant
        else:
            raise ConstructNotHandled(k)

    def find_constants(self, var, fol, constants):
        try:
            (k, v), = fol.items()
        except AttributeError:
            k = "term"
            v = fol

        if k in ["python", "policy"]:
            # Treat as a constant and hoist, since it cannot be quantified
            if fol not in constants:
                constants.append(fol)
            return constants
        elif k == "term":
            if not v.startswith(var):
                constants.append(v)
            return constants
        elif k == "not":
            return self.find_constants(var, v, constants)
        elif k in ["in", "="]:
            lhs, rhs = v
            if isinstance(lhs, str) and isinstance(rhs, str):
                if not lhs.startswith(var) and not rhs.startswith(var):
                    constants.append(fol)
                return constants
            else:
                constants = self.find_constants(var, lhs, constants)
                return self.find_constants(var, rhs, constants)
        elif k in BINOPS:
            lhs, rhs = v
            constants = self.find_constants(var, lhs, constants)
            constants = self.find_constants(var, rhs, constants)
            return constants
        elif k in QUANTS:
            is_constant = self.is_constant(var, v[1])
            if is_constant:
                constants.append(fol)
            return constants
        else:
            raise ConstructNotHandled(k)

    """ Hoist constants out of quantifiers. Depth-first. """

    def hoist_outer(self, fol):
        try:
            (k, v), = fol.items()
        except AttributeError:
            k = "term"
            v = fol

        if k in ["python", "policy"]:
            # Tainted, optimization and distribution not possible
            return fol
        elif k == "term":
            return fol
        elif k == "not":
            vprime = self.hoist_outer(v)
            return {"not": vprime}
        elif k in ["in", "="]:
            lhs, rhs = v
            rlhs = self.hoist_outer(lhs)
            rrhs = self.hoist_outer(rhs)
            return {k: [rlhs, rrhs]}
        elif k in BINOPS:
            lhs, rhs = v
            rlhs = self.hoist_outer(lhs)
            rrhs = self.hoist_outer(rhs)

            fol_prime = {k: [rlhs, rrhs]}
            fol_simplified = self.simplify_binop(fol_prime)
            return fol_simplified
        elif k in QUANTS:
            rexpr = self.hoist_outer(v[1])
            return self.hoist_quant(k, [v[0], rexpr])
        else:
            raise ConstructNotHandled(k)

    def replace_const(self, fol, c, value):
        if fol == c:
            return value

        try:
            (k, v), = fol.items()
        except AttributeError:
            k = "term"
            v = fol

        if k == "term":
            if v == c:
                return value
            else:
                return v
        elif k == "not":
            new_expr = self.replace_const(v, c, value)
            if new_expr == "True":
                return "False"
            elif new_expr == "False":
                return "True"
            else:
                return {"not": new_expr}
        elif k in ["in", "="]:
            lhs, rhs = v
            rlhs = self.replace_const(lhs, c, value)
            rrhs = self.replace_const(rhs, c, value)

            if rlhs == rrhs:
                return "True"
            else:
                return {k: [rlhs, rrhs]}
        elif k in BINOPS:
            lhs, rhs = v

            rlhs = self.replace_const(lhs, c, value)
            rrhs = self.replace_const(rhs, c, value)

            return self.simplify_binop({k: [rlhs, rrhs]})
        elif k in QUANTS:
            var, expr = v
            new_expr = self.replace_const(expr, c, value)
            if new_expr in ["True", "False"]:
                return new_expr
            else:
                return {k: [var, new_expr]}
        else:
            raise ConstructNotHandled(k)

    def shannon_expand(self, c, fol):
        lhs = self.replace_const(fol, c, "True")
        rhs = self.replace_const(fol, c, "False")
        not_c = {"not": c}
        rlhs = {"&": [c, lhs]}
        rlhs = self.simplify_binop(rlhs)

        rrhs = {"&": [not_c, rhs]}
        rrhs = self.simplify_binop(rrhs)

        combined = {"|": [rlhs, rrhs]}
        return self.simplify_binop(combined)

    def hoist_quant(self, k, expr):
        var, v = expr

        constants = self.find_constants(var, v, constants=[])

        fol = {k: expr}

        for c in constants:
            fol = self.shannon_expand(c, fol)

        return fol

        """
        if var:
            if k == 'term':
                if not v.startswith(var):
                    return {'hoist': ['const', fol], 'result': 'True'}
                else:
                    return {'hoist': [], 'result': fol}
            elif k in ['=', 'in']:
                lhs, rhs = v
                if not lhs.startswith(var) and not rhs.startswith(var):
                    return {'hoist': [k, fol], 'result': 'True'}  # XXX
                else:
                    return {'hoist': [], 'result': fol}
            elif k in BINOPS:
                lhs, rhs = v
                rlhs = self.hoist_constants(lhs, var)
                rrhs = self.hoist_constants(rhs, var)

                if rlhs['hoist'] and rrhs['hoist'] and rlhs['result']=='True' and llhs['result']=='True':
                    return {'hoist': ['=', fol], 'result': 'True'}
                elif rlhs['hoist']:
                    return {'hoist': [k, lhs], 'result': rhs}
                elif rrhs['hoist']:
                    return {'hoist': [k, rhs], 'result': lhs}
                else:
                    return {'hoist': [], 'result': fol}

            elif k in QUANTS:
                var2, expr = v
                result = self.hoist_constants(expr, var2)
                if result['hoist']:
                    if result['result'] == 'True':
                        return {'hoist': ['const'], 'result': result['hoist'][1]}
                    elif result['hoist'][0] in BINOPS:
                        return {'hoist': ['const'], 'result': {result['hoist'][0]:
                                [result['hoist'][1], {k: [var2, result['result']]}]}}
                    else:
                        return {'hoist': ['const'], 'result': {k: [var2, result['result']]}}
                else:
                    result = self.hoist_constants(expr, var)
                    if result['result'] == 'True':
                        return {'hoist': ['&', fol], 'result': 'True'}
                    else:
                        return {'hoist': [], 'result': fol}
            else:
                return {'hoist': [], 'result': fol}
        else:
            if k in BINOPS:
                lhs, rhs = v
                rlhs = self.hoist_constants(lhs)
                rrhs = self.hoist_constants(rhs)
                return {k: [rlhs, rrhs]}
            elif k in QUANTS:
                var, expr = v
                result = self.hoist_constants(expr, var)
                if result['hoist']:
                    if result['result'] == 'True':
                        return result['hoist'][1]
                    elif result['hoist'][0] in BINOPS:
                        return {result['hoist'][0]: [result['hoist'][1], {k: [var, result['result']]}]}
                    else:
                        return {k: [var, result['result']]}
                else:
                    return fol
            else:
                return fol
        """

    def gen_validation_function(self, fol, policy_name, message, tag):
        if not tag:
            tag = gen_random_string()

        policy_function_name_template = "policy_%s_" + "%(random_string)s" % {
            "random_string": tag
        }
        policy_function_name = policy_function_name_template % policy_name
        self.verdict_next()
        function_str = """
def %(fn_name)s(obj, ctx):
    if not %(vvar)s: raise XOSValidationError("%(message)s".format(obj=obj, ctx=ctx))
        """ % {
            "fn_name": policy_function_name,
            "vvar": self.verdict_variable,
            "message": message,
        }

        function_ast = self.str_to_ast(function_str)
        policy_code = self.gen_test(
            policy_function_name_template, fol, self.verdict_variable
        )

        function_ast.body = [policy_code] + function_ast.body

        return function_ast

    def gen_test_function(self, fol, policy_name, tag):
        if not tag:
            tag = gen_random_string()

        policy_function_name_template = "%s_" + "%(random_string)s" % {
            "random_string": tag
        }
        policy_function_name = policy_function_name_template % policy_name

        self.verdict_next()
        function_str = """
def %(fn_name)s(obj, ctx):
    return %(vvar)s
        """ % {
            "fn_name": policy_function_name,
            "vvar": self.verdict_variable,
        }

        function_ast = self.str_to_ast(function_str)
        policy_code = self.gen_test(
            policy_function_name_template, fol, self.verdict_variable
        )

        function_ast.body = [policy_code] + function_ast.body

        return function_ast

    def gen_test(self, fn_template, fol, verdict_var, bindings=None):
        if isinstance(fol, str):
            return self.str_to_ast(
                "%(verdict_var)s = %(constant)s"
                % {"verdict_var": verdict_var, "constant": fol}
            )

        (k, v), = fol.items()

        if k == "policy":
            policy_name, object_name = v

            policy_fn = fn_template % policy_name
            call_str = """
if obj.%(object_name)s:
    %(verdict_var)s = %(policy_fn)s(obj.%(object_name)s, ctx)
else:
    # Everybody has access to null objects
    %(verdict_var)s = True
            """ % {
                "verdict_var": verdict_var,
                "policy_fn": policy_fn,
                "object_name": object_name,
            }

            call_ast = self.str_to_ast(call_str)
            return call_ast
        if k == "python":
            try:
                expr_ast = self.str_to_ast(v)
            except SyntaxError:
                raise PolicyException("Syntax error in %s" % v)

            if not isinstance(expr_ast, ast.Expr):
                raise PolicyException("%s is not an expression" % expr_ast)

            assignment_str = """
%(verdict_var)s = (%(escape_expr)s)
            """ % {
                "verdict_var": verdict_var,
                "escape_expr": v,
            }

            assignment_ast = self.str_to_ast(assignment_str)
            return assignment_ast
        elif k == "not":
            top_vvar = verdict_var
            self.verdict_next()
            sub_vvar = self.verdict_variable
            block = self.gen_test(fn_template, v, sub_vvar)
            assignment_str = """
%(verdict_var)s = not (%(subvar)s)
                    """ % {
                "verdict_var": top_vvar,
                "subvar": sub_vvar,
            }

            assignment_ast = self.str_to_ast(assignment_str)

            return ast.Module(body=[block, assignment_ast])
        elif k in ["=", "in"]:
            # This is the simplest case, we don't recurse further
            # To use terms that are not simple variables, use
            # the Python escape, e.g. {{ slice.creator is not None }}
            lhs, rhs = v

            assignments = []

            try:
                for t in lhs, rhs:
                    py_expr = t["python"]

                    self.verdict_next()
                    vv = self.verdict_variable

                    try:
                        expr_ast = self.str_to_ast(py_expr)
                    except SyntaxError:
                        raise PolicyException("Syntax error in %s" % v)

                    if not isinstance(expr_ast, ast.Expr):
                        raise PolicyException("%s is not an expression" % expr_ast)

                    assignment_str = """
%(verdict_var)s = (%(escape_expr)s)
                    """ % {
                        "verdict_var": vv,
                        "escape_expr": py_expr,
                    }

                    if t == lhs:
                        lhs = vv
                    else:
                        rhs = vv

                    assignment_ast = self.str_to_ast(assignment_str)
                    assignments.append(assignment_ast)
            except TypeError:
                pass

            if k == "=":
                operator = "=="
            elif k == "in":
                operator = "in"

            comparison_str = """
%(verdict_var)s = (%(lhs)s %(operator)s %(rhs)s)
            """ % {
                "verdict_var": verdict_var,
                "lhs": lhs,
                "rhs": rhs,
                "operator": operator,
            }

            comparison_ast = self.str_to_ast(comparison_str)
            combined_ast = ast.Module(body=assignments + [comparison_ast])

            return combined_ast
        elif k in BINOPS:
            lhs, rhs = v

            top_vvar = verdict_var

            self.verdict_next()
            lvar = self.verdict_variable

            self.verdict_next()
            rvar = self.verdict_variable

            lblock = self.gen_test(fn_template, lhs, lvar)
            rblock = self.gen_test(fn_template, rhs, rvar)

            invert = ""
            if k == "&":
                binop = "and"
            elif k == "|":
                binop = "or"
            elif k == "->":
                binop = "or"
                invert = "not"

            binop_str = """
%(verdict_var)s = %(invert)s %(lvar)s %(binop)s %(rvar)s
            """ % {
                "verdict_var": top_vvar,
                "invert": invert,
                "lvar": lvar,
                "binop": binop,
                "rvar": rvar,
            }

            binop_ast = self.str_to_ast(binop_str)

            combined_ast = ast.Module(body=[lblock, rblock, binop_ast])
            return combined_ast
        elif k == "exists":
            # If the variable starts with a capital letter,
            # we assume that it is a model. If it starts with
            # a small letter, we assume it is an enumerable
            #
            # We do not support nested exists yet. FIXME.

            var, expr = v

            if var.istitle():
                f = self.fol_to_python_filter(var, expr, django=True)
                entry = f.pop()

                python_str = """
%(verdict_var)s = not not %(model)s.objects.filter(%(query)s)
                """ % {
                    "verdict_var": verdict_var,
                    "model": var,
                    "query": entry,
                }

                python_ast = ast.parse(python_str)
            else:
                f = self.fol_to_python_filter(var, expr, django=False)
                entry = f.pop()

                python_str = """
%(verdict_var)s = filter(lambda __elt:%(query)s, %(model)s)
                """ % {
                    "verdict_var": verdict_var,
                    "model": var,
                    "query": entry,
                }

                python_ast = ast.parse(python_str)

            return python_ast
        elif k == "forall":
            var, expr = v

            if var.istitle():
                f = self.fol_to_python_filter(var, expr, django=True, negate=True)
                entry = f.pop()

                self.verdict_next()
                vvar = self.verdict_variable

                python_str = """
%(verdict_var)s = not not %(model)s.objects.filter(%(query)s)
                """ % {
                    "verdict_var": vvar,
                    "model": var,
                    "query": entry,
                }

                python_ast = ast.parse(python_str)
            else:
                f = self.fol_to_python_filter(var, expr, django=False, negate=True)
                entry = f.pop()

                python_str = """
%(verdict_var)s = next(elt for elt in %(model)s if %(query)s)
                """ % {
                    "verdict_var": vvar,
                    "model": var,
                    "query": entry,
                }

                python_ast = ast.parse(python_str)

            negate_str = """
%(verdict_var)s = not %(vvar)s
            """ % {
                "verdict_var": verdict_var,
                "vvar": vvar,
            }

            negate_ast = ast.parse(negate_str)

            return ast.Module(body=[python_ast, negate_ast])


def xproto_fol_to_python_test(policy, fol, model, tag=None):
    if isinstance(fol, jinja2.Undefined):
        raise Exception("Could not find policy:", policy)

    f2p = FOL2Python()
    fol_reduced = f2p.hoist_outer(fol)

    if fol_reduced in ["True", "False"] and fol != fol_reduced:
        raise TrivialPolicy(
            "Policy %(name)s trivially reduces to %(reduced)s."
            "If this is what you want, replace its contents with %(reduced)s"
            % {"name": policy, "reduced": fol_reduced}
        )

    a = f2p.gen_test_function(fol_reduced, policy, tag="security_check")

    return astunparse.unparse(a)


def xproto_fol_to_python_validator(policy, fol, model, message, tag=None):
    if isinstance(fol, jinja2.Undefined):
        raise Exception("Could not find policy:", policy)

    f2p = FOL2Python()
    fol_reduced = f2p.hoist_outer(fol)

    if fol_reduced in ["True", "False"] and fol != fol_reduced:
        raise TrivialPolicy(
            "Policy %(name)s trivially reduces to %(reduced)s."
            "If this is what you want, replace its contents with %(reduced)s"
            % {"name": policy, "reduced": fol_reduced}
        )

    a = f2p.gen_validation_function(fol_reduced, policy, message, tag="validator")

    return astunparse.unparse(a)


def main():
    while True:
        inp = ""
        while True:
            inp_line = input()
            if inp_line == "EOF":
                break
            else:
                inp += inp_line

        fol_lexer = lex.lex(module=FOLLexer())
        fol_parser = yacc.yacc(
            module=FOLParser(), start="goal", outputdir="/tmp", debug=0
        )

        val = fol_parser.parse(inp, lexer=fol_lexer)
        a = xproto_fol_to_python_test("pol", val, "output", "Test")
        # f2p = FOL2Python()
        # a = f2p.hoist_outer(val)
        print(a)


if __name__ == "__main__":
    main()
