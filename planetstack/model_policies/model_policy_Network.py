from core.models import *

def handle(network):
	from core.models import ControllerSlices,ControllerNetworks
	from collections import defaultdict
	# network controllers are not visible to users. We must ensure
	# networks are deployed at all deploymets available to their slices.
	slice_controllers = ControllerSlices.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_controller in slice_controllers:
		slice_deploy_lookup[slice_controller.slice].append(slice_controller.controller)

	network_controllers = ControllerNetworks.objects.all()
	network_deploy_lookup = defaultdict(list)
	for network_controller in network_controllers:
		network_deploy_lookup[network_controller.network].append(network_controller.controller)

	expected_controllers = slice_deploy_lookup[network.owner]
	for expected_controller in expected_controllers:
		if network not in network_deploy_lookup or \
		  expected_controller not in network_deploy_lookup[network]:
			nd = ControllerNetworks(network=network, controller=expected_controller)
			nd.save()
