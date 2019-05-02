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

from apistats import track_request_time
from authhelper import XOSAuthHelperMixin
from decorators import translate_exceptions, require_authentication
import os
from protos import filetransfer_pb2, filetransfer_pb2_grpc

import hashlib
from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class FileTransferService(filetransfer_pb2_grpc.filetransferServicer, XOSAuthHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        XOSAuthHelperMixin.__init__(self)

    def stop(self):
        pass

    @translate_exceptions("FileTransfer", "Download")
    @track_request_time("FileTransfer", "Download")
    @require_authentication
    def Download(self, request, context):
        if not request.uri.startswith("file://"):
            raise Exception("Uri must start with file://")

        backend_filename = request.uri[7:]
        if not os.path.exists(backend_filename):
            raise Exception("File %s does not exist" % backend_filename)

        with open(backend_filename) as backend_f:
            while True:
                chunk = backend_f.read(65536)
                if not chunk:
                    return
                yield filetransfer_pb2.FileContents(chunk=chunk)

    @translate_exceptions("FileTransfer", "Upload")
    @track_request_time("FileTransfer", "Upload")
    @require_authentication
    def Upload(self, request_iterator, context):
        backend_file = None
        try:
            hasher = hashlib.sha1()
            chunks_received = 0
            bytes_received = 0
            for chunk in request_iterator:
                # The first chunk had better have the URI so we can open the file
                if not backend_file:
                    if not chunk.uri.startswith("file://"):
                        raise Exception("Uri must start with file://")

                    backend_filename = chunk.uri[7:]

                    backend_file = open(backend_filename, "w")

                backend_file.write(chunk.chunk)
                chunks_received += 1
                bytes_received += len(chunk.chunk)
                hasher.update(chunk.chunk)

            response = filetransfer_pb2.FileUploadStatus()
            response.status = response.SUCCESS
            response.chunks_received = chunks_received
            response.bytes_received = bytes_received
            response.checksum = "sha1:" + hasher.hexdigest()

            return response
        finally:
            # Files do not always close automatically when going out of scope
            if backend_file:
                backend_file.close()
