
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


from view_common import *
from core.xoslib.objects.sliceplus import SlicePlus

# This was intended to serve as a download feature for the tenant view. Found
# a better way to do it. This is deprecated.

class DownloadSSHCommandsView(View):
    url = r'^sshcommands/(?P<sliceid>\d+)/$'

    def get(self, request, sliceid=None, **kwargs):
        #slice = Slices.objects.get(id=sliceid);
        #for instance in slice.instances.all():
        #    if (instance.instance_id && instance.instance_name):

        slice = SlicePlus.objects.get(id=sliceid)

        return HttpResponse(slice.getSliceInfo()["sshCommands"], content_type='text/text')

