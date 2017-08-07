
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


from suit.apps import DjangoSuitConfig


class MyDjangoSuitConfig(DjangoSuitConfig):
    admin_name = 'XOS'
    menu_position = 'vertical'
    menu_open_first_child = False
    menu = (
      {'label': 'Deployments', 'icon': 'icon-deployment', 'url': '/admin/core/deployment/'},
      {'label': 'Sites', 'icon': 'icon-site', 'url': '/admin/core/site/'},
      {'label': 'Slices', 'icon': 'icon-slice', 'url': '/admin/core/slice/'},
      {'label': 'Users', 'icon': 'icon-user', 'url': '/admin/core/user/'},
      {'label': 'Services', 'icon': 'icon-cog', 'url': '/admin/core/service/'},
    )
