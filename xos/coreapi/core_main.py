
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


import os
import sys
import time

from grpc_server import XOSGrpcServer, restart_related_containers

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

def init_reaper():
    reaper = None
    try:
        from reaper import ReaperThread
        reaper = ReaperThread()
        reaper.start()
    except:
        logger.log_exception("Failed to initialize reaper")

    return reaper

if __name__ == '__main__':
    server = XOSGrpcServer()
    server.init_django()
    server.start()

    reaper = init_reaper()

    restart_related_containers()

    log.info("XOS core entering wait loop")
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    try:
        while True:
            if server.exit_event.wait(_ONE_DAY_IN_SECONDS):
                break
    except KeyboardInterrupt:
        log.info("XOS core terminated by keyboard interrupt")

    server.stop()
    reaper.stop()
