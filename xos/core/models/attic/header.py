
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import

import sys
import json
import operator
from operator import attrgetter
from core.models.xosbase import *
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

