import os
import base64
import socket
from django.db.models import F, Q
from xos.config import Config
from xos.settings import RESTAPI_HOSTNAME, RESTAPI_PORT
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.instance import Instance
from core.models.slice import Slice, SlicePrivilege, ControllerSlice
from core.models.network import Network, NetworkSlice, ControllerNetwork
from observer.ansible import *
from observer.syncstep import *
from util.logger import observer_logger as logger

def escape(s):
    s = s.replace('\n',r'\n').replace('"',r'\"')
    return s

class SyncInstances(OpenStackSyncStep):
    provides=[Instance]
    requested_interval=0
    observes=Instance

    def get_userdata(self, instance, pubkeys):
        userdata = '#cloud-config\n\nopencloud:\n   slicename: "%s"\n   hostname: "%s"\n   restapi_hostname: "%s"\n   restapi_port: "%s"\n' % (instance.slice.name, instance.node.name, RESTAPI_HOSTNAME, str(RESTAPI_PORT))
        userdata += 'ssh_authorized_keys:\n'
        for key in pubkeys:
            userdata += '  - %s\n' % key
        return userdata

    def sync_record(self, instance):
        logger.info("sync'ing instance:%s slice:%s controller:%s " % (instance, instance.slice.name, instance.node.site_deployment.controller))
        controller_register = json.loads(instance.node.site_deployment.controller.backend_register)

        if (controller_register.get('disabled',False)):
            raise InnocuousException('Controller %s is disabled'%instance.node.site_deployment.controller.name)

        metadata_update = {}
        if (instance.numberCores):
            metadata_update["cpu_cores"] = str(instance.numberCores)

        for tag in instance.slice.tags.all():
            if tag.name.startswith("sysctl-"):
                metadata_update[tag.name] = tag.value

        # public keys
        slice_memberships = SlicePrivilege.objects.filter(slice=instance.slice)
        pubkeys = set([sm.user.public_key for sm in slice_memberships if sm.user.public_key])
        if instance.creator.public_key:
            pubkeys.add(instance.creator.public_key)

        if instance.slice.creator.public_key:
            pubkeys.add(instance.slice.creator.public_key)

        if instance.slice.service and instance.slice.service.public_key:
            pubkeys.add(instance.slice.service.public_key)

        # Handle any ports that are already created and attached to the sliver.
        # If we do have a port for a network, then add that network to an
        # exclude list so we won't try to auto-create ports on that network
        # when instantiating.
        ports = []
        exclude_networks = set()
        exclude_templates = set()
        for ns in sliver.ports.all():
            if not ns.port_id:
                raise DeferredException("Port %s on sliver %s has no id; Try again later" % (str(ns), str(sliver)) )
            ports.append(ns.port_id)
            exclude_networks.add(ns.network)
            exclude_templates.add(ns.network.template)

        nics = []
        networks = [ns.network for ns in NetworkSlice.objects.filter(slice=instance.slice)]
        networks = [n for n in networks if (n not in exclude_networks)]
        controller_networks = ControllerNetwork.objects.filter(network__in=networks,
                                                                controller=instance.node.site_deployment.controller)

        for controller_network in controller_networks:
            if controller_network.network.template.visibility == 'private' and \
               controller_network.network.template.translation == 'none':
                   if not controller_network.net_id:
                        raise DeferredException("Private Network %s has no id; Try again later" % controller_network.network.name)
                   nics.append(controller_network.net_id)

        # Now include network templates, for those networks that use a
        # shared_network_name.
        network_templates = [network.template.shared_network_name for network in networks \
                             if network.template.shared_network_name]
        network_templates = [nt for nt in network_templates if (nt not in exclude_templates)]

        #driver = self.driver.client_driver(caller=instance.creator, tenant=instance.slice.name, controller=instance.controllerNetwork)
        driver = self.driver.admin_driver(tenant='admin', controller=instance.node.site_deployment.controller)
        nets = driver.shell.quantum.list_networks()['networks']
        for net in nets:
            if net['name'] in network_templates:
                nics.append(net['id'])

        # If the slice isn't connected to anything, then at least put it on
        # the public network.
        if (not nics) and (not ports):
            for net in nets:
                if net['name']=='public':
                    nics.append(net['id'])

        image_name = None
        controller_images = instance.image.controllerimages.filter(controller=instance.node.site_deployment.controller)
        if controller_images:
            image_name = controller_images[0].image.name
            logger.info("using image from ControllerImage object: " + str(image_name))

        if image_name is None:
            controller_driver = self.driver.admin_driver(controller=instance.node.site_deployment.controller)
            images = controller_driver.shell.glanceclient.images.list()
            for image in images:
                if image.name == instance.image.name or not image_name:
                    image_name = image.name
                    logger.info("using image from glance: " + str(image_name))

        try:
            legacy = Config().observer_legacy
        except:
            legacy = False

        if (legacy):
            host_filter = instance.node.name.split('.',1)[0]
        else:
            host_filter = instance.node.name.strip()

        availability_zone_filter = 'nova:%s'%host_filter
        instance_name = '%s-%d'%(instance.slice.name,instance.id)

        userData = self.get_userdata(instance, pubkeys)
        if instance.userData:
            userData = instance.userData

        controller = instance.node.site_deployment.controller
        tenant_fields = {'endpoint':controller.auth_url,
                     'admin_user': instance.creator.email,
                     'admin_password': instance.creator.remote_password,
                     'admin_tenant': instance.slice.name,
                     'tenant': instance.slice.name,
                     'tenant_description': instance.slice.description,
                     'name':instance_name,
                     'ansible_tag':instance_name,
                     'availability_zone': availability_zone_filter,
                     'image_name':image_name,
                     'flavor_name':instance.flavor.name,
                     'nics':nics,
                     'ports':ports,
                     'meta':metadata_update,
                     'user_data':r'%s'%escape(userData)}

        res = run_template('sync_instances.yaml', tenant_fields,path='instances', expected_num=1)
        instance_id = res[0]['info']['OS-EXT-SRV-ATTR:instance_name']
        instance_uuid = res[0]['id']

        try:
            hostname = res[0]['info']['OS-EXT-SRV-ATTR:hypervisor_hostname']
            ip = socket.gethostbyname(hostname)
            instance.ip = ip
        except:
            pass

        instance.instance_id = instance_id
        instance.instance_uuid = instance_uuid
        instance.instance_name = instance_name
        instance.save()

    def delete_record(self, instance):
        controller_register = json.loads(instance.node.site_deployment.controller.backend_register)

        if (controller_register.get('disabled',False)):
            raise InnocuousException('Controller %s is disabled'%instance.node.site_deployment.controller.name)

        instance_name = '%s-%d'%(instance.slice.name,instance.id)
        controller = instance.node.site_deployment.controller
        tenant_fields = {'endpoint':controller.auth_url,
                     'admin_user': instance.creator.email,
                     'admin_password': instance.creator.remote_password,
                     'admin_tenant': instance.slice.name,
                     'tenant': instance.slice.name,
                     'tenant_description': instance.slice.description,
                     'name':instance_name,
                     'ansible_tag':instance_name,
                     'delete': True}

        try:
            res = run_template('sync_instances.yaml', tenant_fields,path='instances', expected_num=1)
        except Exception,e:
            print "Could not sync %s"%instance_name
            #import traceback
            #traceback.print_exc()
            raise e

        if (len(res)!=1):
            raise Exception('Could not delete instance %s'%instance.slice.name)
