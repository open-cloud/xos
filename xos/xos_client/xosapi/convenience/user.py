import hashlib
import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperUser(ORMWrapper):
    @property
    def remote_password(self):
        return hashlib.md5(self.password).hexdigest()[:12]

register_convenience_wrapper("User", ORMWrapperUser)
