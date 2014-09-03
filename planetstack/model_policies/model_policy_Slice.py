from core.models import *

def handle(slice):
	site_deployments = SiteDeployments.objects.all()
	site_deploy_lookup = defaultdict(list)
	for site_deployment in site_deployments:
		site_deploy_lookup[site_deployment.site].append(site_deployment.deployment)
	
	slice_deployments = SliceDeployments.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_deployment in slice_deployments:
		slice_deploy_lookup[slice_deployment.slice].append(slice_deployment.deployment)
	
	all_deployments = Deployment.objects.all() 
	# slices are added to all deployments for now
	expected_deployments = all_deployments
	#expected_deployments = site_deploy_lookup[slice.site]
	for expected_deployment in expected_deployments:
		if slice not in slice_deploy_lookup or \
		   expected_deployment not in slice_deploy_lookup[slice]:
			sd = SliceDeployments(slice=slice, deployment=expected_deployment)
			sd.save()

