import pdb

def django_content_type_string(xptags):
    # Check possibility of KeyError in caller
    content_type = xptags['content_type']

    if (content_type=='url'):
        return 'URLField'
    elif (content_type=='ip'):
        return 'GenericIPAddressField'
    elif (content_type=='stripped' or content_type=='"stripped"'):
        return 'StrippedCharField'

def django_string_type(xptags):
    if ('content_type' in xptags):
        return django_content_type_string(xptags)
    elif ('indexed' not in xptags):
        return 'TextField'
    else:
        return 'CharField'

def xproto_base_def(base):
    if (not base):
        return ''
    else:
        return '(' + ','.join(base) + ')'

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
            return 'ManyToManyRelation'
        else:
            return 'GenericRelation'

def format_options_string(d):
    if (not d):
        return ''
    else:
        lst = []
        for k,v in d.items():
            if (type(v)==str and v.startswith('"')): 
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
    allowed_keys=['help_text','default','max_length','modifier','blank','choices','db_index','null'] 

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


def xproto_django_options_str(field, dport=None):
    output_dict = map_xproto_to_django(field)

    if (dport=='_'):
        dport = '+'

    if (dport):
        output_dict['related_name'] = '%r'%dport
    return format_options_string(output_dict)
