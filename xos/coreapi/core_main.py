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
import prometheus_client
import sys

# FIXME: should grpc_server initialize the Config?
from grpc_server import XOSGrpcServer

from xosconfig import Config
from xoskafka import XOSKafkaProducer
from multistructlog import create_logger

log = create_logger(Config().get("logging"))

# create an single kafka producer connection for the core

XOSKafkaProducer.init()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_status",
        dest="model_status",
        type=int,
        default=0,
        help="status of model prep",
    )
    parser.add_argument(
        "--model_output",
        dest="model_output",
        type=file,
        default=None,
        help="file containing output of model prep step",
    )
    parser.add_argument(
        "--no-backupwatcher",
        dest="enable_backupwatcher",
        action="store_false",
        default=True,
        help="disable the backupwatcher thread",
    )
    parser.add_argument(
        "--no-reaper",
        dest="enable_reaper",
        action="store_false",
        default=True,
        help="disable the reaper thread",
    )
    parser.add_argument(
        "--no-server",
        dest="enable_server",
        action="store_false",
        default=True,
        help="disable the grpc server thread",
    )
    parser.add_argument(
        "--no-prometheus",
        dest="enable_prometheus",
        action="store_false",
        default=True,
        help="disable the prometheus thread",
    )
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
    except BaseException:
        log.exception("Failed to initialize reaper")

    return reaper


def init_backupset_watcher(server):
    backupset_watcher = None
    try:
        from backupsetwatcher import BackupSetWatcherThread

        backupset_watcher = BackupSetWatcherThread(server)
        backupset_watcher.start()
    except BaseException:
        log.exception("Failed to initialize backupset watcher")

    return backupset_watcher


if __name__ == "__main__":
    args = parse_args()

    # start the prometheus server
    # TODO (teone) consider moving this in a separate process so that it won't die when we load services
    if args.enable_prometheus:
        prometheus_client.start_http_server(8000)

    server = XOSGrpcServer(
        model_status=args.model_status, model_output=args.model_output
    )

    if args.enable_server:
        server.start()
    else:
        # This is primarily to facilitate development, running the reaper and/or the backupwatcher without
        # actually starting the grpc server.
        server.init_django()
        if not server.django_initialized:
            log.error("Django is broken. Please remove the synchronizer causing the problem and restart the core.")
            sys.exit(-1)

    reaper = None
    backup_watcher = None
    if server.django_initialized:
        if args.enable_reaper:
            reaper = init_reaper()
        if args.enable_backupwatcher:
            backup_watcher = init_backupset_watcher(server)
    else:
        log.warning("Skipping reaper and backupset_watcher as django is not initialized")

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

    if backup_watcher:
        backup_watcher.stop()
