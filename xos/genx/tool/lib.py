import pdb
import re
from pattern import en

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

def xproto_pluralize(field):
    try:
        # The user has set a plural, as an exception that cannot be handled automatically
        plural = field['options']['plural']
        plural = unquote(plural)
    except KeyError:
        plural = en.pluralize(field['name'])

    return plural

def xproto_unquote(s):
    if (s.startswith('"') and s.endswith('"')):
        s = s[1:-1]
    return s

def xproto_links_to_modeldef_relations(llst):
    outlist = []
    seen = []
    for l in llst:
        try:
            t = l['link_type']
        except KeyError, e:
            raise e

        if l['peer'] not in seen and t!='manytomany':
            outlist.append('- {model: %s, type: %s}\n'%(l['peer'], l['link_type']))
        seen.append(l['peer'])
    
    return outlist

def django_content_type_string(xptags):
    # Check possibility of KeyError in caller
    content_type = xptags['content_type']

    try:
        content_type = eval(content_type)
    except:
        pass

    if (content_type=='url'):
        return 'URLField'
    if (content_type=='date'):
        return 'DateTimeField'
    elif (content_type=='ip'):
        return 'GenericIPAddressField'
    elif (content_type=='stripped' or content_type=='"stripped"'):
        return 'StrippedCharField'
    else:
        raise Exception('Unknown Type: %s'%content_type)

def django_string_type(xptags):
    try:
        max_length = eval(xptags['max_length'])
    except:
        max_length = 1024 * 1024

    if ('content_type' in xptags):
        return django_content_type_string(xptags)
    elif (max_length<1024*1024):
        return 'CharField'
    else:
        return 'TextField'

def xproto_base_def(model_name, base):
    if (model_name=='XOSBase'):
        return '(models.Model, PlModelMixIn)'
    elif (not base):
        return ''
    else:
        return '(' + ','.join(base) + ')'

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

def xproto_django_type(xptype, xptags):
    if (xptype=='string'):
        return django_string_type(xptags)
    elif (xptype=='float'):
        return 'FloatField'
    elif (xptype=='bool'):
        return 'BooleanField'
    elif (xptype=='uint32'):
        return 'IntegerField'
    elif (xptype=='int32'):
        return 'IntegerField'
    elif (xptype=='int64'):
        return 'BigIntegerField'
    else:
        raise Exception('Unknown Type: %s'%xptype)



def xproto_django_link_type(f):
    if (f['link_type']=='manytoone'):
        return 'ForeignKey'
    elif (f['link_type']=='manytomany'):
        if (f['dst_port']):
            return 'ManyToManyField'
        else:
            return 'GenericRelation'

def format_options_string(d):
    if (not d):
        return ''
    else:

        lst = []
        for k,v in d.items():
            if (type(v)==str and k=='default' and v.endswith('()"')):
                lst.append('%s = %s'%(k,v[1:-3]))
            elif (type(v)==str and v.startswith('"')): 
                try:
                    tup = eval(v[1:-1])
                    if (type(tup)==tuple):
                        lst.append('%s = %r'%(k,tup))
                    else:
                        lst.append('%s = %s'%(k,v))
                except:
                    lst.append('%s = %s'%(k,v))
            elif (type(v)==bool):
                lst.append('%s = %r'%(k,bool(v)))
            else:
                try:
                    lst.append('%s = %r'%(k,int(v)))
                except ValueError:
                    lst.append('%s = %s'%(k,v))

        return ', '.join(lst)

def map_xproto_to_django(f):
    allowed_keys=['help_text','default','max_length','modifier','blank','choices','db_index','null','editable','on_delete','verbose_name', 'auto_now_add']

    m = {'modifier':{'optional':True, 'required':False, '_target':'null'}}
    out = {}

    for k,v in f['options'].items():
        if (k in allowed_keys):
            try:
                kv2 = m[k]
                out[kv2['_target']] = kv2[v]
            except:
                out[k] = v
    return out


def xproto_django_link_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if (dport and (dport=='+' or '+' not in dport)):
        output_dict['related_name'] = '%r'%dport

    try:
        if field['through']:
            if not field['through'].endswith('_'+field['name']):
                output_dict['through'] = '%r'%field['through']
    except KeyError:
        pass

    return format_options_string(output_dict)

def xproto_django_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if (dport=='_'):
        dport = '+'

    if (dport and (dport=='+' or '+' not in dport)):
        output_dict['related_name'] = '%r'%dport

    return format_options_string(output_dict)

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
        if b in table:
            base_fields = xproto_base_fields(table[b], table)

            model_fields = table[b]['fields']
            fields.extend(base_fields)
            fields.extend(model_fields)

    return fields

def xproto_base_links(m, table):
    links = []

    for b in m['bases']:
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
            validators.append({'name':v1, 'int_value':f['options'][v0]})
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
