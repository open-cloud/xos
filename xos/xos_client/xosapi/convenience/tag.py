from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperTag(ORMWrapper):
    def get_generic_foreignkeys(self):
        return [{"name": "content_object", "content_type": "content_type", "id": "object_id"}]

register_convenience_wrapper("Tag", ORMWrapperTag)
