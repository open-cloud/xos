from django.db.models.signals import post_save
from django.dispatch import receiver
import pdb
from model_policies import *

@receiver(post_save)
def post_save_handler(sender, **kwargs):
	sender_name = sender.__name__
	policy_name = 'model_policy_%s'%sender_name
	try:
		policy_handler = globals[policy_name]
		policy_handler(sender)
	except:
		pass
