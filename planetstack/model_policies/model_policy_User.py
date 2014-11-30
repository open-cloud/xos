from core.models import *

def handle(user):
	from core.models import Controller,ControllerSites,ControllerUsers
	from collections import defaultdict
	controllers = Controller.objects.all()
	controller_sitements = ControllerSites.objects.all()
	controller_site_lookup = defaultdict(list)
	for controller_sitement in controller_sitements:
		controller_site_lookup[controller_sitement.site].append(controller_sitement.controller)

	controller_user_lookup = defaultdict(list)
	for controller_userment in ControllerUsers.objects.all():
		controller_user_lookup[controller_userment.user].append(controller_userment.controller)
   
	all_controllers = Controller.objects.filter() 
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

