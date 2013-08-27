import os
import base64
from planetstack.config import Config

class SyncStep:
	""" A PlanetStack Sync step. 

	Attributes:
		psmodel		Model name the step synchronizes 
		dependencies	list of names of models that must be synchronized first if the current model depends on them
	""" 
	slow=False
	def get_prop(prop):
		try:
			sync_config_dir = Config().sync_config_dir
		except:
			sync_config_dir = '/etc/planetstack/sync'
		prop_config_path = '/'.join(sync_config_dir,self.name,prop)
		return open(prop_config_path).read().rstrip()

	def __init__(self, **args):
		"""Initialize a sync step
		   Keyword arguments:
		   		name -- Name of the step
				provides -- PlanetStack models sync'd by this step
		"""
		try:
			self.soft_deadline = int(self.get_prop('soft_deadline_seconds'))
		except:
			self.soft_deadline = 5 # 5 seconds

		return

	def fetch_pending(self):
		return Sliver.objects.filter(ip=None)

	def call(self):
		return True

	def __call__(self):
		return self.call()
