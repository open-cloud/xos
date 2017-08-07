
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


""" PlusObjectMixin

    Implements fields that are common to all OpenCloud objects. For example,
    stuff related to backend icons.
"""

ICON_URLS = {"success": "/static/admin/img/icon_success.gif",
            "clock": "/static/admin/img/icon_clock.gif",
            "error": "/static/admin/img/icon_error.gif"}



class PlusObjectMixin:
    def getBackendIcon(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")
        return icon_url

    def getBackendHtml(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")

        if tooltip:
            return '<span title="%s"><img src="%s"></span>' % (tooltip, icon_url)
        else:
            return '<img src="%s">' % icon_url


