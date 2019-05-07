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

""" BackupProcessor

    This runs after the core process has completed, and is responsible for performing the actual
    backup and restore operations.

    JSON-encoded text files are used as a communication between the core, which requests backup/restore
    operations, and this processor, which carries out the operations.
"""

import datetime
import hashlib
import json
import os
import traceback

from xosconfig import Config
from multistructlog import create_logger
from backuphandler import BackupHandler


class BackupProcessor(object):
    def __init__(self):
        self.backup_request_dir = "/var/run/xos/backup/requests"
        self.backup_response_dir = "/var/run/xos/backup/responses"
        self.backup_file_dir = "/var/run/xos/backup/local"
        self.log = create_logger(Config().get("logging"))

    def get_backuphandler(self):
        return BackupHandler()

    def instrument_fail(self, req, where):
        """ Check to see if the request indicates that a failure should be instrumented for testing
            purposes. This is done by inserting special strings ("fail_before_restore", etc) into
            the request's filename.
        """

        if where in req["file_details"]["backend_filename"]:
            raise Exception("Instrumented Failure: %s" % where)

    def compute_checksum(self, fn):
        m = hashlib.sha1()
        with open(fn, "rb") as f:
            block = f.read(4096)
            while block:
                m.update(block)
                block = f.read(4096)
        return "sha1:" + m.hexdigest()

    def try_models(self):
        """ Returns True if django modeling is functional """
        result = os.system("python try_models.py")
        return result == 0

    def emergency_rollback(self, emergency_rollback_fn):
        self.log.warning("Performing emergency rollback")
        self.get_backuphandler().restore(emergency_rollback_fn)

    def finalize_response(self, request, response, status, checksum=None, error_msg=None, exception=False):
        """ Build a response dictionary, incorporating informaiton from the request, as well as information
            generated while processing the response.

            If there is an error_msg, it will be printed here and the error will also be encoded into
            the reponse.
        """
        if error_msg:
            response["error_msg"] = error_msg
            if exception:
                response["exception"] = traceback.format_exc()
                self.log.exception(error_msg)
            else:
                self.log.error(error_msg)

        self.log.info("Finalizing response", status=status, id=request["id"], uuid=request["uuid"])
        response["id"] = request["id"]
        response["uuid"] = request["uuid"]
        response["status"] = status
        response["operation"] = request["operation"]
        response["file_details"] = request["file_details"]

        # Date formatted to be consistent with DBMS implementation
        response["effective_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f+00")

        if checksum:
            response["file_details"]["checksum"] = checksum

        fn = os.path.join(self.backup_response_dir, request["request_fn"] + "_response")
        with open(fn, "w") as resp_f:
            resp_f.write(json.dumps(response))
        os.remove(request["request_pathname"])
        return status

    def handle_backup_request(self, req):
        resp = {}

        backend_filename = req["file_details"]["backend_filename"]
        backend_filename_dir = os.path.dirname(backend_filename)
        if not backend_filename_dir:
            return self.finalize_response(req, resp, "failed",
                                          error_msg="backend_filename should include a directory")

        # Ensure the backup directory exists
        if not os.path.exists(backend_filename_dir):
            os.makedirs(backend_filename_dir)

        # Step 1: Run the backup

        try:
            self.instrument_fail(req, "fail_before_backup")
            self.get_backuphandler().backup(backend_filename)
        except Exception:
            return self.finalize_response(req, resp, "failed",
                                          error_msg="Backup failed",
                                          exception=True)

        # Step 2: Generate the checksum

        try:
            checksum = self.compute_checksum(backend_filename)
        except Exception:
            return self.finalize_response(req, resp, "failed",
                                          error_msg="checksum compute failed",
                                          exception=True)

        return self.finalize_response(req, resp, "created", checksum=checksum)

    def handle_restore_request(self, req):
        resp = {}

        backend_filename = req["file_details"]["backend_filename"]
        if not os.path.exists(backend_filename):
            return self.finalize_response(req, resp, "failed",
                                          error_msg="restore file %s does not exist" % backend_filename)

        # Step 1: Verify checksum

        checksum = req["file_details"].get("checksum")
        if checksum:
            computed_checksum = self.compute_checksum(backend_filename)
            if computed_checksum != checksum:
                return self.finalize_response(req, resp, "failed",
                                              error_msg="checksum mismatch: %s != %s" % (computed_checksum, checksum),
                                              exception=True)

        # Step 2: Perform the emergency-rollback backup

        if not os.path.exists(self.backup_file_dir):
            os.makedirs(self.backup_file_dir)

        emergency_rollback_fn = os.path.join(self.backup_file_dir, "emergency_rollback")

        try:
            self.instrument_fail(req, "fail_before_rollback")
            self.get_backuphandler().backup(emergency_rollback_fn)
        except Exception:
            return self.finalize_response(req, resp, "failed",
                                          error_msg="Exception during create emergency rollback",
                                          exception=True)

        # Step 3: Perform the restore

        try:
            self.instrument_fail(req, "fail_before_restore")
            self.get_backuphandler().restore(backend_filename)
        except Exception:
            self.emergency_rollback(emergency_rollback_fn)
            return self.finalize_response(req, resp, "failed",
                                          error_msg="Exception during restore, emergency rollback performed",
                                          exception=True)

        # Step 4: Verify model integrity

        if (not self.try_models()) or ("fail_try_models" in req["file_details"]["backend_filename"]):
            self.emergency_rollback(emergency_rollback_fn)
            return self.finalize_response(req, resp, "failed",
                                          error_msg="Try_models failed, emergency rollback performed")

        return self.finalize_response(req, resp, "restored")

    def run(self):
        # make sure the directory exists
        if not os.path.exists(self.backup_request_dir):
            os.makedirs(self.backup_request_dir)

        for fn in os.listdir(self.backup_request_dir):
            pathname = os.path.join(self.backup_request_dir, fn)
            if os.path.isdir(pathname) or pathname.startswith("."):
                continue

            try:
                request = json.loads(open(pathname).read())
            except Exception:
                # If we can't read it then ignore it
                self.log.exception("Failed to read backup request", fn=pathname)
                continue

            try:
                id = request["id"]
                uuid = request["uuid"]
                operation = request["operation"]
                backend_filename = request["file_details"]["backend_filename"]
            except Exception:
                # If we can't understand it then ignore it
                self.log.exception("Failed to understand backup request", fn=pathname)
                continue

            self.log.info(
                "Processing request",
                id=id,
                uuid=uuid,
                operation=operation,
                backend_filename=backend_filename)

            request["request_fn"] = fn
            request["request_pathname"] = pathname

            try:
                if (operation == "create"):
                    self.handle_backup_request(request)
                elif (operation == "restore"):
                    self.handle_restore_request(request)
                elif (operation == "verify"):
                    self.finalize_response(request, {}, "failed",
                                           error_msg="Verify is not implemented yet")
                else:
                    self.finalize_response(request, {}, "failed",
                                           error_msg="Operation is not backup | restore | verify")
            except Exception:
                # Something failed in a way we didn't expect.
                self.finalize_response(request, {}, "failed",
                                       error_msg="Uncaught exception",
                                       exception=True)


if __name__ == "__main__":
    Config.init()
    BackupProcessor().run()
