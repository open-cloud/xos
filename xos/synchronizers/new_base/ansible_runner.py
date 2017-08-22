
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


#!/usr/bin/env python

import os
import sys
import pdb
import json
import uuid

from ansible import constants
constants = reload(constants)

from tempfile import NamedTemporaryFile
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor import playbook_executor
from ansible.utils.display import Display
from ansible.plugins.callback import CallbackBase

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


class ResultCallback(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = 'resultcallback'
    CALLBACK_TYPE = 'programmatic'

    def __init__(self):
        super(ResultCallback, self).__init__()
        self.results = []
        self.uuid = str(uuid.uuid1())
        self.playbook_status = 'OK'

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "playbook start",
            'ansible_status': "OK",
            'ansible_playbook': self.playbook
        }
        log.info("PLAYBOOK START", playbook = self.playbook, **log_extra)

    def v2_playbook_on_stats(self, stats):
        host_stats = {}
        for host in stats.processed.keys():
            host_stats[host] = stats.summarize(host)

        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "playbook stats",
            'ansible_status': self.playbook_status,
            'ansible_playbook': self.playbook,
            'ansible_result': json.dumps(host_stats)
        }

        if self.playbook_status == 'OK':
            log.info("PLAYBOOK END", playbook = self.playbook, **log_extra)
        else:
            log.error("PLAYBOOK END", playbook = self.playbook, **log_extra)

    def v2_playbook_on_play_start(self, play):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "play start",
            'ansible_status': self.playbook_status,
            'ansible_playbook': self.playbook
        }
        log.debug("PLAY START",play_name = play.name, **log_extra)

    def v2_runner_on_ok(self, result, **kwargs):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "OK",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.debug("OK", task = str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_failed(self, result, **kwargs):
        self.playbook_status = "FAILED"
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "FAILED",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.error("FAILED", task = str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.playbook_status = "FAILED"
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "ASYNC FAILED",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.error("ASYNC FAILED", task = str(result._task), **log_extra)

    def v2_runner_on_skipped(self, result, **kwargs):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "SKIPPED",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.debug("SKIPPED", task = str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_unreachable(self, result, **kwargs):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "UNREACHABLE",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.error("UNREACHABLE", task = str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_retry(self, result, **kwargs):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "RETRY",
            'ansible_result': json.dumps(result._result),
            'ansible_task': result._task,
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.warning("RETRYING - attempt", task =str(result._task), attempt = result._result['attempts'], **log_extra)
        self.results.append(result)

    def v2_playbook_on_handler_task_start(self, task, **kwargs):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "task",
            'ansible_status': "HANDLER",
            'ansible_task': task.get_name().strip(),
            'ansible_playbook': self.playbook,
            # 'ansible_host': result._host.get_name()
        }
        log.debug("HANDLER", task = task.get_name().strip(), **log_extra)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "import",
            'ansible_status': "IMPORT",
            'ansible_result': json.dumps(result._result),
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.debug("IMPORT", imported_file =imported_file, **log_extra)
        self.results.append(result)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        log_extra = {
            'xos_type': "ansible",
            'ansible_uuid': self.uuid,
            'ansible_type': "import",
            'ansible_status': "MISSING IMPORT",
            'ansible_result': json.dumps(result._result),
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.get_name()
        }
        log.debug("MISSING IMPORT", missing = missing_file, **log_extra)
        self.results.append(result)

class Options(object):
    """
    Options class to replace Ansible OptParser
    """
    def __init__(self, verbosity=None, inventory=None, listhosts=None, subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None, new_vault_password_file=None,
                 output_file=None, tags=None, skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None, connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None, poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None, force_handlers=None, flush_cache=None, listtasks=None, listtags=None, module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path


class Runner(object):

    def __init__(self, playbook, run_data, private_key_file=None, verbosity=0, host_file=None):

        self.playbook = playbook
        self.run_data = run_data

        self.options = Options()
        self.options.output_file = playbook + '.result'
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = 'ssh'  # Need a connection type "smart" or "ssh"
        #self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity
        # Executor appears to have it's own
        # verbosity object/setting as well
        playbook_executor.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        #passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        try:
            self.loader.set_vault_password(os.environ['VAULT_PASS'])
        except KeyError:
            pass

        # All the variables from all the various places
        self.variable_manager = VariableManager()
        self.variable_manager.extra_vars = {} # self.run_data

        # Set inventory, using most of above objects
        if (host_file):
            self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list = host_file)
        else:
            self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager)

        self.variable_manager.set_inventory(self.inventory)

        # Setup playbook executor, but don't run until run() called
        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords={})

    def run(self):
        os.environ['REQUESTS_CA_BUNDLE'] = '/usr/local/share/ca-certificates/local_certs.crt'
        callback = ResultCallback()
        self.pbex._tqm._stdout_callback = callback

        self.pbex.run()
        stats = self.pbex._tqm._stats

        # Test if success for record_logs
        run_success = True
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            if t['unreachable'] > 0 or t['failures'] > 0:
                run_success = False

        #os.remove(self.hosts.name)

        return stats,callback.results

