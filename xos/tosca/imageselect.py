
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

from core.models import User,Image

class XOSImageSelector(object):
    def __init__(self, user, distribution=None, type=None, architecture=None, version=None):
        self.user = user

    def get_allowed_images(self):
        # TODO: logic to get images that the user can use
        nodes = Image.objects.all()
        return nodes

    def get_image(self):
        images = self.get_allowed_images()

        # TODO: pick image based on parameters

        found_imgs=images.filter(name="Ubuntu 14.04 LTS")   # portal
        if found_imgs:
            return found_imgs[0]

        found_imgs=images.filter(name="Ubuntu-14.04-LTS")    # demo
        if found_imgs:
            return found_imgs[0]

        found_imgs=images.filter(name="trusty-server-multi-nic")    # demo
        if found_imgs:
            return found_imgs[0]

        raise Exception("Failed to find an acceptable image")

