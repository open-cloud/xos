from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.exceptions import APIException
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
import json
from core.models import UserDashboardView, DashboardView
from api.xosapi_helpers import XOSViewSet, PlusModelSerializer
import django.apps
from rest_framework.views import APIView


class ModelDefsList(APIView):
    method_kind = "list"
    method_name = "modeldefs"

    typeMap = {
        'BooleanField': 'boolean',
        'TextField': 'text',
        'CharField': 'string',
        'ForeignKey': 'number',
        'IntegerField': 'number',
        'AutoField': 'number',
        'DateTimeField': 'date'
    }

    validatorMap = {
        'EmailValidator': 'email',
        'MaxLengthValidator': 'maxlength',
        'URLValidator': 'url',
        'MinValueValidator': 'min',
        'MaxValueValidator': 'max',
        'validate_ipv46_address': 'ip'
    }

    def convertType(self, type):
        try:
            jsType = self.typeMap[type]
            return jsType
        except Exception:
            return None

    def convertValidator(self, validator):
        try:
            jsValidator = self.validatorMap[validator]
            return jsValidator
        except Exception:
            return None

    def getRelationType(self, field):
        if (field.many_to_many):
            return 'many_to_many'
        if (field.many_to_one):
            return 'many_to_one'
        if (field.one_to_many):
            return 'one_to_many'
        if (field.one_to_one):
            return 'one_to_one'

    def get(self, request, format=None):
        models = django.apps.apps.get_models()

        response = []

        for model in models:
            if 'core' in model.__module__:
                # if 'Instance' == model.__name__:
                modeldef = {}
                modeldef['name'] = model.__name__

                fields = []
                relations = []
                for f in model._meta.fields:

                    field = {
                        'name': f.name,
                        'hint': f.help_text,
                        'validators': {
                        }
                    }

                    fieldtype = self.convertType(f.get_internal_type())
                    if fieldtype is not None:
                        field['type'] = fieldtype
                    else:
                        field['type'] = 'string'

                    if not f.blank and not f.null:
                        field['validators']['required'] = True

                    for v in f.validators:
                        validator_name = v.__class__.__name__
                        if 'function' in validator_name:
                            validator_name = v.__name__
                        validator_name = self.convertValidator(validator_name)

                        if hasattr(v, 'limit_value'):
                            field['validators'][validator_name] = v.limit_value
                        else:
                            field['validators'][validator_name] = True

                    fields.append(field)

                    if f.is_relation and f.related_model and f.related_model.__name__ != 'ContentType':
                        # ContentType is a Django internal model, we don't want it in the GUI

                        # Add the relation details to the model
                        field['relation'] = {
                            'model': f.related_model.__name__,
                            'type': self.getRelationType(f)
                        }

                        relations.append(f.related_model.__name__)

                modeldef['fields'] = fields

                # TODO add relation type (eg: OneToMany, ManyToMany)
                modeldef['relations'] = list(set(relations))
                response.append(modeldef)
        return Response(response)
