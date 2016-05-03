# Syndicate service models.py

from core.models import Service
from django.db import models, transaction

SERVICE_NAME = 'syndicateservice'
SERVICE_NAME_VERBOSE = 'Syndicate Service'

class SyndicateService(Service):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE


class Volume(PLCoreBase):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE


