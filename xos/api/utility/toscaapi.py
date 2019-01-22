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
import traceback

# The Tosca engine expects to be run from /opt/xos/tosca/ or equivalent. It
# needs some sys.path fixing up.
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
toscadir = os.path.join(currentdir, "../../tosca")


class ToscaViewSet(XOSViewSet):
    base_name = "tosca"
    method_name = "tosca"
    method_kind = "viewset"

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []

        patterns.append(self.list_url("run/$", {"post": "post_run"}, "tosca_run"))

        return patterns

    def post_run(self, request):

        recipe = request.data.get("recipe", None)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca

            xt = XOSTosca(recipe, parent_dir=toscadir, log_to_console=False)
            xt.execute(request.user)
        except BaseException:
            return Response({"error_text": traceback.format_exc()}, status=500)
        finally:
            sys.path = sys_path_save

        return Response({"log_msgs": xt.log_msgs})
