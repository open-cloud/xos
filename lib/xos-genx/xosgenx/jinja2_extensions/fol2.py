import astunparse
import ast
import random
import string
from plyxproto.parser import *
import pdb

BINOPS = ['|', '&', '=>']
QUANTS = ['exists', 'forall']


class PolicyException(Exception):
    pass


class AutoVariable:
    def __init__(self, base):
        self.base = base

    def __iter__(self):
        self.idx = 0
        return self

    def next(self):
        var = 'i%d' % self.idx
        self.idx += 1
        return var


def gen_random_string():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))


class FOL2Python:
    def __init__(self, context_map=None):
        # This will produce i0, i1, i2 etc.
        self.loopvar = iter(AutoVariable('i'))
        self.verdictvar = iter(AutoVariable('result'))

        self.loop_variable = self.loopvar.next()
        self.verdict_variable = self.verdictvar.next()
        self.context_map = context_map

        if not self.context_map:
            self.context_map = {'user': 'self', 'obj': 'obj'}

    def loop_next(self):
        self.loop_variable = self.loopvar.next()

    def verdict_next(self):
        self.verdict_variable = self.verdictvar.next()

    def gen_enumerate(self, fol):
        pass

    def format_term_for_query(self, model, term, django=False):
        if term.startswith(model + '.'):
            term = term[len(model) + 1:]
            if django:
                term = term.replace('.', '__')
            else:
                term = '__elt' + '.' + term
        return term

    def fol_to_python_filter(self, model, e, django=False, negate=False):
        try:
            (k, v), = e.items()
        except AttributeError:
            return [self.format_term_for_query(model, e)]

        if django:
            if negate:
                # De Morgan's negation
                q_bracket = '~Q(%s)'
                or_expr = ','
                and_expr = '|'
            else:
                q_bracket = 'Q(%s)'
                or_expr = '|'
                and_expr = ','
        else:
            if negate:
                # De Morgan's negation
                q_bracket = 'not %s'
                or_expr = ' and '
                and_expr = ' or '
            else:
                q_bracket = '%s'
                or_expr = ' or '
                and_expr = ' and '

        if k == '=':
            v = [self.format_term_for_query(
                model, term, django=django) for term in v]
            if django:
                operator = ' = '
            else:
                operator = ' == '
            return [q_bracket % operator.join(v)]
        elif k == '|':
            components = [self.fol_to_python_filter(
                model, x, django=django).pop() for x in v]
            return [or_expr.join(components)]
        elif k == '&':
            components = [self.fol_to_python_filter(
                model, x, django=django).pop() for x in v]
            return [and_expr.join(components)]
        elif k == '=>':
            components = [self.fol_to_python_filter(
                model, x, django=django).pop() for x in v]
            return ['~%s | %s' % (components[0], components[1])]

    """ Convert a single leaf node from a string
        to an AST"""

    def str_to_ast(self, s):
        ast_module = ast.parse(s)
        return ast_module.body[0]

    def hoist_constants(self, fol, var=None):
        try:
            (k, v), = fol.items()
        except AttributeError:
            k = 'term'
            v = fol

        if k == 'python':
            # Tainted, don't optimize
            if var:
                return {'hoist': []}
            else:
                return fol

        if var:
            if k == 'term':
                if not v.startswith(var):
                    return {'hoist': ['const', fol], 'result': 'True'}
                else:
                    return {'hoist': [], 'result': fol}
            elif k == '=':
                lhs, rhs = v
                if not lhs.startswith(var) and not rhs.startswith(var):
                    return {'hoist': ['=', fol], 'result': 'True'}  # XXX
                else:
                    return {'hoist': [], 'result': fol}
            elif k in BINOPS:
                lhs, rhs = v
                rlhs = self.hoist_constants(lhs, var)
                rrhs = self.hoist_constants(rhs, var)

                if rlhs['hoist'] and rrhs['hoist']:
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
                        return {'hoist': ['const'], 'result': {result['hoist'][0]: [result['hoist'][1], {k: [var2, result['result']]}]}}
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

    def gen_test_function(self, fol, policy_name, tag):
        if not tag:
            tag = gen_random_string()

        policy_function_name = 'policy_%(policy_name)s_%(random_string)s' % {
            'policy_name': policy_name, 'random_string': tag}
        self.verdict_next()
        function_str = """
def %(fn_name)s(obj, ctx):
    return %(vvar)s
        """ % {'fn_name': policy_function_name, 'vvar': self.verdict_variable}

        function_ast = self.str_to_ast(function_str)
        policy_code = self.gen_test(fol, self.verdict_variable)

        function_ast.body = [policy_code] + function_ast.body

        return astunparse.unparse(function_ast)

    def gen_test(self, fol, verdict_var, bindings=None):
        if isinstance(fol, str):
            return self.str_to_ast('%(verdict_var)s = %(constant)s' % {'verdict_var': verdict_var, 'constant': fol})

        (k, v), = fol.items()

        if k == '=':
            # This is the simplest case, we don't recurse further
            # To use terms that are not simple variables, use
            # the Python escape, e.g. {{ slice.creator is not None }}
            lhs, rhs = v

            assignments = []

            try:
                for t in lhs, rhs:
                    py_expr = t['python']

                    self.verdict_next()
                    vv = self.verdict_variable

                    try:
                        expr_ast = self.str_to_ast(py_expr)
                    except SyntaxError:
                        raise PolicyException('Syntax error in %s' % v)

                    if not isinstance(expr_ast, ast.Expr):
                        raise PolicyException(
                            '%s is not an expression' % expr_ast)

                    assignment_str = """
%(verdict_var)s = (%(escape_expr)s)
                    """ % {'verdict_var': vv, 'escape_expr': py_expr}

                    if t == lhs:
                        lhs = vv
                    else:
                        rhs = vv

                    assignment_ast = self.str_to_ast(assignment_str)
                    assignments.append(assignment_ast)
            except TypeError:
                pass

            comparison_str = """
%(verdict_var)s = (%(lhs)s == %(rhs)s)
            """ % {'verdict_var': verdict_var, 'lhs': lhs, 'rhs': rhs}

            comparison_ast = self.str_to_ast(comparison_str)

            combined_ast = ast.Module(body=assignments + [comparison_ast])
            return combined_ast
        elif k in BINOPS:
            lhs, rhs = v

            top_vvar = self.verdict_variable

            self.verdict_next()
            lvar = self.verdict_variable

            self.verdict_next()
            rvar = self.verdict_variable

            lblock = self.gen_test(lhs, lvar)
            rblock = self.gen_test(rhs, rvar)

            invert = ''
            if k == '&':
                binop = 'and'
            elif k == '|':
                binop = 'or'
            elif k == '=>':
                binop = 'or'
                invert = 'not'

            binop_str = """
%(verdict_var)s = %(invert)s %(lvar)s %(binop)s %(rvar)s
            """ % {'verdict_var': top_vvar, 'invert': invert, 'lvar': lvar, 'binop': binop, 'rvar': rvar}

            binop_ast = self.str_to_ast(binop_str)

            combined_ast = ast.Module(body=[lblock, rblock, binop_ast])
            return combined_ast
        elif k == 'exists':
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
%(verdict_var)s = %(model)s.objects.filter(%(query)s)[0]
                """ % {'verdict_var': verdict_var, 'model': var, 'query': entry}

                python_ast = ast.parse(python_str)
            else:
                f = self.fol_to_python_filter(var, expr, django=False)
                entry = f.pop()

                python_str = """
