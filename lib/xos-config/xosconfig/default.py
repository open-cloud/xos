
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
    'xos_dir': '/opt/xos',
    'logging': {
        'file': '/var/log/xos.log', # TODO remove me, the new logger will be able to decide on which file to log
        'level': 'info',
        'channels': ['file', 'console'],
        'logstash_hostport': 'cordloghost:5617'
    },
    'accessor': {
        'endpoint': 'xos-core.cord.lab:50051',
        'kind': 'grpcapi',
    },
    'keep_temp_files': False,
    'enable_watchers': False,
    'dependency_graph': '/opt/xos/model-deps',
    'error_map_path': '/opt/xos/error_map.txt',
    'feefie': {
        'client_user': 'pl'
    },
    'proxy_ssh': {
      'enabled': True,
      'key': '/opt/cord_profile/node_key',
      'user': 'root'
    },
    'node_key': '/opt/cord_profile/node_key',
    'config_dir': '/etc/xos/sync',
    'backoff_disabled': True
}
