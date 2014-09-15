from core.models import *

def handle(network):
	from core.models import SliceDeployments,NetworkDeployments
	from collections import defaultdict
	# network deployments are not visible to users. We must ensure
	# networks are deployed at all deploymets available to their slices.
	slice_deployments = SliceDeployments.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_deployment in slice_deployments:
		slice_deploy_lookup[slice_deployment.slice].append(slice_deployment.deployment)

	network_deployments = NetworkDeployments.objects.all()
	network_deploy_lookup = defaultdict(list)
	for network_deployment in network_deployments:
		network_deploy_lookup[network_deployment.network].append(network_deployment.deployment)

	expected_deployments = slice_deploy_lookup[network.owner]
	for expected_deployment in expected_deployments:
		if network not in network_deploy_lookup or \
		  expected_deployment not in network_deploy_lookup[network]:
			nd = NetworkDeployments(network=network, deployment=expected_deployment)
			nd.save()
