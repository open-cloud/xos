import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import Slice, SlicePrivilege, ControllerSlices
from core.models.network import Network, NetworkSlice, ControllerNetworks
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
        logger.info("sync'ing sliver:%s slice:%s controller:%s " % (sliver, sliver.slice.name, sliver.node.site_controller))

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
	controller_networks = ControllerNetworks.objects.filter(network__in=networks, 
								controller=sliver.node.site_controller.controller)

	for controller_network in controller_networks:
	    if controller_network.network.template.visibility == 'private' and \
	       controller_network.network.template.translation == 'none' and controller_network.net_id: 
		nics.append(controller_network.net_id)

        # now include network template
        network_templates = [network.template.sharedNetworkName for network in networks \
                             if network.template.sharedNetworkName]

        #driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, controller=sliver.controllerNetwork)
        driver = self.driver.admin_driver(tenant='admin', controller=sliver.controllerNetwork)
	nets = driver.shell.quantum.list_networks()['networks']
	for net in nets:
	    if net['name'] in network_templates: 
		nics.append(net['id']) 

	if (not nics):
	    for net in nets:
	        if net['name']=='public':
	    	    nics.append(net['id'])

	# look up image id
	controller_driver = self.driver.admin_driver(controller=sliver.controllerNetwork.name)
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
	    

	userData = self.get_userdata(sliver)
	if sliver.userData:
	    userData = sliver.userData
	    
	sliver_name = '@'.join([sliver.slice.name,sliver.node.name])
	tenant_fields = {'endpoint':sliver.node.controller.auth_url,
		     'admin_user': sliver.node.controller.admin_user,
		     'admin_password': sliver.node.controller.admin_password,
		     'admin_tenant': 'admin',
		     'tenant': sliver.slice.name,
		     'tenant_description': sliver.slice.description,
		     'name':sliver_name,
		     'image_id':image_id,
		     'key_name':keyname,
		     'flavor_id':1,
		     'nics':nics,
		     'meta':metadata_update,
		     'key':key_fields,
		     'user_data':r'%s'%escape(userData)}

	res = run_template('sync_slivers.yaml', tenant_fields)
	if (len(res)!=2):
	    raise Exception('Could not sync sliver %s'%sliver.slice.name)
	else:
	    sliver_id = res[1]['id'] # 0 is for the key

            sliver.instance_id = sliver_id
            sliver.instance_name = sliver_name
            sliver.save()

    def delete_record(self, sliver):
        sliver_name = '@'.join([sliver.slice.name,sliver.node.name])
        tenant_fields = {'name':sliver_name,
                         'ansible_tag':sliver_name
                        }
        res = run_template('delete_slivers.yaml', tenant_fields, path='slivers')
