import plyproto.model as m
import pdb
import argparse
import plyproto.parser as plyproto
import traceback
import sys
import jinja2
import os


''' Proto2XProto overrides the underlying visitor pattern to transform the tree
    in addition to traversing it '''
class Proto2XProto(m.Visitor):
    stack = Stack()
    count_stack = Stack()
    content=""
    offset=0
    statementsChanged=0

    def map_field(self, obj, s):
        if 'model' in s:
            link = m.LinkDefinition('onetoone','src','name','dst', obj.linespan, obj.lexspan, obj.p)
            lspec = m.LinkSpec(link, obj)
        else:
            lspec = obj
        return lspec


    def get_stack(self):
        return stack

    def __init__(self):
        super(Proto2XProto, self).__init__()

        self.verbose = 0
        self.first_field = True
        self.first_method = True

    def visit_PackageStatement(self, obj):
        '''Ignore'''
        return True

    def visit_ImportStatement(self, obj):
        '''Ignore'''
        return True

    def visit_OptionStatement(self, obj):
        '''Ignore'''
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

        try:
            value = obj.value.value.pval
        except AttributeError:
            try:
                value = obj.value.value
            except AttributeError:
                value = obj.value.pval

        self.stack.push([name,value])
        return True

    def visit_FieldType(self, obj):
        return True

    def visit_LinkDefinition(self, obj):
        return True

    def visit_FieldDefinition(self, obj):
        self.count_stack.push(len(obj.fieldDirective))
        return True

    def visit_FieldDefinition_post(self, obj):
        opts = {}
        n = self.count_stack.pop()
        for i in range(0, n):
            k,v = self.stack.pop()
            opts[k] = v

        f = self.map_field(obj, s)
        self.stack.push(f)
        return True

    def visit_EnumFieldDefinition(self, obj):
        return True

    def visit_EnumDefinition(self, obj):
        return True

    def visit_MessageDefinition(self, obj):
        self.count_stack.push(len(obj.body))
        return True
    
    def visit_MessageDefinition_post(self, obj):
        stack_num = self.count_stack.pop()
        fields = []
        links = []
        for i in range(0,stack_num):
            f = self.stack.pop()
            if (f['_type']=='link'):
                links.insert(0,f)
            else:
                fields.insert(0,f)

        self.stack.push({'name':obj.name.value.pval,'fields':fields,'links':links})
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
