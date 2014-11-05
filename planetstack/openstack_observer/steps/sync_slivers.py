import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import Slice, SlicePrivilege, SliceDeployments
from core.models.network import Network, NetworkSlice, NetworkDeployments
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
        logger.info("sync'ing sliver:%s deployment:%s " % (sliver, sliver.node.deployment))

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
	network_deployments = NetworkDeployments.objects.filter(network__in=networks, 
								deployment=sliver.node.deployment)

	for network_deployment in network_deployments:
	    if network_deployment.network.template.visibility == 'private' and \
	       network_deployment.network.template.translation == 'none' and network_deployment.net_id: 
		nics.append(network_deployment.net_id)

	# now include network template
	network_templates = [network.template.sharedNetworkName for network in networks \
			     if network.template.sharedNetworkName]

        #driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.deploymentNetwork)
        driver = self.driver.admin_driver(tenant='admin', deployment=sliver.deploymentNetwork)
	nets = driver.shell.quantum.list_networks()['networks']
	for net in nets:
	    if net['name'] in network_templates: 
		nics.append(net['id']) 

	if (not nics):
	    for net in nets:
	        if net['name']=='public':
	    	    nics.append(net['id'])

	# look up image id
	deployment_driver = self.driver.admin_driver(deployment=sliver.deploymentNetwork.name)
	image_id = None
	images = deployment_driver.shell.glanceclient.images.list()
	for image in images:
	    if image.name == sliver.image.name or not image_id:
		image_id = image.id
		
	# look up key name at the deployment
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
	tenant_fields = {'endpoint':sliver.node.deployment.auth_url,
		     'admin_user': sliver.node.deployment.admin_user,
		     'admin_password': sliver.node.deployment.admin_password,
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
        if sliver.instance_id:
            driver = self.driver.client_driver(caller=sliver.creator, 
                                               tenant=sliver.slice.name,
                                               deployment=sliver.deploymentNetwork.name)
            driver.destroy_instance(sliver.instance_id)
