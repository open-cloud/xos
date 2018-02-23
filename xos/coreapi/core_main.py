
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


import argparse
import os
import sys
import time

from grpc_server import XOSGrpcServer

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_status", dest="model_status", type=int, default=0, help="status of model prep")
    parser.add_argument("--model_output", dest="model_output", type=file, default=None, help="file containing output of model prep step")
    args = parser.parse_args()

    if args.model_output:
        args.model_output = args.model_output.read()
    else:
        args.model_output = ""

    return args

def init_reaper():
    reaper = None
    try:
        from reaper import ReaperThread
        reaper = ReaperThread()
        reaper.start()
    except:
        log.exception("Failed to initialize reaper")

    return reaper

if __name__ == '__main__':
    args = parse_args()

    server = XOSGrpcServer(model_status = args.model_status,
                           model_output = args.model_output)
    server.start()

    if server.django_initialized:
        reaper = init_reaper()
    else:
        log.warning("Skipping reaper as django is not initialized")
        reaper = None

    log.info("XOS core entering wait loop")
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    try:
        while True:
            if server.exit_event.wait(_ONE_DAY_IN_SECONDS):
                break
    except KeyboardInterrupt:
        log.info("XOS core terminated by keyboard interrupt")

    server.stop()

    if reaper:
        reaper.stop()
