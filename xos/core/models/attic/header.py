from __future__ import absolute_import

import sys
import json
import operator
from operator import attrgetter
from core.models.plcorebase import *
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from core.acl import AccessControlList
from django.core.exceptions import ValidationError,PermissionDenied

from distutils.version import LooseVersion
from django.db import models,transaction
from django.db.models import *
from django.core.validators import URLValidator
from xos.exceptions import *
import urlparse
from xos.config import Config

config = Config()

# If true, then IP addresses will be allocated by the model. If false, then
# we will assume the observer handles it.
NO_OBSERVER=False

def ParseNatList(ports):
    """ Support a list of ports in the format "protocol:port, protocol:port, ..."
        examples:
            tcp 123
            tcp 123:133
            tcp 123, tcp 124, tcp 125, udp 201, udp 202

        User can put either a "/" or a " " between protocol and ports
        Port ranges can be specified with "-" or ":"
    """
    nats = []
    if ports:
        parts = ports.split(",")
        for part in parts:
            part = part.strip()
            if "/" in part:
                (protocol, ports) = part.split("/",1)
            elif " " in part:
                (protocol, ports) = part.split(None,1)
            else:
                raise TypeError('malformed port specifier %s, format example: "tcp 123, tcp 201:206, udp 333"' % part)

            protocol = protocol.strip()
            ports = ports.strip()

            if not (protocol in ["udp", "tcp"]):
                raise ValueError('unknown protocol %s' % protocol)

            if "-" in ports:
                (first, last) = ports.split("-")
                first = int(first.strip())
                last = int(last.strip())
                portStr = "%d:%d" % (first, last)
            elif ":" in ports:
                (first, last) = ports.split(":")
                first = int(first.strip())
                last = int(last.strip())
                portStr = "%d:%d" % (first, last)
            else:
                portStr = "%d" % int(ports)

            nats.append( {"l4_protocol": protocol, "l4_port": portStr} )

    return nats

def ValidateNatList(ports):
    try:
        ParseNatList(ports)
    except Exception,e:
        raise ValidationError(str(e))



def get_default_flavor(controller = None):
    # Find a default flavor that can be used for a instance. This is particularly
    # useful in evolution. It's also intended this helper function can be used
    # for admin.py when users

    if controller:
        flavors = controller.flavors.all()
    else:
        from core.models.flavor import Flavor
        flavors = Flavor.objects.all()

    if not flavors:
        return None

    for flavor in flavors:
        if flavor.default:
            return flavor

    return flavors[0]

class InstanceDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(InstanceDeletionManager, self)
        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()
        if (backend_type):
            return parent_queryset.filter(Q(node__controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class InstanceManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(InstanceManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(node__controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()
        
def get_default_serviceclass():
    from core.models.serviceclass import ServiceClass
    try:
        return ServiceClass.objects.get(name="Best Effort")
    except ServiceClass.DoesNotExist:
        return None

class ControllerLinkDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(ControllerLinkDeletionManager, self)
        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()
        if (backend_type):
            return parent_queryset.filter(Q(controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class ControllerDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(ControllerDeletionManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

class ControllerLinkManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(ControllerLinkManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class ControllerManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(ControllerManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

