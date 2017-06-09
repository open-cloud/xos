import plyxproto.model as m
import pdb
import argparse
import plyxproto.parser as plyxproto
import traceback
import sys
import jinja2
import os

class Stack(list):
    def push(self,x):
        self.append(x)

def str_to_dict(s):
    lst = s.rsplit('.',1)
    name = lst[-1]

    if len(lst)==2:
        package = lst[0]
    else:
        package = ''

    return {'name': name, 'package': package, 'fqn': s}

def replace_link(obj):
        try:
            link = obj.link
            try:
                through = link['through']
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

            model_dict = str_to_dict(link['model'][1:-1])

            ls = m.LinkSpec(obj, m.LinkDefinition(link['link'][1:-1],obj.name,model_dict,link['port'][1:-1],through_dict))
            return ls
        except:
            return obj

class Proto2XProto(m.Visitor):
    def __init__(self):
        super(Proto2XProto, self).__init__()

        self.stack = Stack()
        self.count_stack = Stack()
        self.content=""
        self.offset=0
        self.statementsChanged=0
        self.message_options = {}
        self.options = {}
        self.current_message_name = None

        self.xproto_message_options = ['bases']
        self.xproto_field_options = ['model']
        self.verbose = 0
        self.first_field = True
        self.first_method = True
    
    def proto_to_xproto_field(self, obj):
        try:
            opts = {}
            for fd in obj.fieldDirective:
                k = fd.pval.name.value.pval
                v = fd.pval.value.value.pval
                opts[k]=v

            if ('model' in opts and 'link' in opts and 'port' in opts):
                obj.link = opts
            pass
        except KeyError:
            raise

    def proto_to_xproto_message(self, obj):
        try:
            bases = self.message_options['bases'].split(',')
            bases = map(lambda x:str_to_dict(x[1:-1]), bases)
            obj.bases = bases
        except KeyError:
            raise

    def map_field(self, obj, s):
        if 'model' in s:
            link = m.LinkDefinition('onetoone','src','name','dst', obj.linespan, obj.lexspan, obj.p)
            lspec = m.LinkSpec(link, obj)
        else:
            lspec = obj
        return lspec


    def get_stack(self):
        return self.stack

    def visit_PackageStatement(self, obj):
        '''Ignore'''
        return True

    def visit_ImportStatement(self, obj):
        '''Ignore'''
        return True

    def visit_OptionStatement(self, obj):
        if (self.current_message_name):
            k = obj.name.value.pval
            self.message_options[k] = obj.value.value.pval
            if (k in self.xproto_message_options):
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
        obj.body = filter(lambda x:not hasattr(x, 'mark_for_deletion'), obj.body)
        obj.body = map(replace_link, obj.body)

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
        return True

    def visit_LinkSpec(self, obj):
        return False
