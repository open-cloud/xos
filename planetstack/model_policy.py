from django.db.models.signals import post_save
from django.dispatch import receiver
import pdb
from core.models import *
from dependency_walker import *
import model_policies
from util.logger import logger

modelPolicyEnabled = True

def EnableModelPolicy(x):
    global modelPolicyEnabled
    modelPolicyEnabled = x

def update_dep(d, o):
	try:
		if (d.updated < o.updated):
			d.save(update_fields=['updated'])
	except AttributeError,e:
		pdb.set_trace()
		raise e
	
def delete_if_inactive(d, o):
	#print "Deleting %s (%s)"%(d,d.__class__.__name__)
	d.delete()	
	return

@receiver(post_save)
def post_save_handler(sender, instance, **kwargs):
        if not modelPolicyEnabled:
            return

	sender_name = sender.__name__
	policy_name = 'model_policy_%s'%sender_name
	
	if (not kwargs['update_fields']):
		# Automatic dirtying
		walk_inv_deps(update_dep, instance)

		try:
			policy_handler = getattr(model_policies, policy_name, None)
			if policy_handler is not None:
				policy_handler.handle(instance)
		except:
			logger.log_exc("Model Policy Error:") 
	elif 'deleted' in kwargs['update_fields']:
		walk_inv_deps(delete_if_inactive, instance)
	
