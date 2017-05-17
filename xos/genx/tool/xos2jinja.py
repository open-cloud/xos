import plyproto.model as m
import pdb
import argparse
import plyproto.parser as plyproto
import traceback
import sys
import jinja2
import os
import copy

def count_messages(body):
    count = 0
    for e in body:
        if (type(e)==m.MessageDefinition):
            count+=1
    return count

def count_fields(body):
    count = 0
    for e in body:
        if (type(e) in [m.LinkDefinition,m.FieldDefinition,m.LinkSpec]):
            count+=1
    return count

def compute_rlinks(messages):
    rev_links = {}

    link_opposite = {
            'manytomany': 'manytomany',
            'manytoone' : 'onetomany',
            'onetoone'  : 'onetoone',
            'onetomany' : 'manytoone'
    }

    for m in messages:
        for l in m['links']:
            rlink = copy.deepcopy(l)
            rlink['_type'] = 'rlink' # An implicit link, not declared in the model
            rlink['src_port'] = l['dst_port']
            rlink['dst_port'] = l['src_port']
            rlink['peer'] = m['name']
            rlink['link_type'] = link_opposite[l['link_type']]

            try:
                rev_links[l['peer']].append(rlink)
            except KeyError:
                rev_links[l['peer']] = [rlink]

    for m in messages:
        try:
            m['rlinks'] = rev_links[m['name']]
        except KeyError:
            pass

class Stack(list):
    def push(self,x):
        self.append(x)

''' XOS2Jinja overrides the underlying visitor pattern to transform the tree
    in addition to traversing it '''
class XOS2Jinja(m.Visitor):
    stack = Stack()
    models = {}
    options = {}
    message_options = {}
    count_stack = Stack()
    content=""
    offset=0
    current_message_name = None

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
        if not hasattr(obj,'mark_for_deletion'):
            if (self.current_message_name):
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

        try:
            s['link_type'] = obj.link_type.pval
        except AttributeError:
            s['link_type'] = obj.link_type

        s['src_port'] = obj.src_port.value.pval
        s['name'] = obj.src_port.value.pval

        try:
            s['dst_port'] = obj.dst_port.value.pval
        except AttributeError:
            s['dst_port'] = obj.dst_port


        try:
            s['through'] = obj.through.pval
        except AttributeError:
            s['through'] = obj.through

        try:
            s['peer'] = obj.name.pval
        except AttributeError:
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

            # The two lines below may be added to eliminate "" around an option. 
            # Right now, this is handled in targets. FIXME
            #
            # if (v.startswith('"') and v.endswith('"')):
            #    v = v[1:-1]

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
        last_field = None
        try:
            obj.bases = map(lambda x:x.pval, obj.bases)
        except AttributeError:
            pass

        for i in range(0,stack_num):
            f = self.stack.pop()
            if (f['_type']=='link'):
                f['options']={i:d[i] for d in [f['options'],last_field['options']] for i in d}

                links.insert(0,f)
            else:
                fields.insert(0,f)
                last_field = f

        model_def = {'name':obj.name.value.pval,'fields':fields,'links':links, 'bases':obj.bases, 'options':self.message_options}
        self.stack.push(model_def)
        self.models[obj.name.value.pval] = model_def
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
        for i in range(0,count):
            try:
                m = self.stack.pop()
            except IndexError:
                pass

            messages.insert(0,m)

        compute_rlinks(messages)
        self.messages = messages
        return True

    def visit_LinkSpec(self, obj):
        count = self.count_stack.pop()
        self.count_stack.push(count+1)
        return True
