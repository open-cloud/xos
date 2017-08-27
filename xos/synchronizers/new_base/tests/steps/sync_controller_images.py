
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
import base64
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
from mock_modelaccessor import *

class SyncControllerImages(SyncStep):
    provides=[ControllerImages]
    observes = ControllerImages
    requested_interval=0
    playbook='sync_controller_images.yaml'

    def fetch_pending(self, deleted):
        ci = ControllerImages()
        i = Image()
        i.name = "Lush Loss"
        ci.i = i
        return [ci]

    def map_sync_inputs(self, controller_image):
        image_fields = {'endpoint':controller_image.controller.auth_url,
                        'endpoint_v3': controller_image.controller.auth_url_v3,
                        'admin_user':controller_image.controller.admin_user,
                        'admin_password':controller_image.controller.admin_password,
                        'domain': controller_image.controller.domain,
                        'name':controller_image.image.name,
                        'filepath':controller_image.image.path,
                        'ansible_tag': '%s@%s'%(controller_image.image.name,controller_image.controller.name), # name of ansible playbook
                        }

	return image_fields

    def map_sync_outputs(self, controller_image, res):
        image_id = res[0]['id']
        controller_image.glance_image_id = image_id
	controller_image.backend_status = '1 - OK'
        controller_image.save()
