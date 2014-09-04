from django.core.signals import post_save
from django.dispatch import receiver
import pdb

@receiver(post_save)
def post_save_handler(sender, **kwargs):
	pdb.set_trace()
    print("Request finished!")
