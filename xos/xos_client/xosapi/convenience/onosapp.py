import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper
from xosapi.convenience.tenant import ORMWrapperTenant

class ORMWrapperONOSApp(ORMWrapperTenant):
    pass

register_convenience_wrapper("ONOSApp", ORMWrapperONOSApp)
