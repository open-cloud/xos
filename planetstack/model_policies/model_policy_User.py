from core.models import *

def handle(user):
	from core.models import Controller, ControllerSiteDeployments, ControllerUsers
	from collections import defaultdict
	ctrl_site_deployments = ControllerSiteDeployments.objects.all()
	controller_lookup = defaultdict(list)
	for ctrl_site_deployment in ctrl_site_deployments:
		controller_site_lookup[ctrl_site_deployment.site_deployment].append(ctrl_site_deployment)

	controller_user_lookup = defaultdict(list)
	for controller_user in ControllerUsers.objects.all():
		controller_user_lookup[controller_user.user].append(controller_user.controller)
   
	if user.is_admin:
		# admins should have an account at all controllers
		expected_controllers = controllers
	else:
		# normal users should have an account at their site's controllers
		#expected_controllers = controller_site_lookup[user.site]
		# users are added to all controllers for now
		expected_controllers = controllers        

	for expected_controller in expected_controllers:
		if not user in controller_user_lookup or \
		  expected_controller not in controller_user_lookup[user]: 
			# add new record
			ud = ControllerUsers(user=user, controller=expected_controller)
			ud.save()    

