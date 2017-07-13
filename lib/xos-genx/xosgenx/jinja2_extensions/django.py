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
            d = {}
            if isinstance(field['through'], str):
                split = field['through'].rsplit('.',1)
                d['name'] = split[-1]
                if len(split)==2:
                    d['package'] = split[0]
                    d['fqn'] = 'package' + '.' + d['name']
                else:
                    d['fqn'] = d['name']
                    d['package'] = ''
            else:
                d = field['through']

            if not d['name'].endswith('_'+field['name']):
                output_dict['through'] = '%r'%d['fqn']
    except KeyError:
        pass

    return format_options_string(output_dict)

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

def xproto_django_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if (dport=='_'):
        dport = '+'

    if (dport and (dport=='+' or '+' not in dport)):
        output_dict['related_name'] = '%r'%dport

    return format_options_string(output_dict)
