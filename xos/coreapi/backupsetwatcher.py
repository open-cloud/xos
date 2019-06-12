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

""" Backup Set Watcher

    Watches for backup/restore operations. Stops the core so they can be executed.

    The basic idea is that backup/restore requests are written to a directory, and responses are read from another
    directory. After a request has been written the core will exit. Only one request is written at a time. Responses
    are only read when the thread is started, as it's impossible for a response to show up while the core is
    running.

        1. Operator optionally creates BackupFile in the XOS database to describe where backup shall be placed
        2. Operator creates BackupOperation in the XOS database
        2. BackupSetWatcher notices new BackupOperation, writes to file in /var/run/xos/backup/requests
        3. BackupSetWatcher terminates coreapi
        4. coreapi exits
        5. the root core shell script executes backup, writing response to /var/run/xos/backup/responses
        6. the root core shell script restarts coreapi
        7. BackupSetWatcher notices a new response, and updates the appropriate BackupOperation object.
"""

import datetime
import json
import os
import threading
import time

from core.models import BackupFile, BackupOperation
from django.db.models import Q, F
from decorators import check_db_connection

from xosconfig import Config
from multistructlog import create_logger
log = create_logger(Config().get("logging"))


# Restrict what the user can specify as a URI for now
ALLOWED_URI = "file:///var/run/xos/backup/local/"


def max_non_none(*lst):
    lst = [x for x in lst if x is not None]
    return max(lst)


def set_enacted(model, code, status):
    model.enacted = max_non_none(model.updated, model.changed_by_policy)
    model.backend_code = code
    model.backend_status = status


class BackupDoesNotExist(Exception):
    pass


class BackupUnreadable(Exception):
    pass