%(verdict_var)s = filter(lambda __elt:%(query)s, %(model)s)
                """ % {'verdict_var': verdict_var, 'model': var, 'query': entry}

                python_ast = ast.parse(python_str)

            return python_ast
        elif k=='forall':
            var, expr = v

            if var.istitle():
                f = self.fol_to_python_filter(var, expr, django=True, negate = True)
                entry = f.pop()

                self.verdict_next()
                vvar = self.verdict_variable

                python_str = """
%(verdict_var)s = %(model)s.objects.filter(%(query)s)[0]
                """ % {'verdict_var': vvar, 'model': var, 'query': entry}

                python_ast = ast.parse(python_str)
            else:
                f = self.fol_to_python_filter(var, expr, django=False, negate = True)
                entry = f.pop()

                python_str = """
%(verdict_var)s = next(elt for elt in %(model)s if %(query)s)
                """ % {'verdict_var': vvar, 'model': var, 'query': entry}

                python_ast = ast.parse(python_str)

            negate_str = """
%(verdict_var)s = not %(vvar)s
            """ % {'verdict_var': verdict_var, 'vvar': vvar}

            negate_ast = ast.parse(negate_str)

            return ast.Module(body=[python_ast, negate_ast])

def xproto_fol_to_python_test(fol, model, tag=None):
    f2p = FOL2Python()
    fol = f2p.hoist_constants(fol)
    a = f2p.gen_test_function(fol, 'output', tag)
    return a


def main():
    while True:
        inp = raw_input()
        fol_lexer = lex.lex(module=FOLLexer())
        fol_parser = yacc.yacc(module=FOLParser(), start='goal')

        val = fol_parser.parse(inp, lexer=fol_lexer)
        a = xproto_fol_to_python_test(val, 'output')
        print a


if __name__ == "__main__":
    main()
