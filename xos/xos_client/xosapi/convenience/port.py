import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperPort(ORMWrapper):
    def get_parameters(self):
        parameter_dict = {}

        for param in self.stub.NetworkParameter.objects.filter(content_type=self.self_content_type_id, object_id=self.id):
            parameter_dict[param.parameter.name] = param.value

        return parameter_dict

register_convenience_wrapper("Port", ORMWrapperPort)
