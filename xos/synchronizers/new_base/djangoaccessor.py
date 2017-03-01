import traceback

import django.apps
from django.db import reset_queries
from django.utils import timezone
from modelaccessor import ModelAccessor
from django.db import connection
from django.db.models import F, Q
from django import setup as django_setup # django 1.7

from xos.logger import Logger, logging
logger = Logger(level=logging.INFO)

class DjangoModelAccessor(ModelAccessor):
    def __init__(self):
        django_setup()
        super(DjangoModelAccessor, self).__init__()

    def get_all_model_classes(self):
        all_model_classes = {}
        for model in django.apps.apps.get_models():
            all_model_classes[model.__name__] = model

        return all_model_classes

    def fetch_pending(self, main_objs, deletion=False):
        if (type(main_objs) is not list):
                main_objs=[main_objs]

        objs = []
        for main_obj in main_objs:
            if (not deletion):
                lobjs = main_obj.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False),Q(no_sync=False))
            else:
                lobjs = main_obj.deleted_objects.all()
            objs.extend(lobjs)

        return objs

    def reset_queries(self):
        reset_queries()

    def connection_close(self):
        connection.close()

    def check_db_connection_okay(self):
        # django implodes if the database connection is closed by
        # docker-compose
        try:
            diag = self.get_model_class("Diag").objects.filter(name="foo").first()
        except Exception as e:
            from django import db
            if "connection already closed" in traceback.format_exc():
                logger.error("XXX connection already closed")
                try:
                    #                       if db.connection:
                    #                           db.connection.close()
                    db.close_old_connections()
                except:
                    logger.log_exc("XXX we failed to fix the failure")
            else:
                logger.log_exc("XXX some other error")

    def obj_exists(self, o):
        return (o.pk is not None)

    def obj_in_list(self, o, olist):
        return o in olist

    def now(self):
        return timezone.now()

    def is_type(self, obj, name):
        return type(obj) == self.get_model_class(name)

    def is_type(self, obj, name):
        return isinstance(obj, self.get_model_class(name))


