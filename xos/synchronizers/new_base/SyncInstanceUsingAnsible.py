
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


import hashlib
import os
import socket
import sys
import base64
import time
from xosconfig import Config
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.ansible_helper import run_template_ssh
from synchronizers.new_base.modelaccessor import *
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


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
        # zdw, 2017-02-18 - is raising the exception here necessary? - seems like
        # it's just logging the same thing twice
        log.info("defer object", object = str(o), reason = reason, **o.tologdict())
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
        run_template_ssh(template_name, fields, object=o)
        log.info("playbook execution time", time = int(time.time() - tStart), **o.tologdict())

    def pre_sync_hook(self, o, fields):
        pass

    def post_sync_hook(self, o, fields):
        pass

    def sync_fields(self, o, fields):
        self.run_playbook(o, fields)

    def prepare_record(self, o):
        pass

    def get_node(self, o):
        return o.node

    def get_node_key(self, node):
        # NOTE `node_key` is never defined, does it differ from `proxy_ssh_key`? the value looks to be the same
        return Config.get("node_key")

    def get_key_name(self, instance):
        if instance.isolation == "vm":
            if instance.slice and instance.slice.service and instance.slice.service.private_key_fn:
                key_name = instance.slice.service.private_key_fn
            else:
                raise Exception("Make sure to set private_key_fn in the service")
        elif instance.isolation == "container":
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

            fields = {"instance_name": instance.name,
                      "hostname": instance.node.name,
                      "instance_id": instance.instance_id,
                      "username": "ubuntu",
                      "ssh_ip": instance.get_ssh_ip(),
                      }

        elif (instance.isolation == "container"):
            # container on bare metal
            node = self.get_node(instance)
            hostname = node.name
            fields = {"hostname": hostname,
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
            fields = {"hostname": instance.parent.node.name,
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

        # Now the ceilometer stuff
        # Only do this if the instance is not being deleted.
        if not instance.deleted:
            cslice = ControllerSlice.objects.get(slice_id=instance.slice.id)
            if not cslice:
                raise Exception("Controller slice object for %s does not exist" % instance.slice.name)

            cuser = ControllerUser.objects.get(user_id=instance.creator.id)
            if not cuser:
                raise Exception("Controller user object for %s does not exist" % instance.creator)

            fields.update({"keystone_tenant_id": cslice.tenant_id,
                           "keystone_user_id": cuser.kuser_id,
                           "rabbit_user": getattr(instance.controller, "rabbit_user", None),
                           "rabbit_password": getattr(instance.controller, "rabbit_password", None),
                           "rabbit_host": getattr(instance.controller, "rabbit_host", None)})

        return fields

    def sync_record(self, o):
        log.info("sync'ing object", object = str(o), **o.tologdict())

        self.prepare_record(o)

        if self.skip_ansible_fields(o):
            fields = {}
        else:
            if self.get_external_sync(o):
                # sync to some external host

                # UNTESTED

                (hostname, container_name) = self.get_external_sync(o)
                fields = {"hostname": hostname,
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

        fields["ansible_tag"] = getattr(o, "ansible_tag", o.__class__.__name__ + "_" + str(o.id))

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

            if (controller_register.get('disabled', False)):
                raise InnocuousException('Controller %s is disabled' % o.node.site_deployment.controller.name)
        except AttributeError:
            pass

        instance = self.get_instance(o)

        if not instance:
            # the instance is gone. There's nothing left for us to do.
            return

        if instance.deleted:
            # the instance is being deleted. There's nothing left for us to do.
            return

        if isinstance(instance, basestring):
            # sync to some external host

            # XXX - this probably needs more work...

            fields = {"hostname": instance,
                      "instance_id": "ubuntu",  # this is the username to log into
                      "private_key": service.key,
                      }
        else:
            # sync to an XOS instance
            fields = self.get_ansible_fields(instance)

            fields["ansible_tag"] = getattr(o, "ansible_tag", o.__class__.__name__ + "_" + str(o.id))

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        if hasattr(self, "map_delete_inputs"):
            fields.update(self.map_delete_inputs(o))

        fields['delete'] = True
        res = self.run_playbook(o, fields)

        if hasattr(self, "map_delete_outputs"):
            self.map_delete_outputs(o, res)

    # In order to enable the XOS watcher functionality for a synchronizer, define the 'watches' attribute
    # in the derived class: eg. watches = [ModelLink(ServiceDependency,via='servicedependency')]
    # This base class implements the notification handler for handling ServiceDependency model notifications
    # If a synchronizer need to watch on multiple objects, the additional handlers need to be implemented
    # in the derived class and override the below handle_watched_object() method to route the notifications
    # accordingly
    def handle_watched_object(self, o):
        log.info("handle_watched_object is invoked for object",object = str(o), **o.tologdict())
        if (model_accessor.is_type(o, "ServiceDependency")):
            self.handle_service_composition_watch_notification(o)
        elif (model_accessor.is_type(o, "ServiceMonitoringAgentInfo")):
            self.handle_service_monitoringagentinfo_watch_notification(o)
        pass

    def handle_service_composition_watch_notification(self, coarse_tenant):
        cls_obj = self.observes
        if (type(cls_obj) is list):
            cls_obj = cls_obj[0]
        log.info("handle_watched_object observed model", model = cls_obj)

        objs = cls_obj.objects.filter(kind=cls_obj.KIND)

        for obj in objs:
            self.handle_service_composition_for_object(obj, coarse_tenant)

    def handle_service_monitoringagentinfo_watch_notification(self, monitoring_agent_info):
        pass

    def handle_service_composition_for_object(self, obj, coarse_tenant):
        try:
            instance = self.get_instance(obj)
            valid_instance = True
        except:
            valid_instance = False

        if not valid_instance:
            log.warn("handle_watched_object: No valid instance found for object", object =str(obj))
            return

        provider_service = coarse_tenant.provider_service
        subscriber_service = coarse_tenant.subscriber_service

        if model_accessor.is_instance(obj, "Service"):
            if obj.id == provider_service.id:
                matched_service = provider_service
                other_service = subscriber_service
            elif obj.id == subscriber_service.id:
                matched_service = subscriber_service
                other_service = provider_service
            else:
                log.info("handle_watched_object: Service object does not match with any of composed services", 
                object = str(obj))
                return
        elif model_accessor.is_instance(obj, "Tenant"):
            if obj.provider_service.id == provider_service.id:
                matched_service = provider_service
                other_service = subscriber_service
            elif obj.provider_service.id == subscriber_service.id:
                matched_service = subscriber_service
                other_service = provider_service
            else:
                log.info(
                    "handle_watched_object: Tenant object does not match with any of composed services", object = str(obj))
                return
        else:
            log.warn("handle_watched_object: Model object is of neither Service nor Tenant type", object = str(obj))

        src_networks = matched_service.get_composable_networks()
        target_networks = other_service.get_composable_networks()
        if src_networks and target_networks:
            src_network = src_networks[0]  # Only one composable network should present per service
            target_network = target_networks[0]
            src_ip = instance.get_network_ip(src_network.name)
            target_subnet = target_network.controllernetworks.all()[0].subnet

            # Run ansible playbook to update the routing table entries in the instance
            fields = self.get_ansible_fields(instance)
            fields["ansible_tag"] = getattr(obj, "ansible_tag",
                                            obj.__class__.__name__ + "_" + str(obj.id)) + "_service_composition"
            fields["src_intf_ip"] = src_ip
            fields["target_subnet"] = target_subnet
            # Template file is available under .../synchronizers/shared_templates
            service_composition_template_name = "sync_service_composition.yaml"
            log.info(
                "handle_watched_object: Updating routing tables in the instance associated with object. target_subnet:%s src_ip:%s",
                object = str(obj), subnet = target_subnet, ip = src_ip)
            SyncInstanceUsingAnsible.run_playbook(self, obj, fields, service_composition_template_name)
        else:
            log.info("handle_watched_object: No intersection of composable networks between composed services", object = str(coarse_tenant))