class BackupSetWatcherThread(threading.Thread):
    daemon = True
    interval = 5

    def __init__(self, server, *args, **kwargs):
        self.terminate_signal = False
        super(BackupSetWatcherThread, self).__init__(*args, **kwargs)

        self.server = server
        self.exiting = False
        self.backup_request_dir = "/var/run/xos/backup/requests"
        self.backup_response_dir = "/var/run/xos/backup/responses"
        self.backup_file_dir = "/var/run/xos/backup/local"

        # For people to copy in a file, it helps to ensure the directory exists.
        if not os.path.exists(self.backup_file_dir):
            os.makedirs(self.backup_file_dir)

        # Process any responses that were generated before the coreapi process started.
        self.process_response_dir()

    def init_request_dir(self):
        # make sure the directory exists
        if not os.path.exists(self.backup_request_dir):
            os.makedirs(self.backup_request_dir)

        # make sure it is empty
        for fn in os.listdir(self.backup_request_dir):
            fn = os.path.join(self.backup_request_dir, fn)
            if os.path.isdir(fn) or fn.startswith("."):
                continue
            os.remove(fn)

    def process_response_create(self, uuid, operation, status, response):
        file_details = response["file_details"]

        backupops = BackupOperation.objects.filter(uuid=uuid)
        if not backupops:
            log.exception("Backup response refers to a backupop that does not exist", id=id)
            raise BackupDoesNotExist()

        backupop = backupops[0]

        checksum = file_details.get("checksum")
        if checksum:
            backupop.file.checksum = checksum
            backupop.file.save(allow_modify_feedback=True,
                               update_fields=["checksum"])

        backupop.status = status
        backupop.error_msg = response.get("error_msg", "")
        backupop.effective_date = response.get("effective_date", "")
        set_enacted(backupop, 1, "enacted")
        backupop.save(allow_modify_feedback=True,
                      update_fields=["backend_code", "backend_status", "effective_date", "enacted", "file", "status",
                                     "error_msg"])

    def process_response_restore(self, uuid, operation, status, response):
        file_details = response["file_details"]

        # If the restore was successful, then look for any inprogress backups and mark them orphaned.
        # There should be exactly one such inprogress backup, because there was a BackupOp sitting
        # in the data model when the backup ran.
        if (status == "restored"):
            for req in BackupOperation.objects.filter(status="inprogress", operation="create"):
                log.info("Orphaning inprogress backupop", backupop=req)
                req.status = "orphaned"
                req.save(allow_modify_feedback=True,
                         update_fields=["status"])

        # It's likely the Restore operation doesn't exist, because it went away during the restore
        # process. Check for the existing operation first, and if it doesn't exist, then create
        # one to stand in its place.
        backupops = BackupOperation.objects.filter(uuid=uuid)
        if backupops:
            backupop = backupops[0]
            log.info("Resolved existing backupop model", backupop=backupop)
        else:
            # TODO: Should this use a UUID also?
            backupfiles = BackupFile.objects.filter(id=file_details["id"])
            if backupfiles:
                backupfile = backupfiles[0]
            else:
                backupfile = BackupFile(
                    name=file_details["name"],
                    uri=file_details["uri"],
                    checksum=file_details["checksum"],
                    backend_filename=file_details["backend_filename"])
                backupfile.save(allow_modify_feedback=True)
                log.info("Created backupfile model", backupfile=backupfile)

            backupop = BackupOperation(operation=operation,
                                       file=backupfile,
                                       uuid=uuid)
            backupop.save(allow_modify_feedback=True)
            log.info("Created backupop model", backupop=backupop)

        set_enacted(backupop, 1, "enacted")
        backupop.error_msg = response.get("error_msg", "")
        backupop.status = status
        backupop.effective_date = response.get("effective_date", "")
        backupop.save(allow_modify_feedback=True,
                      update_fields=["backend_code", "backend_status", "effective_date", "enacted", "status",
                                     "error_msg"])

    def process_response_dir(self):
        # make sure the directory exists
        if not os.path.exists(self.backup_response_dir):
            os.makedirs(self.backup_response_dir)

        log.info("Looking for backup responses")

        # process the responses and delete them
        for fn in os.listdir(self.backup_response_dir):
            try:
                fn = os.path.join(self.backup_response_dir, fn)
                if os.path.isdir(fn) or fn.startswith("."):
                    continue

                log.info("Processing backup response", fn=fn)

                try:
                    contents = json.loads(open(fn).read())
                except Exception:
                    # If we can't read it then ignore and delete it
                    log.exception("Failed to read backup response", fn=fn)
                    raise BackupUnreadable()

                try:
                    uuid = contents["uuid"]
                    operation = contents["operation"]
                    status = contents["status"]
                    _ = contents["file_details"]["backend_filename"]
                except Exception:
                    # If we can't understand it then ignore and delete it
                    log.exception("Failed to understand backup response", fn=fn)
                    raise BackupUnreadable()

                if operation == "create":
                    self.process_response_create(uuid, operation, status, contents)
                elif operation == "restore":
                    self.process_response_restore(uuid, operation, status, contents)

                # We've successfully concluded. Delete the response file
                os.remove(fn)
            except (BackupUnreadable, BackupDoesNotExist):
                # Critical failures that can never be resolved, and we can never update the status in the data model,
                # so delete the response file
                os.remove(fn)

    def save_request(self, backupop):
        request = {"id": backupop.id,
                   "uuid": backupop.uuid,
                   "operation": backupop.operation}

        request["file_details"] = {
            "id": backupop.file.id,
            "name": backupop.file.name,
            "uri": backupop.file.uri,
            "checksum": backupop.file.checksum,
            "backend_filename": backupop.file.backend_filename}

        request_fn = os.path.join(self.backup_request_dir, "request")
        with open(request_fn, "w") as f:
            f.write(json.dumps(request))

    @check_db_connection
    def run_once(self):
        # If we're exiting due to a backup request being saved, then return
        if self.exiting:
            return

        # The standard synchronizer dirty object query
        backupops = BackupOperation.objects.filter(
            Q(enacted=None)
            | Q(enacted__lt=F("updated"))
            | Q(enacted__lt=F("changed_by_policy")))

        for backupop in backupops:
            if backupop.operation not in ["create", "restore"]:
                # TODO(smbaker): Implement verify
                # If it's not a create or restore then there is
                # nothing for us to do.
                continue

            if backupop.component != "xos":
                # We only handle XOS Backups / Restores
                continue

            if backupop.status:
                log.info("BackupOp is already executed", backupop=backupop, status=backupop.status)
                # The op was assigned a status. We are done with it.
                # Set its enacted timestamp to prevent finding it again.
                set_enacted(backupop, 1, "already_executed")
                backupop.save(allow_modify_feedback=True,
                              update_fields=["enacted", "backend_code", "backend_status"])
                continue

            if backupop.file:
                # file was specified, check that the uri is allowed
                if (not backupop.file.uri) or (not backupop.file.uri.startswith(ALLOWED_URI)):
                    backupop.backend_code = 2
                    backupop.backend_status = "Only backup_uri that starts with %s is supported" % ALLOWED_URI
                    backupop.save(allow_modify_feedback=True,
                                  update_fields=["backend_code", "backend_status"])
                    continue

                # Generate a backend_filename from uri by stripping off file://
                # This will leave one leading slash on the URL.
                backupop.file.backend_filename = backupop.file.uri[7:]
                backupop.file.save(allow_modify_feedback=True,
                                   update_fields=["backend_filename"])

            # Restores must always specify a file
            if (backupop.operation == "restore") and (not backupop.file):
                backupop.backend_code = 2
                backupop.backend_status = "Must specify file for restore operation"
                backupop.save(allow_modify_feedback=True,
                              update_fields=["backend_code", "backend_status"])
                continue

            # Create operation doesn't require a file, so autogenerate one as necessary.
            if (backupop.operation == "create") and (not backupop.file):
                log.info("Adding autogenerated file to BackupOp", backupop=backupop)
                current_datetime = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
                name = "autogenerated-file-%s" % current_datetime
                backend_filename = os.path.join(self.backup_file_dir, name)
                backupop_file = BackupFile(name=name,
                                           uri="file://" + backend_filename,
                                           backend_filename=backend_filename)
                backupop_file.save(allow_modify_feedback=True)
                backupop.file = backupop_file
                backupop.save(update_fields=["file"])

            # There can only be one request at a time. Ensure the directory is empty.
            self.init_request_dir()
            self.save_request(backupop)
            self.exiting = True

            # Mark the operation as inprogress
            backupop.status = "inprogress"
            backupop.save(allow_modify_feedback=True,
                          update_fields=["effective_date", "status"])

            log.info("Backup/Restore request saved - initiating core shutdown")
            self.server.delayed_shutdown(0)

            # Stop looping through backupops. Since we set self.exiting=True, we know the loop will
            # not be called again.
            return

    def run(self):
        while not self.terminate_signal:
            start = time.time()
            try:
                self.run_once()
            except BaseException:
                log.exception("backupop_watcher: Exception in run loop")

            telap = time.time() - start
            if telap < self.interval:
                time.sleep(self.interval - telap)

    def stop(self):
        self.terminate_signal = True
