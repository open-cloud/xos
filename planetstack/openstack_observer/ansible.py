#!/usr/bin/python
import jinja2
import tempfile
import os
import json

try:
    step_dir = Config().observer_steps_dir
except:
    step_dir = '/opt/planetstack/observer/steps'

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
	    
def run_template(name, opts):
    template = os_template_env.get_template(name)
    buffer = template.render(opts)
    
    f = tempfile.NamedTemporaryFile(mode='w')
    f.write(buffer)
    f.flush()
    
    run = os.popen('/opt/planetstack/observer/run_ansible '+f.name)
    msg = run.read()
    status = run.close()

    try:
    	ok_results = parse_output(msg)
    except ValueError,e:
	print str(e)
	raise e
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
