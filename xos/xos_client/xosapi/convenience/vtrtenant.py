from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVTRTenant(ORMWrapper):
    def get_generic_foreignkeys(self):
        return [{"name": "target", "content_type": "target_type", "id": "target_id"}]

register_convenience_wrapper("VTRTenant", ORMWrapperVTRTenant)
