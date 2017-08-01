from base import xproto_string_type, unquote

def xproto_type_to_ui_type(f):
    try:
        content_type = f['options']['content_type']
        content_type = eval(content_type)
    except:
        content_type = None
        pass

    if 'choices' in f['options']:
        return 'select';
    elif content_type == 'date':
        return 'date'
    elif f['type'] == 'bool':
        return 'boolean'
    elif f['type'] == 'string':
        return xproto_string_type(f['options'])
    elif f['type'] in ['int','uint32','int32'] or 'link' in f:
        return 'number'
    elif f['type'] in ['double','float']:
        return 'string'

def xproto_options_choices_to_dict(choices):
    list = []

    for c in eval(choices):
        list.append({'id': c[0], 'label': c[1]})
    if len(list) > 0:
        return list
    else:
        return None

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def xproto_default_to_gui(default):
    val = "null"
    if is_number(default):
        val = str(default)
    elif eval(default) == True:
        val = 'true'
    elif eval(default) == False:
        val = 'false'
    elif eval(default) == None:
        val = 'null'
    else:
        val = str(default)
    return val