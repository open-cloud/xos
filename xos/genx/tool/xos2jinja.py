import plyproto.model as m
import pdb
import argparse
import plyproto.parser as plyproto
import traceback
import sys
import jinja2
import os

class Stack(list):
    def push(self,x):
        self.append(x)

''' XOS2Jinja overrides the underlying visitor pattern to transform the tree
    in addition to traversing it '''
class XOS2Jinja(m.Visitor):
    stack = Stack()
    count_stack = Stack()
    content=""
    offset=0
    doNameSanitization=False
    statementsChanged=0
    prefix=""

    def get_stack(self):
        return stack

    def __init__(self):
        super(XOS2Jinja, self).__init__()

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
        '''Field type, if type is name, then it may need refactoring consistent with refactoring rules according to the table'''
        return True

    def visit_LinkDefinition(self, obj):
        s={}

        s['link_type'] = obj.link_type.pval
        s['src_port'] = obj.src_port.value.pval
        s['name'] = obj.src_port.value.pval
        try:
            s['dst_port'] = obj.dst_port.value.pval
        except AttributeError:
            s['dst_port'] = ''
        s['peer'] = obj.name
        s['_type'] = 'link'
        s['options'] = {'modifier':'optional'}

        self.stack.push(s)
        return True

    def visit_FieldDefinition(self, obj):
        self.count_stack.push(len(obj.fieldDirective))
        return True

    def visit_FieldDefinition_post(self, obj):
        s= {}
        
        if isinstance(obj.ftype, m.Name):
            s['type'] = obj.ftype.value
        else:
            s['type'] = obj.ftype.name.pval
        s['name'] = obj.name.value.pval
        s['modifier'] = obj.field_modifier.pval
        s['id'] = obj.fieldId.pval

        opts = {'modifier':s['modifier']}
        n = self.count_stack.pop()
        for i in range(0, n):
            k,v = self.stack.pop()
            opts[k] = v

        s['options'] = opts
        try:
            last_link = self.stack[-1]['_type']
            if (last_link=='link'):
                s['link'] = True
        except:
            pass
        s['_type'] = 'field'

        self.stack.push(s)
        return True

    def visit_EnumFieldDefinition(self, obj):
        if self.verbose > 4:
            print "\tEnumField: name=%s, %s" % (obj.name, obj)

        return True

    def visit_EnumDefinition(self, obj):
        '''New enum definition, refactor name'''
        if self.verbose > 3:
            print "Enum, [%s] body=%s\n\n" % (obj.name, obj.body)

        self.prefixize(obj.name, obj.name.value)
        return True

    def visit_MessageDefinition(self, obj):
        self.count_stack.push(len(obj.body))
        return True
    
    def visit_MessageDefinition_post(self, obj):
        stack_num = self.count_stack.pop()
        fields = []
        links = []
        last_field = None
        obj.bases = map(lambda x:x.pval, obj.bases)

        for i in range(0,stack_num):
            f = self.stack.pop()
            if (f['_type']=='link'):
                f['options']={i:d[i] for d in [f['options'],last_field['options']] for i in d}

                links.insert(0,f)
            else:
                fields.insert(0,f)
                last_field = f

        self.stack.push({'name':obj.name.value.pval,'fields':fields,'links':links, 'bases':obj.bases})
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
        count = self.count_stack.pop()
        messages = []
        for i in range(0,count):
            m = self.stack.pop()
            messages.insert(0,m)

        self.messages = messages
        return True

    def visit_LinkSpec(self, obj):
        count = self.count_stack.pop()
        self.count_stack.push(count+1)
        return True
