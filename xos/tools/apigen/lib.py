import pdb

def format_options_string(d):
    if (not d): return ''
    lst = []
    try:
	    for k,v in d.items():
               if (type(v)==int or type(v)==bool or type(v)==float):
	          lst.append('%s = %r'%(k,v))
               else:
                  lst.append('%s = "%s"'%(k,v))
    except:
            pass
    return '['+', '.join(lst)+']'
    

def map_django_to_xproto(f):
    allowed_keys=['help_text','default','max_length','choices','blank','null','related_name','db_index']

    m = {'help_text':{'_target':'help_text','':None}}
    out = {}

    for k in allowed_keys:
        try:
           v = getattr(f,k)
        except:
           continue

        if (k=='choices' and v==[]):
           continue

        if (k=='default' and type(v)==float): 
           pass

        if (k=='default' and 'function' in type(v).__name__):
           v = v.__name__+"()"

        try:
            n = v.__name__
        except AttributeError: 
            n = None
        if (v is None or n=='NOT_PROVIDED'): 
	    continue
       
        if (k in allowed_keys):
            try:
                kv2 = m[k]
                if (kv2[v] is None):
                   continue

                out[kv2['_target']] = kv2[v]
            except:
                out[k] = v
    return out


def xp_options(field):
    output_dict = map_django_to_xproto(field)
    t0 = field.type

    if (t0=='StrippedCharField'):
        ctype = 'stripped'
    elif (t0=='URLField'):
        ctype = 'url'
    elif (t0=='DateTimeField'):
        ctype = 'date'
    elif (t0=='GenericIPAddressField'):
        ctype = 'ip'
    else:
        ctype = None

    if (ctype):
        output_dict['content_type'] =  ctype


    return format_options_string(output_dict)
    
def xp_to_xproto(field, idx):
    t = field.get_internal_type()
    link = False

    if (t=='CharField' or t=='TextField' or t=='SlugField'):
        xptype = 'string'
    elif (t=='BooleanField'):
        xptype = 'bool'
    elif (t=='ForeignKey'):
        xptype = 'manytoone'
        peer = field.related.model.__name__
        if (field.related.name):
            dst_port = ':' + field.related.name
        else:
            dst_port = ''
        link = True
    elif (t=='DateTimeField'):
        xptype = 'string'
    elif (t=='AutoField'):
        xptype = 'int32'
    elif (t=='BigIntegerField'):
        xptype = 'int32'
    elif (t=='IntegerField'):
        xptype = 'int32'
    elif (t=='PositiveIntegerField'):
        xptype = 'uint32'
    elif (t=='FloatField'):
        xptype = 'float'
    elif (t=='GenericIPAddressField'):
        xptype = 'string'
    elif (t=='OneToOneField'):
        link = True
 
    
    if (field.null==False):
       modifier = 'required'
    else: 
       modifier = 'optional'

    if (link):
       str = '%s %s %s->%s%s = %d'%(modifier, xptype, field.name, peer, dst_port, idx)
    else:
       str = '%s %s %s = %d'%(modifier, xptype, field.name, idx)

    return str

