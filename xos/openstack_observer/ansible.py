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

def parse_unreachable(msg):
    total_unreachable=0
    for l in msg.splitlines():
        x = re.findall('ok=([0-9]+).*changed=([0-9]+).*unreachable=([0-9]+).*failed=([0-9]+)', l)
        if x:
            (ok, changed, unreachable, failed) = x[0]
            ok=int(ok)
            changed=int(changed)
            unreachable=int(unreachable)
            failed=int(failed)

            total_unreachable += unreachable
    return total_unreachable


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def get_playbook_fn(opts, path):
    if not opts.get("ansible_tag", None):
        # if no ansible_tag is in the options, then generate a unique one
        objname= id_generator()
        opts = opts.copy()
        opts["ansible_tag"] = objname

    objname = opts["ansible_tag"]

    os.system('mkdir -p %s' % os.path.join(sys_dir, path))
    return (opts, os.path.join(sys_dir,path,objname))

def run_template(name, opts, path='', expected_num=None, ansible_config=None, ansible_hosts=None, run_ansible_script=None):
    template = os_template_env.get_template(name)
    buffer = template.render(opts)

    (opts, fqp) = get_playbook_fn(opts, path)

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
            run_ansible_script = os.path.join(XOS_DIR, "observer/run_ansible")

        process = subprocess.Popen("%s %s" % (run_ansible_script, shellquote(fqp)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        msg = process.stdout.read()
        err_msg = process.stderr.read()

        if getattr(Config(), "observer_save_ansible_output", False):
            try:
                open(fqp+".out","w").write(msg)
                open(fqp+".err","w").write(err_msg)
            except:
                # fail silently
                pass

    else:
        msg = open(fqp+'.out').read()

    try:
        ok_results = parse_output(msg)
        if (expected_num is not None) and (len(ok_results) != expected_num):
            raise ValueError('Unexpected num %s!=%d' % (str(expected_num), len(ok_results)) )

        total_unreachable = parse_unreachable(msg)
        if (total_unreachable > 0):
            raise ValueError("Unreachable results in ansible recipe")
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
    instance_name = opts["instance_name"]
    hostname = opts["hostname"]
    private_key = opts["private_key"]
    nat_ip = opts["nat_ip"]

    try:
        proxy_ssh = Config().observer_proxy_ssh
    except:
        proxy_ssh = True

    (opts, fqp) = get_playbook_fn(opts, path)
    private_key_pathname = fqp + ".key"
    config_pathname = fqp + ".config"
    hosts_pathname = fqp + ".hosts"

    f = open(private_key_pathname, "w")
    f.write(private_key)
    f.close()

    f = open(config_pathname, "w")
    f.write("[ssh_connection]\n")
    if proxy_ssh:
        proxy_command = "ProxyCommand ssh -q -i %s -o StrictHostKeyChecking=no %s@%s" % (private_key_pathname, instance_id, hostname)
        f.write('ssh_args = -o "%s"\n' % proxy_command)
    f.write('scp_if_ssh = True\n')
    f.write('pipelining = True\n')
    f.write('\n[defaults]\n')
    f.write('host_key_checking = False\n')
    f.close()

    f = open(hosts_pathname, "w")
    f.write("[%s]\n" % instance_name)
    if proxy_ssh:
        f.write("%s ansible_ssh_private_key_file=%s\n" % (hostname, private_key_pathname))
    else:
        # acb: Login user is hardcoded, this is not great
        f.write("%s ansible_ssh_private_key_file=%s ansible_ssh_user=ubuntu\n" % (nat_ip, private_key_pathname))
    f.close()

    # SSH will complain if private key is world or group readable
    os.chmod(private_key_pathname, 0600)

    print "ANSIBLE_CONFIG=%s" % config_pathname
    print "ANSIBLE_HOSTS=%s" % hosts_pathname

    return run_template(name, opts, path, expected_num, ansible_config = config_pathname, ansible_hosts = hosts_pathname, run_ansible_script="/opt/xos/observer/run_ansible_verbose")



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
