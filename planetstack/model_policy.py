from django.db.models.signals import post_save
from django.dispatch import receiver
import pdb
from core.models import *
import model_policies

modelPolicyEnabled = True

def EnableModelPolicy(x):
    global modelPolicyEnabled
    modelPolicyEnabled = x

@receiver(post_save)
def post_save_handler(sender, instance, **kwargs):
	sender_name = sender.__name__
	policy_name = 'model_policy_%s'%sender_name

        if not modelPolicyEnabled:
            return
	
	if (not kwargs['update_fields']):
		try:
			policy_handler = getattr(model_policies, policy_name, None)
			if policy_handler is not None:
				policy_handler.handle(instance)
		except:
			pass
