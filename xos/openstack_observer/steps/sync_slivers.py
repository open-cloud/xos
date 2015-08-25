import os
import base64
import socket
from django.db.models import F, Q
from xos.config import Config
from xos.settings import RESTAPI_HOSTNAME, RESTAPI_PORT
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import Slice, SlicePrivilege, ControllerSlice
from core.models.network import Network, NetworkSlice, ControllerNetwork
from observer.ansible import *
from observer.syncstep import *
from util.logger import observer_logger as logger

def escape(s):
    s = s.replace('\n',r'\n').replace('"',r'\"')
    return s

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0
    observes=Sliver

    def get_userdata(self, sliver, pubkeys):
        userdata = '#cloud-config\n\nopencloud:\n   slicename: "%s"\n   hostname: "%s"\n   restapi_hostname: "%s"\n   restapi_port: "%s"\n' % (sliver.slice.name, sliver.node.name, RESTAPI_HOSTNAME, str(RESTAPI_PORT))
        userdata += 'ssh_authorized_keys:\n'
        for key in pubkeys:
            userdata += '  - %s\n' % key
        return userdata

    def sync_record(self, sliver):
        logger.info("sync'ing sliver:%s slice:%s controller:%s " % (sliver, sliver.slice.name, sliver.node.site_deployment.controller))
        controller_register = json.loads(sliver.node.site_deployment.controller.backend_register)

        if (controller_register.get('disabled',False)):
            raise InnocuousException('Controller %s is disabled'%sliver.node.site_deployment.controller.name)

        metadata_update = {}
        if (sliver.numberCores):
            metadata_update["cpu_cores"] = str(sliver.numberCores)

        for tag in sliver.slice.tags.all():
            if tag.name.startswith("sysctl-"):
                metadata_update[tag.name] = tag.value

        # public keys
        slice_memberships = SlicePrivilege.objects.filter(slice=sliver.slice)
        pubkeys = set([sm.user.public_key for sm in slice_memberships if sm.user.public_key])
        if sliver.creator.public_key:
            pubkeys.add(sliver.creator.public_key)

        if sliver.slice.creator.public_key:
            pubkeys.add(sliver.slice.creator.public_key)

        if sliver.slice.service and sliver.slice.service.public_key:
            pubkeys.add(sliver.slice.service.public_key)

        # Handle any ports that are already created and attached to the sliver.
        # If we do have a port for a network, then add that network to an
        # exclude list so we won't try to auto-create ports on that network
        # when instantiating.
        ports = []
        exclude_networks = set()
        exclude_templates = set()
        for ns in sliver.networkslivers.all():
            if not ns.port_id:
                raise DeferredException("Port %s on sliver %s has no id; Try again later" % (str(ns), str(sliver)) )
            ports.append(ns.port_id)
            exclude_networks.add(ns.network)
            exclude_templates.add(ns.network.template)

        nics = []
        networks = [ns.network for ns in NetworkSlice.objects.filter(slice=sliver.slice)]
        networks = [n for n in networks if (n not in exclude_networks)]
        controller_networks = ControllerNetwork.objects.filter(network__in=networks,
                                                                controller=sliver.node.site_deployment.controller)

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

        #driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, controller=sliver.controllerNetwork)
        driver = self.driver.admin_driver(tenant='admin', controller=sliver.node.site_deployment.controller)
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
        controller_images = sliver.image.controllerimages.filter(controller=sliver.node.site_deployment.controller)
        if controller_images:
            image_name = controller_images[0].image.name
            logger.info("using image from ControllerImage object: " + str(image_name))

        if image_name is None:
            controller_driver = self.driver.admin_driver(controller=sliver.node.site_deployment.controller)
            images = controller_driver.shell.glanceclient.images.list()
            for image in images:
                if image.name == sliver.image.name or not image_name:
                    image_name = image.name
                    logger.info("using image from glance: " + str(image_name))

        try:
            legacy = Config().observer_legacy
        except:
            legacy = False

        if (legacy):
            host_filter = sliver.node.name.split('.',1)[0]
        else:
            host_filter = sliver.node.name.strip()

        availability_zone_filter = 'nova:%s'%host_filter
        sliver_name = '%s-%d'%(sliver.slice.name,sliver.id)

        userData = self.get_userdata(sliver, pubkeys)
        if sliver.userData:
            userData = sliver.userData

        controller = sliver.node.site_deployment.controller
        tenant_fields = {'endpoint':controller.auth_url,
                     'admin_user': sliver.creator.email,
                     'admin_password': sliver.creator.remote_password,
                     'admin_tenant': sliver.slice.name,
                     'tenant': sliver.slice.name,
                     'tenant_description': sliver.slice.description,
                     'name':sliver_name,
                     'ansible_tag':sliver_name,
                     'availability_zone': availability_zone_filter,
                     'image_name':image_name,
                     'flavor_name':sliver.flavor.name,
                     'nics':nics,
                     'ports':ports,
                     'meta':metadata_update,
                     'user_data':r'%s'%escape(userData)}

        res = run_template('sync_slivers.yaml', tenant_fields,path='slivers', expected_num=1)
        sliver_id = res[0]['info']['OS-EXT-SRV-ATTR:instance_name']
        sliver_uuid = res[0]['id']

        try:
            hostname = res[0]['info']['OS-EXT-SRV-ATTR:hypervisor_hostname']
            ip = socket.gethostbyname(hostname)
            sliver.ip = ip
        except:
            pass

        sliver.instance_id = sliver_id
        sliver.instance_uuid = sliver_uuid
        sliver.instance_name = sliver_name
        sliver.save()

    def delete_record(self, sliver):
        controller_register = json.loads(sliver.node.site_deployment.controller.backend_register)

        if (controller_register.get('disabled',False)):
            raise InnocuousException('Controller %s is disabled'%sliver.node.site_deployment.controller.name)

        sliver_name = '%s-%d'%(sliver.slice.name,sliver.id)
        controller = sliver.node.site_deployment.controller
        tenant_fields = {'endpoint':controller.auth_url,
                     'admin_user': sliver.creator.email,
                     'admin_password': sliver.creator.remote_password,
                     'admin_tenant': sliver.slice.name,
                     'tenant': sliver.slice.name,
                     'tenant_description': sliver.slice.description,
                     'name':sliver_name,
                     'ansible_tag':sliver_name,
                     'delete': True}

        try:
            res = run_template('sync_slivers.yaml', tenant_fields,path='slivers', expected_num=1)
        except Exception,e:
            print "Could not sync %s"%sliver_name
            #import traceback
            #traceback.print_exc()
            raise e

        if (len(res)!=1):
            raise Exception('Could not delete sliver %s'%sliver.slice.name)
