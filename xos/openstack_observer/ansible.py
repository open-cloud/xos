#!/usr/bin/env python
import jinja2
import tempfile
import os
import json
import pdb
import string
import random
import re
import traceback
import subprocess
from xos.config import Config, XOS_DIR

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

def run_template(name, opts,path='', expected_num=None, ansible_config=None, ansible_hosts=None, run_ansible_script=None):
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

    # This is messy -- there's no way to specify ansible config file from
    # the command line, but we can specify it using the environment.
    env = os.environ.copy()
    if ansible_config:
       env["ANSIBLE_CONFIG"] = ansible_config
    if ansible_hosts:
       env["ANSIBLE_HOSTS"] = ansible_hosts

    if (not Config().observer_pretend):
        if not run_ansible_script:
            run_ansible_script = os.path.join(XOS_DIR, "/observer/run_ansible")

        #run = os.popen(XOS_DIR + '/observer/run_ansible %s'%shellquote(fqp), env=env)
        run = subprocess.Popen("%s %s" % (run_ansible_script, shellquote(fqp)), shell=True, stdout=subprocess.PIPE, env=env).stdout
        msg = run.read()
        status = run.close()

        
    else:
        msg = open(fqp+'.out').read()

    try:
        ok_results = parse_output(msg)
        if (expected_num is not None) and (len(ok_results) != expected_num):
            raise ValueError('Unexpected num %s!=%d' % (str(expected_num), len(ok_results)) )
    except ValueError,e:
        all_fatal = [e.message] + re.findall(r'^msg: (.*)',msg,re.MULTILINE)
        all_fatal2 = re.findall(r'^ERROR: (.*)',msg,re.MULTILINE)

        all_fatal.extend(all_fatal2)
        try:
            error = ' // '.join(all_fatal)
        except:
            pass
        raise Exception(error)

    return ok_results

def run_template_ssh(name, opts, path='', expected_num=None):
    instance_id = opts["instance_id"]
    sliver_name = opts["sliver_name"]
    hostname = opts["hostname"]
    private_key = opts["private_key"]

    (private_key_handle, private_key_pathname) = tempfile.mkstemp()
    (config_handle, config_pathname) = tempfile.mkstemp()
    (hosts_handle, hosts_pathname) = tempfile.mkstemp()

    try:
        proxy_command = "ProxyCommand ssh -q -i %s %s@%s" % (private_key_pathname, instance_id, hostname)

        os.write(private_key_handle, private_key)
        os.close(private_key_handle)

        os.write(config_handle, "[ssh_connection]\n")
        os.write(config_handle, 'ssh_args = -o "%s"\n' % proxy_command)
        os.write(config_handle, 'scp_if_ssh = True\n')
        os.close(config_handle)

        os.write(hosts_handle, "[%s]\n" % sliver_name)
        os.write(hosts_handle, "%s ansible_ssh_private_key_file=%s\n" % (hostname, private_key_pathname))
        os.close(hosts_handle)

        print "ANSIBLE_CONFIG=%s" % config_pathname
        print "ANSIBLE_HOSTS=%s" % hosts_pathname

        return run_template(name, opts, path, expected_num, ansible_config = config_pathname, ansible_hosts = hosts_pathname, run_ansible_script="/opt/xos/observer/run_ansible_verbose")

    finally:
        #os.remove(private_key_pathname)
        #os.remove(config_pathname)
        #os.remove(hosts_pathname)
        pass



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
