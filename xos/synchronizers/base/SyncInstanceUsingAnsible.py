import hashlib
import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from core.models import Service, Slice, ControllerSlice, ControllerUser
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncInstanceUsingAnsible(SyncStep):
    # All of the following should be defined for classes derived from this
    # base class. Examples below use VSGTenant.

    # provides=[VSGTenant]
    # observes=VSGTenant
    # requested_interval=0
    # template_name = "sync_vcpetenant.yaml"

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def skip_ansible_fields(self, o):
        # Return True if the instance processing and get_ansible_fields stuff
        # should be skipped. This hook is primarily for the OnosApp
        # sync step, so it can do its external REST API sync thing.
        return False

    def defer_sync(self, o, reason):
        logger.info("defer object %s due to %s" % (str(o), reason),extra=o.tologdict())
        raise Exception("defer object %s due to %s" % (str(o), reason))

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes that aren't part of the
        # object itself.

        return {}

    def get_instance(self, o):
        # We need to know what instance is associated with the object. Let's
        # assume 'o' has a field called 'instance'. If the field is called
        # something else, or if custom logic is needed, then override this
        # method.

        return o.instance

    def get_external_sync(self, o):
        hostname = getattr(o, "external_hostname", None)
        container = getattr(o, "external_container", None)
        if hostname and container:
            return (hostname, container)
        else:
            return None

    def run_playbook(self, o, fields, template_name=None):
        if not template_name:
            template_name = self.template_name
        tStart = time.time()
        run_template_ssh(template_name, fields)
        logger.info("playbook execution time %d" % int(time.time()-tStart),extra=o.tologdict())

    def pre_sync_hook(self, o, fields):
        pass

    def post_sync_hook(self, o, fields):
        pass

    def sync_fields(self, o, fields):
        self.run_playbook(o, fields)

    def prepare_record(self, o):
        pass

    def get_node(self,o):
        return o.node

    def get_node_key(self, node):
        return "/root/setup/node_key"

    def get_key_name(self, instance):
        if instance.isolation=="vm":
            if (instance.slice) and (instance.slice.service) and (instance.slice.service.private_key_fn):
                key_name = instance.slice.service.private_key_fn
            else:
                raise Exception("Make sure to set private_key_fn in the service")
        elif instance.isolation=="container":
            node = self.get_node(instance)
            key_name = self.get_node_key(node)
        else:
            # container in VM
            key_name = instance.parent.slice.service.private_key_fn

        return key_name

    def get_ansible_fields(self, instance):
        # return all of the fields that tell Ansible how to talk to the context
        # that's setting up the container.

        if (instance.isolation == "vm"):
            # legacy where container was configured by sync_vcpetenant.py

            fields = { "instance_name": instance.name,
                       "hostname": instance.node.name,
                       "instance_id": instance.instance_id,
                       "username": "ubuntu",
                       "ssh_ip": instance.get_ssh_ip(),
                     }

        elif (instance.isolation == "container"):
            # container on bare metal
            node = self.get_node(instance)
            hostname = node.name
            fields = { "hostname": hostname,
                       "baremetal_ssh": True,
                       "instance_name": "rootcontext",
                       "username": "root",
                       "container_name": "%s-%s" % (instance.slice.name, str(instance.id))
                       # ssh_ip is not used for container-on-metal
                     }
        else:
            # container in a VM
            if not instance.parent:
                raise Exception("Container-in-VM has no parent")
            if not instance.parent.instance_id:
                raise Exception("Container-in-VM parent is not yet instantiated")
            if not instance.parent.slice.service:
                raise Exception("Container-in-VM parent has no service")
            if not instance.parent.slice.service.private_key_fn:
                raise Exception("Container-in-VM parent service has no private_key_fn")
            fields = { "hostname": instance.parent.node.name,
                       "instance_name": instance.parent.name,
                       "instance_id": instance.parent.instance_id,
                       "username": "ubuntu",
                       "ssh_ip": instance.parent.get_ssh_ip(),
                       "container_name": "%s-%s" % (instance.slice.name, str(instance.id))
                         }

        key_name = self.get_key_name(instance)
        if not os.path.exists(key_name):
            raise Exception("Node key %s does not exist" % key_name)

        key = file(key_name).read()

        fields["private_key"] = key

        # now the ceilometer stuff

        cslice = ControllerSlice.objects.get(slice=instance.slice)
        if not cslice:
            raise Exception("Controller slice object for %s does not exist" % instance.slice.name)

        cuser = ControllerUser.objects.get(user=instance.creator)
        if not cuser:
            raise Exception("Controller user object for %s does not exist" % instance.creator)

        fields.update({"keystone_tenant_id": cslice.tenant_id,
                       "keystone_user_id": cuser.kuser_id,
                       "rabbit_user": getattr(instance.controller,"rabbit_user", None),
                       "rabbit_password": getattr(instance.controller, "rabbit_password", None),
                       "rabbit_host": getattr(instance.controller, "rabbit_host", None)})

        return fields

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o),extra=o.tologdict())

        self.prepare_record(o)

        if self.skip_ansible_fields(o):
            fields = {}
        else:
            if self.get_external_sync(o):
                # sync to some external host

                # UNTESTED

                (hostname, container_name) = self.get_external_sync(o)
                fields = { "hostname": hostname,
                           "baremetal_ssh": True,
                           "instance_name": "rootcontext",
                           "username": "root",
                           "container_name": container_name
                         }
                key_name = self.get_node_key(node)
                if not os.path.exists(key_name):
                    raise Exception("Node key %s does not exist" % key_name)

                key = file(key_name).read()

                fields["private_key"] = key
                # TO DO: Ceilometer stuff
            else:
                instance = self.get_instance(o)
                # sync to an XOS instance
                if not instance:
                    self.defer_sync(o, "waiting on instance")
                    return

                if not instance.instance_name:
                    self.defer_sync(o, "waiting on instance.instance_name")
                    return

                fields = self.get_ansible_fields(instance)

        fields["ansible_tag"] =  o.__class__.__name__ + "_" + str(o.id)

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.sync_fields(o, fields)

        o.save()

    def delete_record(self, o):
        try:
            controller = o.get_controller()
            controller_register = json.loads(o.node.site_deployment.controller.backend_register)

            if (controller_register.get('disabled',False)):
                raise InnocuousException('Controller %s is disabled'%o.node.site_deployment.controller.name)
        except AttributeError:
            pass

        instance = self.get_instance(o)
        if isinstance(instance, basestring):
            # sync to some external host

            # XXX - this probably needs more work...

            fields = { "hostname": instance,
                       "instance_id": "ubuntu",     # this is the username to log into
                       "private_key": service.key,
                     }
        else:
            # sync to an XOS instance
            fields = self.get_ansible_fields(instance)

            fields["ansible_tag"] =  o.__class__.__name__ + "_" + str(o.id)

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.map_delete_inputs(o))

        fields['delete']=True
        res = self.run_playbook(o,fields)
        try:
                self.map_delete_outputs(o,res)
        except AttributeError:
                pass
