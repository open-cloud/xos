#!/usr/bin/env python

# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function

import json
import os
import pickle
import random
import string
import tempfile

import jinja2

from multistructlog import create_logger
from xosconfig import Config
from six.moves import range

log = create_logger(Config().get("logging"))


step_dir = Config.get("steps_dir")
sys_dir = Config.get("sys_dir")

os_template_loader = jinja2.FileSystemLoader(
    searchpath=[step_dir, "/opt/xos/synchronizers/shared_templates"]
)
os_template_env = jinja2.Environment(loader=os_template_loader)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def get_playbook_fn(opts, path):
    if not opts.get("ansible_tag", None):
        # if no ansible_tag is in the options, then generate a unique one
        objname = id_generator()
        opts = opts.copy()
        opts["ansible_tag"] = objname

    objname = opts["ansible_tag"]

    pathed_sys_dir = os.path.join(sys_dir, path)
    if not os.path.isdir(pathed_sys_dir):
        os.makedirs(pathed_sys_dir)

    # symlink steps/roles into sys/roles so that playbooks can access roles
    roledir = os.path.join(step_dir, "roles")
    rolelink = os.path.join(pathed_sys_dir, "roles")
    if os.path.isdir(roledir) and not os.path.islink(rolelink):
        os.symlink(roledir, rolelink)

    return (opts, os.path.join(pathed_sys_dir, objname))


def run_playbook(ansible_hosts, ansible_config, fqp, opts):
    args = {
        "ansible_hosts": ansible_hosts,
        "ansible_config": ansible_config,
        "fqp": fqp,
        "opts": opts,
        "config_file": Config.get_config_file(),
    }

    keep_temp_files = Config.get("keep_temp_files")

    dir = tempfile.mkdtemp()
    args_fn = None
    result_fn = None
    try:
        log.info("creating args file", dir=dir)

        args_fn = os.path.join(dir, "args")
        result_fn = os.path.join(dir, "result")

        open(args_fn, "w").write(pickle.dumps(args))

        ansible_main_fn = os.path.join(os.path.dirname(__file__), "ansible_main.py")

        os.system("python %s %s %s" % (ansible_main_fn, args_fn, result_fn))

        result = pickle.loads(open(result_fn).read())

        if hasattr(result, "exception"):
            log.error("Exception in playbook", exception=result["exception"])

        stats = result.get("stats", None)
        aresults = result.get("aresults", None)
    except BaseException:
        log.exception("Exception running ansible_main")
        stats = None
        aresults = None
    finally:
        if not keep_temp_files:
            if args_fn and os.path.exists(args_fn):
                os.remove(args_fn)
            if result_fn and os.path.exists(result_fn):
                os.remove(result_fn)
            os.rmdir(dir)

    return (stats, aresults)


def run_template(
    name,
    opts,
    path="",
    expected_num=None,
    ansible_config=None,
    ansible_hosts=None,
    run_ansible_script=None,
    object=None,
):
    template = os_template_env.get_template(name)
    buffer = template.render(opts)

    (opts, fqp) = get_playbook_fn(opts, path)

    f = open(fqp, "w")
    f.write(buffer)
    f.flush()

    """
    q = Queue()
    p = Process(target=run_playbook, args=(ansible_hosts, ansible_config, fqp, opts, q,))
    p.start()
    stats,aresults = q.get()
    p.join()
    """
    stats, aresults = run_playbook(ansible_hosts, ansible_config, fqp, opts)

    error_msg = []

    output_file = fqp + ".out"
    try:
        if aresults is None:
            raise ValueError("Error executing playbook %s" % fqp)

        ok_results = []
        total_unreachable = 0
        failed = 0

        ofile = open(output_file, "w")

        for x in aresults:
            if not x.is_failed() and not x.is_unreachable() and not x.is_skipped():
                ok_results.append(x)
            elif x.is_unreachable():
                failed += 1
                total_unreachable += 1
                try:
                    error_msg.append(x._result["msg"])
                except BaseException:
                    pass
            elif x.is_failed():
                failed += 1
                try:
                    error_msg.append(x._result["msg"])
                except BaseException:
                    pass

            # FIXME (zdw, 2017-02-19) - may not be needed with new callback logging

            ofile.write("%s: %s\n" % (x._task, str(x._result)))

            if object:
                oprops = object.tologdict()
                ansible = x._result
                oprops["xos_type"] = "ansible"
                oprops["ansible_result"] = json.dumps(ansible)

                if failed == 0:
                    oprops["ansible_status"] = "OK"
                else:
                    oprops["ansible_status"] = "FAILED"

                log.info("Ran Ansible task", task=x._task, **oprops)

        ofile.close()

        if (expected_num is not None) and (len(ok_results) != expected_num):
            raise ValueError(
                "Unexpected num %s!=%d" % (str(expected_num), len(ok_results))
            )

        if failed:
            raise ValueError("Ansible playbook failed.")

        # NOTE(smbaker): Playbook errors are slipping through where `aresults` does not show any failed tasks, but
        # `stats` does show them. See CORD-3169.
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            if t["unreachable"] > 0:
                raise ValueError(
                    "Ansible playbook reported unreachable for host %s" % h
                )
            if t["failures"] > 0:
                raise ValueError("Ansible playbook reported failures for host %s" % h)

    except ValueError:
        if error_msg:
            try:
                error = " // ".join(error_msg)
            except BaseException:
                error = "failed to join error_msg"
            raise Exception(error)
        else:
            raise

    processed_results = [x._result for x in ok_results]
    return processed_results[1:]  # 0 is setup


