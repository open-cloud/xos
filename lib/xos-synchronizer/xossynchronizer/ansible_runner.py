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

from __future__ import absolute_import

import json
import os
import uuid

from ansible import constants
from ansible.executor import playbook_executor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.utils.display import Display
from ansible.vars.manager import VariableManager

from multistructlog import create_logger
from xosconfig import Config

try:
    # Python 2: "reload" is built-in
    # pylint: disable=W1626
    reload
except NameError:
    # Python 3: "reload" is part of importlib
    from importlib import reload

constants = reload(constants)


log = create_logger(Config().get("logging"))


class ResultCallback(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = "resultcallback"
    CALLBACK_TYPE = "programmatic"

    def __init__(self):
        super(ResultCallback, self).__init__()
        self.results = []
        self.uuid = str(uuid.uuid1())
        self.playbook_status = "OK"

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "playbook start",
            "ansible_status": "OK",
            "ansible_playbook": self.playbook,
        }
        log.info("PLAYBOOK START", playbook=self.playbook, **log_extra)

    def v2_playbook_on_stats(self, stats):
        host_stats = {}
        for host in stats.processed.keys():
            host_stats[host] = stats.summarize(host)

        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "playbook stats",
            "ansible_status": self.playbook_status,
            "ansible_playbook": self.playbook,
            "ansible_result": json.dumps(host_stats),
        }

        if self.playbook_status == "OK":
            log.info("PLAYBOOK END", playbook=self.playbook, **log_extra)
        else:
            log.error("PLAYBOOK END", playbook=self.playbook, **log_extra)

    def v2_playbook_on_play_start(self, play):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "play start",
            "ansible_status": self.playbook_status,
            "ansible_playbook": self.playbook,
        }
        log.debug("PLAY START", play_name=play.name, **log_extra)

    def v2_runner_on_ok(self, result, **kwargs):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "OK",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.debug("OK", task=str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_failed(self, result, **kwargs):
        self.playbook_status = "FAILED"
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "FAILED",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.error("FAILED", task=str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.playbook_status = "FAILED"
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "ASYNC FAILED",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.error("ASYNC FAILED", task=str(result._task), **log_extra)

    def v2_runner_on_skipped(self, result, **kwargs):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "SKIPPED",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.debug("SKIPPED", task=str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_on_unreachable(self, result, **kwargs):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "UNREACHABLE",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.error("UNREACHABLE", task=str(result._task), **log_extra)
        self.results.append(result)

    def v2_runner_retry(self, result, **kwargs):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "RETRY",
            "ansible_result": json.dumps(result._result),
            "ansible_task": result._task,
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.warning(
            "RETRYING - attempt",
            task=str(result._task),
            attempt=result._result["attempts"],
            **log_extra
        )
        self.results.append(result)

    def v2_playbook_on_handler_task_start(self, task, **kwargs):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "task",
            "ansible_status": "HANDLER",
            "ansible_task": task.get_name().strip(),
            "ansible_playbook": self.playbook,
            # 'ansible_host': result._host.get_name()
        }
        log.debug("HANDLER", task=task.get_name().strip(), **log_extra)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "import",
            "ansible_status": "IMPORT",
            "ansible_result": json.dumps(result._result),
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.debug("IMPORT", imported_file=imported_file, **log_extra)
        self.results.append(result)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        log_extra = {
            "xos_type": "ansible",
            "ansible_uuid": self.uuid,
            "ansible_type": "import",
            "ansible_status": "MISSING IMPORT",
            "ansible_result": json.dumps(result._result),
            "ansible_playbook": self.playbook,
            "ansible_host": result._host.get_name(),
        }
        log.debug("MISSING IMPORT", missing=missing_file, **log_extra)
        self.results.append(result)


class Options(object):
    """
    Options class to replace Ansible OptParser
    """

    def __init__(
        self,
        ask_pass=None,
        ask_su_pass=None,
        ask_sudo_pass=None,
        become=None,
        become_ask_pass=None,
        become_method=None,
        become_user=None,
        check=None,
        connection=None,
        diff=None,
        flush_cache=None,
        force_handlers=None,
        forks=1,
        listtags=None,
        listtasks=None,
        module_path=None,
        new_vault_password_file=None,
        one_line=None,
        output_file=None,
        poll_interval=None,
        private_key_file=None,
        remote_user=None,
        scp_extra_args=None,
        seconds=None,
        sftp_extra_args=None,
        skip_tags=None,
        ssh_common_args=None,
        ssh_extra_args=None,
        sudo=None,
        sudo_user=None,
        syntax=None,
        tags=None,
        timeout=None,
        tree=None,
        vault_password_files=None,
        ask_vault_pass=None,
        extra_vars=None,
        inventory=None,
        listhosts=None,
        module_paths=None,
        subset=None,
        verbosity=None,
    ):

        if tags:
            self.tags = tags

        if skip_tags:
            self.skip_tags = skip_tags

        self.ask_pass = ask_pass
        self.ask_su_pass = ask_su_pass
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_vault_pass = ask_vault_pass
        self.become = become
        self.become_ask_pass = become_ask_pass
        self.become_method = become_method
        self.become_user = become_user
        self.check = check
        self.connection = connection
        self.diff = diff
        self.extra_vars = extra_vars
        self.flush_cache = flush_cache
        self.force_handlers = force_handlers
        self.forks = forks
        self.inventory = inventory
        self.listhosts = listhosts
        self.listtags = listtags
        self.listtasks = listtasks
        self.module_path = module_path
        self.module_paths = module_paths
        self.new_vault_password_file = new_vault_password_file
        self.one_line = one_line
        self.output_file = output_file
        self.poll_interval = poll_interval
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.scp_extra_args = scp_extra_args
        self.seconds = seconds
        self.sftp_extra_args = sftp_extra_args
        self.ssh_common_args = ssh_common_args
        self.ssh_extra_args = ssh_extra_args
        self.subset = subset
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.syntax = syntax
        self.timeout = timeout
        self.tree = tree
        self.vault_password_files = vault_password_files
        self.verbosity = verbosity


class Runner(object):
    def __init__(
        self, playbook, run_data, private_key_file=None, verbosity=0, host_file=None
    ):

        self.playbook = playbook
        self.run_data = run_data

        self.options = Options()
        self.options.output_file = playbook + ".result"
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = "ssh"  # Need a connection type "smart" or "ssh"
        # self.options.become = True
        self.options.become_method = "sudo"
        self.options.become_user = "root"

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity
        # Executor appears to have it's own
        # verbosity object/setting as well
        playbook_executor.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        # passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        try:
            self.loader.set_vault_password(os.environ["VAULT_PASS"])
        except AttributeError:
            pass

        # Set inventory, using most of above objects
        if host_file:
            self.inventory = InventoryManager(loader=self.loader, sources=host_file)
        else:
            self.inventory = InventoryManager(loader=self.loader)

        # All the variables from all the various places
        self.variable_manager = VariableManager(
            loader=self.loader, inventory=self.inventory
        )
        self.variable_manager.extra_vars = {}  # self.run_data

        # Setup playbook executor, but don't run until run() called
        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords={},
        )

    def run(self):
        os.environ[
            "REQUESTS_CA_BUNDLE"
        ] = "/usr/local/share/ca-certificates/local_certs.crt"
        callback = ResultCallback()
        self.pbex._tqm._stdout_callback = callback

        self.pbex.run()
        stats = self.pbex._tqm._stats

        # os.remove(self.hosts.name)

        return stats, callback.results
