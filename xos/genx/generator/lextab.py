# lextab.py. This file automatically created by PLY (version 3.5). Don't edit!
_tabversion   = '3.5'
_lextokens    = {'LPAR': 1, 'OPTION': 1, 'EXTEND': 1, 'FIXED32': 1, 'RPAR': 1, 'REPEATED': 1, 'TRUE': 1, 'DOT': 1, 'STRING': 1, 'INT32': 1, 'SERVICE': 1, 'SEMI': 1, 'OPTIONAL': 1, 'REQUIRED': 1, 'TO': 1, 'RPC': 1, 'NUM': 1, 'EXTENSIONS': 1, 'FIXED64': 1, 'IMPORT': 1, 'UINT32': 1, 'SINT32': 1, 'BLOCK_COMMENT': 1, 'ENUM': 1, 'LINE_COMMENT': 1, 'RBRACE': 1, 'PACKAGE': 1, 'RBRACK': 1, 'BYTES': 1, 'RETURNS': 1, 'INT64': 1, 'MAX': 1, 'EQ': 1, 'STRING_LITERAL': 1, 'UINT64': 1, 'LBRACE': 1, 'FALSE': 1, 'NAME': 1, 'SINT64': 1, 'STARTTOKEN': 1, 'FLOAT': 1, 'LBRACK': 1, 'SFIXED64': 1, 'SFIXED32': 1, 'BOOL': 1, 'DOUBLE': 1, 'EXTENDS': 1, 'MESSAGE': 1}
_lexreflags   = 0
_lexliterals  = '()+-*/=?:,.^|&~!=[]{};<>@%'
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_BLOCK_COMMENT>/\\*(.|\\n)*?\\*/)|(?P<t_NAME>[A-Za-z_$][A-Za-z0-9_$]*)|(?P<t_newline>\\n+)|(?P<t_newline2>(\\r\\n)+)|(?P<t_STRING_LITERAL>\\"([^\\\\\\n]|(\\\\.))*?\\")|(?P<t_NUM>[+-]?\\d+)|(?P<t_ignore_LINE_COMMENT>//.*)|(?P<t_RPAR>\\))|(?P<t_DOT>\\.)|(?P<t_LPAR>\\()|(?P<t_LBRACK>\\[)|(?P<t_STARTTOKEN>\\+)|(?P<t_RBRACK>\\])|(?P<t_RBRACE>})|(?P<t_EQ>=)|(?P<t_LBRACE>{)|(?P<t_SEMI>;)', [None, ('t_BLOCK_COMMENT', 'BLOCK_COMMENT'), None, ('t_NAME', 'NAME'), ('t_newline', 'newline'), ('t_newline2', 'newline2'), None, (None, 'STRING_LITERAL'), None, None, (None, 'NUM'), (None, None), (None, 'RPAR'), (None, 'DOT'), (None, 'LPAR'), (None, 'LBRACK'), (None, 'STARTTOKEN'), (None, 'RBRACK'), (None, 'RBRACE'), (None, 'EQ'), (None, 'LBRACE'), (None, 'SEMI')])]}
_lexstateignore = {'INITIAL': ' \t\x0c'}
_lexstateerrorf = {'INITIAL': 't_error'}
