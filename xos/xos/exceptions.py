from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied as RestFrameworkPermissionDenied

class XOSProgrammingError(APIException):
    status_code=400
    def __init__(self, why="programming error", fields={}):
        APIException.__init__(self, {"error": "XOSProgrammingError",
                            "specific_error": why,
                            "fields": fields})

class XOSPermissionDenied(RestFrameworkPermissionDenied):
    def __init__(self, why="permission error", fields={}):
        APIException.__init__(self, {"error": "XOSPermissionDenied",
                            "specific_error": why,
                            "fields": fields})

class XOSNotAuthenticated(RestFrameworkPermissionDenied):
    def __init__(self, why="you must be authenticated to use this api", fields={}):
        APIException.__init__(self, {"error": "XOSNotAuthenticated",
                            "specific_error": why,
                            "fields": fields})

class XOSNotFound(RestFrameworkPermissionDenied):
    status_code=404
    def __init__(self, why="object not found", fields={}):
        APIException.__init__(self, {"error": "XOSNotFound",
                            "specific_error": why,
                            "fields": fields})

class XOSValidationError(APIException):
    status_code=403
    def __init__(self, why="validation error", fields={}):
        APIException.__init__(self, {"error": "XOSValidationError",
                            "specific_error": why,
                            "fields": fields})

class XOSDuplicateKey(APIException):
    status_code=400
    def __init__(self, why="duplicate key", fields={}):
        APIException.__init__(self, {"error": "XOSDuplicateKey",
                            "specific_error": why,
                            "fields": fields})

class XOSMissingField(APIException):
    status_code=400
    def __init__(self, why="missing field", fields={}):
        APIException.__init__(self, {"error": "XOSMissingField",
                            "specific_error": why,
                            "fields": fields})

class XOSConfigurationError(APIException):
    status_code=400
    def __init__(self, why="configuration error", fields={}):
        APIException.__init__(self, {"error": "XOSConfigurationError",
                            "specific_error": why,
                            "fields": fields})

class XOSConflictingField(APIException):
    status_code=400
    def __init__(self, why="conflicting field", fields={}):
        APIException.__init__(self, {"error": "XOSMissingField",
                            "specific_error": why,
                            "fields": fields})

class XOSServiceUnavailable(APIException):
    status_code=503
    def __init__(self, why="Service temporarily unavailable, try again later", fields={}):
        APIException.__init__(self, {"error": "XOSServiceUnavailable",
                            "specific_error": why,
                            "fields": fields})
