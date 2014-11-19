from core.models import *

def handle(user):
	from core.models import Deployment,SiteDeployments,UserDeployments
	from collections import defaultdict
	deployments = Deployment.objects.all()
	site_deployments = SiteDeployments.objects.all()
	site_deploy_lookup = defaultdict(list)
	for site_deployment in site_deployments:
		site_deploy_lookup[site_deployment.site].append(site_deployment.deployment)

	user_deploy_lookup = defaultdict(list)
	for user_deployment in UserDeployments.objects.all():
		user_deploy_lookup[user_deployment.user].append(user_deployment.deployment)
   
	all_deployments = Deployment.objects.filter() 
	if user.is_admin:
		# admins should have an account at all deployments
		expected_deployments = deployments
	else:
		# normal users should have an account at their site's deployments
		#expected_deployments = site_deploy_lookup[user.site]
		# users are added to all deployments for now
		expected_deployments = deployments        

	for expected_deployment in expected_deployments:
		if not user in user_deploy_lookup or \
		  expected_deployment not in user_deploy_lookup[user]: 
			# add new record
			ud = UserDeployments(user=user, deployment=expected_deployment)
			ud.save()    

