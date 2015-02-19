from django.db.models.signals import post_save
from django.dispatch import receiver
import pdb
from dependency_walker import *
import model_policies
from util.logger import logger
from django.utils import timezone
import time
from core.models import *
from django.db.transaction import atomic
from django.db.models import F, Q

modelPolicyEnabled = True

def EnableModelPolicy(x):
    global modelPolicyEnabled
    modelPolicyEnabled = x

def update_dep(d, o):
	try:
		if (d.updated < o.updated):
			d.save(update_fields=['updated'])
	except AttributeError,e:
		raise e
	
def delete_if_inactive(d, o):
	#print "Deleting %s (%s)"%(d,d.__class__.__name__)
	# d.delete()	
	return

@atomic
def execute_model_policy(instance, deleted):
	# Automatic dirtying
	walk_inv_deps(update_dep, instance)

	sender_name = instance.__class__.__name__
	policy_name = 'model_policy_%s'%sender_name
	noargs = False

	if deleted:
		walk_inv_deps(delete_if_inactive, instance)
	else:
		try:
			policy_handler = getattr(model_policies, policy_name, None)
			logger.error("POLICY HANDLER: %s %s" % (policy_name, policy_handler))                       
			if policy_handler is not None:
				policy_handler.handle(instance)
		except:
			logger.log_exc("Model Policy Error:") 
			print "Policy Exceution Error"

	instance.policed=timezone.now()
        instance.save(update_fields=['policed'])

def run_policy():
        from core.models import Slice,Controller,Network,User,SlicePrivilege,Site,SitePrivilege,Image,ControllerSlice,ControllerUser,ControllerSite
	while (True):
		start = time.time()
		models = [Slice, Controller, Network, User, SlicePrivilege, Site, SitePrivilege, Image, ControllerSlice, ControllerSite, ControllerUser]
		objects = []
		
		for m in models:
        		res = m.objects.filter(Q(policed__lt=F('updated')) | Q(policed=None))
			objects.extend(res)	

		for o in objects:
			print "Working on %r"%o
			execute_model_policy(o, False)
		
		
		if (time.time()-start<1):
			time.sleep(1)	
