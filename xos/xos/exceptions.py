
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


import json
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied as RestFrameworkPermissionDenied

def _get_json_error_details(data):
    """
    Convert error details to JSON
    """
    if isinstance(data, dict):
        ret = {
            key: value for key, value in data.items()
        }
    elif isinstance(data, list):
        ret = [
            item for item in data
        ]

    return json.dumps(ret)


class XOSProgrammingError(APIException):
    status_code=400
    def __init__(self, why="programming error", fields={}):
        raw_detail = {
            "error": "XOSProgrammingError",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSPermissionDenied(RestFrameworkPermissionDenied):
    def __init__(self, why="permission error", fields={}):
        raw_detail = {
            "error": "XOSPermissionDenied",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSNotAuthenticated(RestFrameworkPermissionDenied):
    status_code=401
    def __init__(self, why="you must be authenticated to use this api", fields={}):
        raw_detail = {
            "error": "XOSNotAuthenticated",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSNotFound(RestFrameworkPermissionDenied):
    status_code=404
    def __init__(self, why="object not found", fields={}):
        raw_detail = {
            "error": "XOSNotFound",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSValidationError(APIException):
    status_code=403
    def __init__(self, why="validation error", fields={}):
        raw_detail = {
            "error": "XOSValidationError",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSDuplicateKey(APIException):
    status_code=400
    def __init__(self, why="duplicate key", fields={}):
        raw_detail = {
            "error": "XOSDuplicateKey",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSMissingField(APIException):
    status_code=400
    def __init__(self, why="missing field", fields={}):
        raw_detail = {
            "error": "XOSMissingField",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSConfigurationError(APIException):
    status_code=400
    def __init__(self, why="configuration error", fields={}):
        raw_detail = {
            "error": "XOSConfigurationError",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSConflictingField(APIException):
    status_code=400
    def __init__(self, why="conflicting field", fields={}):
        raw_detail = {
            "error": "XOSMissingField",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)

class XOSServiceUnavailable(APIException):
    status_code=503
    def __init__(self, why="Service temporarily unavailable, try again later", fields={}):
        raw_detail = {
            "error": "XOSServiceUnavailable",
            "specific_error": why,
            "fields": fields
        }
        APIException.__init__(self, raw_detail)
        self.raw_detail = raw_detail
        self.json_detail = _get_json_error_details(raw_detail)
