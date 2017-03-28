import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperSlice(ORMWrapper):
    # TODO: this looks to be incorrect
    @property
    def slicename(self):
        return "%s_%s" % (self.site.login_base, self.name)

register_convenience_wrapper("Slice", ORMWrapperSlice)
