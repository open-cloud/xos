from core.models import *

def handle(network):
	from core.models import ControllerSlice,ControllerNetwork, Network
	from collections import defaultdict

        print "MODEL POLICY: network", network

        # network = Network.get(network_id)
	# network controllers are not visible to users. We must ensure
	# networks are deployed at all deploymets available to their slices.
	slice_controllers = ControllerSlice.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_controller in slice_controllers:
		slice_deploy_lookup[slice_controller.slice].append(slice_controller.controller)

	network_controllers = ControllerNetwork.objects.all()
	network_deploy_lookup = defaultdict(list)
	for network_controller in network_controllers:
		network_deploy_lookup[network_controller.network].append(network_controller.controller)

	expected_controllers = slice_deploy_lookup[network.owner]
	for expected_controller in expected_controllers:
		if network not in network_deploy_lookup or \
		  expected_controller not in network_deploy_lookup[network]:
                        lazy_blocked=True

                        # check and see if some instance already exists
                        for networkslice in network.networkslices.all():
                            if networkslice.slice.instances.filter(node__site_deployment__controller=expected_controller).exists():
                               print "MODEL_POLICY: network, setting lazy_blocked to false because instance on controller already exists"
                               lazy_blocked=False

			nd = ControllerNetwork(network=network, controller=expected_controller, lazy_blocked=lazy_blocked)
                        print "MODEL POLICY: network", network, "create ControllerNetwork", nd, "lazy_blocked", lazy_blocked
                        if network.subnet:
                            # XXX: Possibly unpredictable behavior if there is
                            # more than one ControllerNetwork and the subnet
                            # is specified.
                            nd.subnet = network.subnet
			nd.save()
