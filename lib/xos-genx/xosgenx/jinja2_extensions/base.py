import pdb
import re
from pattern import en

class FieldNotFound(Exception):
    def __init__(self, message):
        super(FieldNotFound, self).__init__(message)

def xproto_debug(**kwargs):
    print kwargs
    pdb.set_trace()

def xproto_unquote(s):
    return unquote(s)

def unquote(s):
    if (s.startswith('"') and s.endswith('"')):
        return s[1:-1]

def xproto_singularize(field):
    try:
        # The user has set a singular, as an exception that cannot be handled automatically
        singular = field['options']['singular']
        singular = unquote(singular)
    except KeyError:
        singular = en.singularize(field['name'])

    return singular

def xproto_singularize_pluralize(field):
    try:
        # The user has set a plural, as an exception that cannot be handled automatically
        plural = field['options']['plural']
        plural = unquote(plural)
    except KeyError:
        plural = en.pluralize(en.singularize(field['name']))

    return plural

def xproto_pluralize(field):
    try:
        # The user has set a plural, as an exception that cannot be handled automatically
        plural = field['options']['plural']
        plural = unquote(plural)
    except KeyError:
        plural = en.pluralize(field['name'])

    return plural

def xproto_links_to_modeldef_relations(llst):
    outlist = []
    seen = []
    for l in llst:
        try:
            t = l['link_type']
        except KeyError, e:
            raise e

        if l['peer']['fqn'] not in seen and t!='manytomany':
            outlist.append('- {model: %s, type: %s}\n'%(l['peer']['name'], l['link_type']))
        seen.append(l['peer'])
    
    return outlist


def xproto_base_def(model_name, base, suffix='', suffix_list=[]):
    if (model_name=='XOSBase'):
        return '(models.Model, PlModelMixIn)'
    elif (not base):
        return ''
    else:
        int_base = [i['name']+suffix for i in base if i['name'] in suffix_list]
        ext_base = [i['name'] for i in base if i['name'] not in suffix_list]
        return '(' + ','.join(int_base + ext_base) + ')'

def xproto_first_non_empty(lst):
    for l in lst:
        if l: return l

def xproto_api_type(field):
    try:
        if (unquote(field['options']['content_type'])=='date'):
            return 'float'
    except KeyError:
        pass

    return field['type']


def xproto_base_name(n):
    # Hack - Refactor NetworkParameter* to make this go away
    if (n.startswith('NetworkParameter')):
        return '_'

    expr = r'^[A-Z]+[a-z]*'

    try:
        match = re.findall(expr, n)[0]
    except:
        return '_'

    return match

def xproto_base_fields(m, table):
    fields = []

    for b in m['bases']:
        option1 = b['fqn']
        try:
            option2 = m['package'] + '.' + b['name']
        except TypeError:
            option2 = option1

        accessor = None
        if option1 in table: accessor = option1
        elif option2 in table: accessor = option2

        if accessor:
            base_fields = xproto_base_fields(table[accessor], table)

            model_fields = table[accessor]['fields']
            fields.extend(base_fields)
            fields.extend(model_fields)

    return fields

def xproto_base_rlinks(m, table):
    links = []

    for base in m['bases']:
        b = base['name']
        if b in table:
            base_rlinks = xproto_base_rlinks(table[b], table)

            model_rlinks = table[b]['rlinks']
            links.extend(base_rlinks)
            links.extend(model_rlinks)

    return links

def xproto_base_links(m, table):
    links = []

    for base in m['bases']:
        b = base['name']
        if b in table:
            base_links = xproto_base_links(table[b], table)

            model_links = table[b]['links']
            links.extend(base_links)
            links.extend(model_links)
    return links


def xproto_validators(f):
    # To be cleaned up when we formalize validation in xproto
    validators = []

    # bound-based validators
    bound_validators = [('max_length','maxlength'), ('min', 'min'), ('max', 'max')]

    for v0, v1 in bound_validators:
        try:
            validators.append({'name':v1, 'int_value':int(f['options'][v0])})
        except KeyError:
            pass

    # validators based on content_type
    content_type_validators = ['ip', 'url', 'email']

    for v in content_type_validators:
        #if f['name']=='ip': pdb.set_trace()
        try:
            val = unquote(f['options']['content_type'])==v
            if not val:
                raise KeyError

            validators.append({'name':v, 'bool_value': True})
        except KeyError:
            pass

    # required validator
    try:
        required = f['options']['blank']=='False' and f['options']['null']=='False'
        if required:
            validators.append({'name':'required', 'bool_value':required})
    except KeyError:
        pass

    return validators

def xproto_string_type(xptags):
    try:
        max_length = eval(xptags['max_length'])
    except:
        max_length = 1024

    if ('varchar' not in xptags):
        return 'string'
    else:
        return 'text'

def xproto_type_to_ui_type(f):
    try:
        content_type = f['options']['content_type']
        content_type = eval(content_type)
    except:
        content_type = None
        pass

    if content_type == 'date':
        return 'date'
    elif f['type'] == 'bool':
        return 'boolean'
    elif f['type'] == 'string':
        return xproto_string_type(f['options'])
    elif f['type'] in ['int','uint32','int32'] or 'link' in f:
        return 'number'
    elif f['type'] in ['double','float']:
        return 'string'

def xproto_tuplify(nested_list_or_set):
    if not isinstance(nested_list_or_set, list) and not isinstance(nested_list_or_set, set):
        return nested_list_or_set
    else:
        return tuple([xproto_tuplify(i) for i in nested_list_or_set])

def xproto_field_graph_components(fields, tag='unique_with'):
    def find_components(graph):
        pending = set(graph.keys())
        components = []

        while pending:
            front = { pending.pop() }
            component = set()

            while front:
                node = front.pop()
                neighbours = graph[node]
                neighbours-=component # These we have already visited
                front |= neighbours

                pending-=neighbours
                component |= neighbours
            
            components.append(component)

        return components

    field_graph = {}
    field_names = {f['name'] for f in fields}

    for f in fields:
        try:
            tagged_str = unquote(f['options'][tag])
            tagged_fields = tagged_str.split(',')

            for uf in tagged_fields:
                if uf not in field_names:
                    raise FieldNotFound('Field %s not found'%uf)

                field_graph.setdefault(f['name'],set()).add(uf)
                field_graph.setdefault(uf,set()).add(f['name'])
        except KeyError:
            pass

    components = find_components(field_graph)
    return components

def xproto_api_opts(field):
    options = []
    if 'max_length' in field['options'] and field['type']=='string':
        options.append('(val).maxLength = %s'%field['options']['max_length'])

    try:
        if field['options']['null'] == 'False':
            options.append('(val).nonNull = true')
    except KeyError:
        pass

    if 'link' in field and 'model' in field['options']:
        options.append('(foreignKey).modelName = "%s"'%field['options']['model'])

    if options:
        options_str = '[' + ', '.join(options) + ']'
    else:
        options_str = ''

    return options_str

def xproto_tosca_required(null, blank, default=None):

    if null == 'True' or blank == 'True' or default != 'False':
        return "false"
    return "true"

def xproto_tosca_field_type(type):
    """
    TOSCA requires fields of type 'bool' to be 'boolean'
    """
    if type == "bool":
        return "boolean"
    else:
        return type
