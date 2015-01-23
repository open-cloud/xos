import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import Slice, SlicePrivilege, ControllerSlice
from core.models.network import Network, NetworkSlice, ControllerNetwork
from util.logger import Logger, logging
from observer.ansible import *

logger = Logger(level=logging.INFO)

def escape(s):
    s = s.replace('\n',r'\n').replace('"',r'\"')
    return s

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def get_userdata(self, sliver):
        userdata = 'opencloud:\n   slicename: "%s"\n   hostname: "%s"\n' % (sliver.slice.name, sliver.node.name)
        return userdata

    def sync_record(self, sliver):
        logger.info("sync'ing sliver:%s slice:%s controller:%s " % (sliver, sliver.slice.name, sliver.node.site_deployment.controller))

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

        nics = []
        networks = [ns.network for ns in NetworkSlice.objects.filter(slice=sliver.slice)]
        controller_networks = ControllerNetwork.objects.filter(network__in=networks,
                                                                controller=sliver.node.site_deployment.controller)

        for controller_network in controller_networks:
            if controller_network.network.template.visibility == 'private' and \
               controller_network.network.template.translation == 'none' and controller_network.net_id:
                nics.append(controller_network.net_id)

        # now include network template
        network_templates = [network.template.shared_network_name for network in networks \
                             if network.template.shared_network_name]

        #driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, controller=sliver.controllerNetwork)
        driver = self.driver.admin_driver(tenant='admin', controller=sliver.node.site_deployment.controller)
        nets = driver.shell.quantum.list_networks()['networks']
        for net in nets:
            if net['name'] in network_templates:
                nics.append(net['id'])

        if (not nics):
            for net in nets:
                if net['name']=='public':
                    nics.append(net['id'])

        # look up image id
        controller_driver = self.driver.admin_driver(controller=sliver.node.site_deployment.controller)
        image_id = None
        images = controller_driver.shell.glanceclient.images.list()
        for image in images:
            if image.name == sliver.image.name or not image_id:
                image_id = image.id

        # look up key name at the controller
        # create/fetch keypair
        keyname = None
        keyname = sliver.creator.email.lower().replace('@', 'AT').replace('.', '') +\
                  sliver.slice.name
        key_fields =  {'name': keyname,
                       'public_key': sliver.creator.public_key}

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

        userData = self.get_userdata(sliver)
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
                     'image_id':image_id,
                     'key_name':keyname,
                     'flavor_id':sliver.flavor.id,
                     'nics':nics,
                     'meta':metadata_update,
                     'key':key_fields,
                     'user_data':r'%s'%escape(userData)}

        res = run_template('sync_slivers.yaml', tenant_fields,path='slivers', expected_num=2)
        sliver_id = res[1]['info']['OS-EXT-SRV-ATTR:instance_name'] # 0 is for the key
        sliver_uuid = res[1]['id'] # 0 is for the key

        try:
            hostname = res[1]['info']['OS-EXT-SRV-ATTR:hypervisor_hostname']
            ip = socket.gethostbyname(hostname)
            sliver.ip = ip
        except:
            pass

        sliver.instance_id = sliver_id
        sliver.instance_uuid = sliver_uuid
        sliver.instance_name = sliver_name
        sliver.save()

    def delete_record(self, sliver):
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

        res = run_template('sync_slivers.yaml', tenant_fields,path='slivers')
        if (len(res)!=1):
            raise Exception('Could not delete sliver %s'%sliver.slice.name)
