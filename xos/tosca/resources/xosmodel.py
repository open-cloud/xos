
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


from xosresource import XOSResource
from core.models import XOS


class XOSXOS(XOSResource):
    provides = "tosca.nodes.XOS"
    xos_model = XOS
    obsolete_props = [
        "ui_port", "bootstrap_ui_port", "docker_project_name", "db_container_name", "redis_container_name",
        "enable_build", "frontend_only", "source_ui_image", "extra_hosts", "no_start", "no_build",
        "dest_ui_image", "cert_chain_name",
    ]

