
from core.models.networkparameter import NetworkParameter
from core.models.networkparametertype import NetworkParameterType

class ParameterMixin(object):
    # helper classes for dealing with NetworkParameter

    def get_parameters(self):
        parameter_dict = {}

        instance_type = self.get_content_type_key()
        for param in NetworkParameter.objects.filter(content_type=instance_type, object_id=self.id):
            parameter_dict[param.parameter.name] = param.value

        return parameter_dict

    def set_parameter(self, name, value):
        instance_type = self.get_content_type_key()
        existing_params = NetworkParameter.objects.filter(parameter__name=name, content_type=instance_type, object_id=self.id)
        if existing_params:
            p=existing_params[0]
            p.value = value
            p.save()
        else:
            pt = NetworkParameterType.objects.get(name=name)
            p = NetworkParameter(parameter=pt, content_type=instance_type, object_id=self.id, value=value)
            p.save()

    def unset_parameter(self, name):
        instance_type = self.get_content_type_key()
        existing_params = NetworkParameter.objects.filter(parameter__name=name, content_type=instance_type, object_id=self.id)
        for p in existing_params:
            p.delete()

