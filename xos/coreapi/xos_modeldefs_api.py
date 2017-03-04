import base64
import time
from protos import modeldefs_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
import django.apps
from core.models import *
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin


class ModelDefsService(modeldefs_pb2.modeldefsServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

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

    def parseModuleName(self, module):
        if 'core' in module:
            return 'core'
        if 'service' in module:
            return module[:-7]
        return module

    def ListModelDefs(self, request, context):
        models = django.apps.apps.get_models()

        modeldefs = modeldefs_pb2.ModelDefs()

        response = []

        for model in models:
            # NOTE removing Django internal models
            if 'django' in model.__module__:
                continue
            if 'cors' in model.__module__:
                continue
            if 'contenttypes' in model.__module__:
                continue
            if 'core.models.journal' in model.__module__:
                continue
            if 'core.models.project' in model.__module__:
                continue

            modeldef = modeldefs.items.add()

            modeldef.name = model.__name__
            modeldef.app = self.parseModuleName(model.__module__)

            for f in model._meta.fields:
                field = modeldef.fields.add()

                field.name = f.name
                field.hint = f.help_text

                fieldtype = self.convertType(f.get_internal_type())
                if fieldtype is not None:
                    field.type = fieldtype
                else:
                    field.type = 'string'

                if not f.blank and not f.null:
                    val = field.validators.add()
                    val.name = "required"
                    val.bool_value = True

                for v in f.validators:
                    val = field.validators.add()
                    validator_name = v.__class__.__name__
                    if 'function' in validator_name:
                        validator_name = v.__name__
                    validator_name = self.convertValidator(validator_name)

                    if not validator_name:
                        continue

                    val.name = validator_name
                    if hasattr(v, 'limit_value'):
                        try:
                            val.int_value = v.limit_value
                        except TypeError:
                            val.str_value = str(v.limit_value)
                    else:
                        val.bool_value = True

                if f.is_relation and f.related_model:

                    if 'ContentType' in f.related_model.__name__:
                        # ContentType is a Django internal
                        continue

                    field.name = field.name + '_id'
                    field.relation.model = f.related_model.__name__
                    field.relation.type = self.getRelationType(f)

                    rel = modeldef.relations.add()
                    rel.model = f.related_model.__name__
                    rel.type = self.getRelationType(f)
        return modeldefs