def run_template_ssh(name, opts, path="", expected_num=None, object=None):
    instance_name = opts["instance_name"]
    hostname = opts["hostname"]
    private_key = opts["private_key"]
    baremetal_ssh = opts.get("baremetal_ssh", False)
    if baremetal_ssh:
        # no instance_id or ssh_ip for baremetal
        # we never proxy to baremetal
        proxy_ssh = False
    else:
        instance_id = opts["instance_id"]
        ssh_ip = opts["ssh_ip"]
        proxy_ssh = Config.get("proxy_ssh.enabled")

        if not ssh_ip:
            raise Exception("IP of ssh proxy not available. Synchronization deferred")

    (opts, fqp) = get_playbook_fn(opts, path)
    private_key_pathname = fqp + ".key"
    config_pathname = fqp + ".cfg"
    hosts_pathname = fqp + ".hosts"

    f = open(private_key_pathname, "w")
    f.write(private_key)
    f.close()

    f = open(config_pathname, "w")
    f.write("[ssh_connection]\n")
    if proxy_ssh:
        proxy_ssh_key = Config.get("proxy_ssh.key")
        proxy_ssh_user = Config.get("proxy_ssh.user")
        if proxy_ssh_key:
            # If proxy_ssh_key is known, then we can proxy into the compute
            # node without needing to have the OpenCloud sshd machinery in
            # place.
            proxy_command = (
                "ProxyCommand ssh -q -i %s -o StrictHostKeyChecking=no %s@%s nc %s 22"
                % (proxy_ssh_key, proxy_ssh_user, hostname, ssh_ip)
            )
        else:
            proxy_command = (
                "ProxyCommand ssh -q -i %s -o StrictHostKeyChecking=no %s@%s"
                % (private_key_pathname, instance_id, hostname)
            )
        f.write('ssh_args = -o "%s"\n' % proxy_command)
    f.write("scp_if_ssh = True\n")
    f.write("pipelining = True\n")
    f.write("\n[defaults]\n")
    f.write("host_key_checking = False\n")
    f.write("timeout = 30\n")
    f.close()

    f = open(hosts_pathname, "w")
    f.write("[%s]\n" % instance_name)
    f.write("%s ansible_ssh_private_key_file=%s\n" % (ssh_ip, private_key_pathname))
    f.close()

    # SSH will complain if private key is world or group readable
    os.chmod(private_key_pathname, 0o600)

    print("ANSIBLE_CONFIG=%s" % config_pathname)
    print("ANSIBLE_HOSTS=%s" % hosts_pathname)

    return run_template(
        name,
        opts,
        path,
        ansible_config=config_pathname,
        ansible_hosts=hosts_pathname,
        run_ansible_script="/opt/xos/synchronizers/base/run_ansible_verbose",
        object=object,
    )


def main():
    run_template(
        "ansible/sync_user_deployments.yaml",
        {
            "endpoint": "http://172.31.38.128:5000/v2.0/",
            "name": "Sapan Bhatia",
            "email": "gwsapan@gmail.com",
            "password": "foobar",
            "admin_user": "admin",
            "admin_password": "6a789bf69dd647e2",
            "admin_tenant": "admin",
            "tenant": "demo",
            "roles": ["user", "admin"],
        },
    )
