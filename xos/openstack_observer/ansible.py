#!/usr/bin/env python
import jinja2
import tempfile
import os
import json
import pdb
import string
import random
import re

# XXX hardcoded path
#    is there any reason why we aren't importing xos.config ?
XOS_DIR="/opt/xos"

try:
    step_dir = Config().observer_steps_dir
    sys_dir = Config().observer_sys_dir
except:
    step_dir = XOS_DIR + '/observer/steps'
    sys_dir = '/opt/opencloud'

os_template_loader = jinja2.FileSystemLoader( searchpath=step_dir)
os_template_env = jinja2.Environment(loader=os_template_loader)

def parse_output(msg):
    lines = msg.splitlines()
    results = []
    print msg

    for l in lines:
        magic_str = 'ok: [127.0.0.1] => '
        magic_str2 = 'changed: [127.0.0.1] => '
        if (l.startswith(magic_str)):
            w = len(magic_str)
            str = l[w:]
            d = json.loads(str)
            results.append(d)
        elif (l.startswith(magic_str2)):
            w = len(magic_str2)
            str = l[w:]
            d = json.loads(str)
            results.append(d)


    return results

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def run_template(name, opts,path='', expected_num=None):
    template = os_template_env.get_template(name)
    buffer = template.render(opts)

    try:
        objname = opts['ansible_tag']
    except:
        objname= id_generator()

    os.system('mkdir -p %s'%'/'.join([sys_dir,path]))
    fqp = '/'.join([sys_dir,path,objname])


    f = open(fqp,'w')
    f.write(buffer)
    f.flush()

    
    if (Config().observer_steps):
        run = os.popen(XOS_DIR + '/observer/run_ansible %s'%shellquote(fqp))
        msg = run.read()
        status = run.close()

        
    else:
        msg = open(fqp+'.out').read()
        
    try:
        ok_results = parse_output(msg)
        if (len(ok_results) != expected_num):
            raise ValueError('Unexpected num')
    except ValueError,e:
        all_fatal = re.findall(r'^msg: (.*)',msg,re.MULTILINE)
        all_fatal2 = re.findall(r'^ERROR: (.*)',msg,re.MULTILINE)


        all_fatal.extend(all_fatal2)
        try:
            error = ' // '.join(all_fatal)
        except:
            pass
        raise Exception(error)

    return ok_results

def main():
    run_template('ansible/sync_user_deployments.yaml',{ "endpoint" : "http://172.31.38.128:5000/v2.0/",
             "name" : "Sapan Bhatia",
             "email": "gwsapan@gmail.com",
             "password": "foobar",
             "admin_user":"admin",
             "admin_password":"6a789bf69dd647e2",
             "admin_tenant":"admin",
             "tenant":"demo",
             "roles":['user','admin'] })
