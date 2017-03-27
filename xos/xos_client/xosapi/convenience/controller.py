import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperController(ORMWrapper):
    @property
    def auth_url_v3(self):
        if self.auth_url and self.auth_url[-1] == '/':
            return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-2]))
        else:
            return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-1]))

register_convenience_wrapper("Controller", ORMWrapperController)
