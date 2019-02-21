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

DEFAULT_VALUES = {
    "xos_dir": "/opt/xos",
    "desired_state": "load",  # synchronizers - default to "load"
    # by default version in not set,
    # we can't make it mandatory as we're reading multiple files in the synchronizers
    "core_version": None,
    # The configuration below inherits from the standard config of the Python logging module
    # See: https://docs.python.org/2/library/logging.config.html
    # multistructlog supports this config in all of its generality
    # So for instance, you can add new handlers. Note that all handlers will
    # receive logs simultaneously.
    "blueprints": {},
    "logging": {
        "version": 1,
        "handlers": {
            "console": {"class": "logging.StreamHandler"},
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/var/log/xos.log",
                "maxBytes": 10485760,
                "backupCount": 5,
            },
        },
        "loggers": {"": {"handlers": ["console", "file"], "level": "DEBUG"}},
    },
    "accessor": {"endpoint": "xos-core.cord.lab:50051", "kind": "grpcapi"},
    "keep_temp_files": False,
    "dependency_graph": None,
    "error_map_path": "/opt/xos/error_map.txt",
    "feefie": {"client_user": "pl"},
    "proxy_ssh": {"enabled": True, "key": "/opt/cord_profile/node_key", "user": "root"},
    "node_key": "/opt/cord_profile/node_key",
    "config_dir": "/etc/xos/sync",
    "backoff_disabled": True,
    "kafka_bootstrap_servers": ["cord-kafka:9092"],
}
