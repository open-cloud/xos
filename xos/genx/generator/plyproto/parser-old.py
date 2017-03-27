__author__ = "Dusan (Ph4r05) Klinec"
__copyright__ = "Copyright (C) 2014 Dusan (ph4r05) Klinec"
__license__ = "Apache License, Version 2.0"
__version__ = "1.0"

import ply.lex as lex
import ply.yacc as yacc
from .model import *

class ProtobufLexer(object):
    keywords = ('double', 'float', 'int32', 'int64', 'uint32', 'uint64', 'sint32', 'sint64',
                'fixed32', 'fixed64', 'sfixed32', 'sfixed64', 'bool', 'string', 'bytes',
                'message', 'required', 'optional', 'repeated', 'enum', 'extensions', 'max', 'extends', 'extend',
                'to', 'package', 'service', 'rpc', 'returns', 'true', 'false', 'option', 'import', 'onetomany', 'manytomany', 'onetoone')

    tokens = [
        'NAME',
        'NUM',
        'STRING_LITERAL',
        'LINE_COMMENT', 'BLOCK_COMMENT',

        'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
        'LPAR', 'RPAR', 'EQ', 'SEMI', 'DOT',
        'ARROW', 'COLON'
        'STARTTOKEN'

    ] + [k.upper() for k in keywords]
    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_NUM = r'[+-]?\d+'
    t_STRING_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

    t_ignore_LINE_COMMENT = '//.*'
    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    t_LBRACE = '{'
    t_RBRACE = '}'
    t_LBRACK = '\\['
    t_RBRACK = '\\]'
    t_LPAR = '\\('
    t_RPAR = '\\)'
    t_EQ = '='
    t_COLON = ':'
    t_ARROW = '\\-\\>'
    t_SEMI = ';'
    t_DOT = '\\.'
    t_ignore = ' \t\f'
    t_STARTTOKEN = '\\+'

    def t_NAME(self, t):
        '[A-Za-z_$][A-Za-z0-9_$]*'
        if t.value in ProtobufLexer.keywords:
            #print "type: %s val %s t %s" % (t.type, t.value, t)
            t.type = t.value.upper()
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newline2(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        t.lexer.skip(1)

class LexHelper:
    offset = 0
    def get_max_linespan(self, p):
        defSpan=[1e60, -1]
        mSpan=[1e60, -1]
        for sp in range(0, len(p)):
            csp = p.linespan(sp)
            if csp[0] == 0 and csp[1] == 0:
                if hasattr(p[sp], "linespan"):
                    csp = p[sp].linespan
                else:
                    continue
            if csp == None or len(csp) != 2: continue
            if csp[0] == 0 and csp[1] == 0: continue
            if csp[0] < mSpan[0]: mSpan[0] = csp[0]
            if csp[1] > mSpan[1]: mSpan[1] = csp[1]
        if defSpan == mSpan: return (0,0)
        return tuple([mSpan[0]-self.offset, mSpan[1]-self.offset])

    def get_max_lexspan(self, p):
        defSpan=[1e60, -1]
        mSpan=[1e60, -1]
        for sp in range(0, len(p)):
            csp = p.lexspan(sp)
            if csp[0] == 0 and csp[1] == 0:
                if hasattr(p[sp], "lexspan"):
                    csp = p[sp].lexspan
                else:
                    continue
            if csp == None or len(csp) != 2: continue
            if csp[0] == 0 and csp[1] == 0: continue
            if csp[0] < mSpan[0]: mSpan[0] = csp[0]
            if csp[1] > mSpan[1]: mSpan[1] = csp[1]
        if defSpan == mSpan: return (0,0)
        return tuple([mSpan[0]-self.offset, mSpan[1]-self.offset])

    def set_parse_object(self, dst, p):
        dst.setLexData(linespan=self.get_max_linespan(p), lexspan=self.get_max_lexspan(p))
        dst.setLexObj(p)

class ProtobufParser(object):
    tokens = ProtobufLexer.tokens
    offset = 0
    lh = LexHelper()

    def setOffset(self, of):
        self.offset = of
        self.lh.offset = of

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_field_modifier(self,p):
        '''field_modifier : REQUIRED
                          | OPTIONAL'''
        p[0] = LU.i(p,1)

    def p_primitive_type(self, p):
        '''primitive_type : DOUBLE
                          | FLOAT
                          | INT32
                          | INT64
                          | UINT32
                          | UINT64
                          | SINT32
                          | SINT64
                          | FIXED32
                          | FIXED64
                          | SFIXED32
                          | SFIXED64
                          | BOOL
                          | STRING
                          | BYTES'''
        p[0] = LU.i(p,1)
   
    def p_link_type(self, p):
        '''link_type      : ONETOONE
                          | ONETOMANY
                          | MANYTOMANY'''
        p[0] = LU.i(p,1)

    def p_field_id(self, p):
        '''field_id : NUM'''
        p[0] = LU.i(p,1)

    def p_rvalue(self, p):
        '''rvalue : NUM
                  | TRUE
                  | FALSE'''
        p[0] = LU.i(p,1)

    def p_rvalue2(self, p):
        '''rvalue : NAME'''
        p[0] = Name(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_field_directive(self, p):
        '''field_directive : LBRACK NAME EQ rvalue RBRACK'''
        p[0] = FieldDirective(Name(LU.i(p, 2)), LU.i(p,4))
        self.lh.set_parse_object(p[0], p)

    def p_field_directive_times(self, p):
        '''field_directive_times : field_directive_plus'''
        p[0] = p[1]

    def p_field_directive_times2(self, p):
        '''field_directive_times : empty'''
        p[0] = []

    def p_field_directive_plus(self, p):
        '''field_directive_plus : field_directive
                               | field_directive_plus field_directive'''
        if len(p) == 2:
            p[0] = [LU(p,1)]
        else:
            p[0] = p[1] + [LU(p,2)]

    def p_dotname(self, p):
        '''dotname : NAME
                   | dotname DOT NAME'''
        if len(p) == 2:
            p[0] = [LU(p,1)]
        else:
            p[0] = p[1] + [LU(p,3)]

    # Hack for cases when there is a field named 'message' or 'max'
    def p_fieldName(self, p):
        '''field_name : NAME
                      | MESSAGE
                      | MAX'''
        p[0] = Name(LU.i(p,1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_field_type(self, p):
        '''field_type : primitive_type'''
        p[0] = FieldType(LU.i(p,1))
        self.lh.set_parse_object(p[0], p)

    def p_field_type2(self, p):
        '''field_type : dotname'''
        p[0] = DotName(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    # Root of the field declaration.
    def p_field_definition(self, p):
        '''field_definition : field_modifier field_type field_name EQ field_id field_directive_times SEMI'''
        p[0] = FieldDefinition(LU.i(p,1), LU.i(p,2), LU.i(p, 3), LU.i(p,5), LU.i(p,6))
        self.lh.set_parse_object(p[0], p)

    # Link definition
    #def p_link_definition(self, p):
    #    '''link_definition : link_type field_modifier field_name ARROW NAME COLON field_name EQ field_id SEMI'''
    #    #p[0] = FieldDefinition(LU.i(p,1), FieldType(INT32), LU.i(p, 3), LU.i(p, 9), [FieldDirective('type', 'link'), FieldDirective('model',LU.i(p,5)), FieldDirective('port',LU.i(p,7))])
    #    p[0] = FieldDefinition(LU.i(p,2), FieldType(INT32), LU.i(p, 3), LU.i(p, 9), [])
    #    self.lh.set_parse_object(p[0], p)

    def p_message_body_part(self, p):
        '''message_body_part : field_definition
                           | message_definition'''

        #'''message_body_part : field_definition
        #                   | link_definition
        #                   | message_definition'''

        p[0] = p[1]

    # message_body ::= { field_definition | enum_definition | message_definition | extensions_definition | message_extension }*
    def p_message_body(self, p):
        '''message_body : empty'''
        p[0] = []

    # message_body ::= { field_definition | enum_definition | message_definition | extensions_definition | message_extension }*
    def p_message_body2(self, p):
        '''message_body : message_body_part
                      | message_body message_body_part'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # Root of the message declaration.
    # message_definition = MESSAGE_ - ident("messageId") + LBRACE + message_body("body") + RBRACE
    def p_message_definition(self, p):
        '''message_definition : MESSAGE NAME LBRACE message_body RBRACE'''
        p[0] = MessageDefinition(Name(LU.i(p, 2)), LU.i(p,4))
        self.lh.set_parse_object(p[0], p)

    # package_directive ::= 'package' ident [ '.' ident]* ';'
    def p_package_directive(self,p):
        '''package_directive : PACKAGE dotname SEMI'''
        p[0] = PackageStatement(Name(LU.i(p, 2)))
        self.lh.set_parse_object(p[0], p)

    # import_directive = IMPORT_ - quotedString("importFileSpec") + SEMI
    def p_import_directive(self, p):
        '''import_directive : IMPORT STRING_LITERAL SEMI'''
        p[0] = ImportStatement(Literal(LU.i(p,2)))
        self.lh.set_parse_object(p[0], p)

    # topLevelStatement = Group(message_definition | message_extension | enum_definition | service_definition | import_directive | option_directive)
    def p_topLevel(self,p):
        '''topLevel : message_definition'''
        p[0] = p[1]

    def p_package_definition(self, p):
        '''package_definition : package_directive'''
        p[0] = p[1]

    def p_packages2(self, p):
        '''package_definition : empty'''
        p[0] = []

    def p_statements2(self, p):
        '''statements : topLevel
                      | statements topLevel'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statements(self, p):
        '''statements : empty'''
        p[0] = []

    # parser = Optional(package_directive) + ZeroOrMore(topLevelStatement)
    def p_protofile(self, p):
        '''protofile : package_definition statements'''
        p[0] = ProtoFile(LU.i(p,1), LU.i(p,2))
        self.lh.set_parse_object(p[0], p)

    # Parsing starting point
    def p_goal(self, p):
        '''goal : STARTTOKEN protofile'''
        p[0] = p[2]

    def p_error(self, p):
        print('error: {}'.format(p))

class ProtobufAnalyzer(object):

    def __init__(self):
        self.lexer = lex.lex(module=ProtobufLexer(), optimize=1)
        self.parser = yacc.yacc(module=ProtobufParser(), start='goal', optimize=1)

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token)

    def tokenize_file(self, _file):
        if type(_file) == str:
            _file = file(_file)
        content = ''
        for line in _file:
            content += line
        return self.tokenize_string(content)

    def parse_string(self, code, debug=0, lineno=1, prefix='+'):
        self.lexer.lineno = lineno
        self.parser.offset = len(prefix)
        return self.parser.parse(prefix + code, lexer=self.lexer, debug=debug)

    def parse_file(self, _file, debug=0):
        if type(_file) == str:
            _file = file(_file)
        content = ''
        for line in _file:
            content += line
        return self.parse_string(content, debug=debug)
