import os
import base64
from syncstep import SyncStep

class OpenStackSyncStep:
	""" PlanetStack Sync step for copying data to OpenStack 
	""" 
	
	def __init__(self, **args):
		super(SyncStep,self).__init__(**args)
		return

	def call(self):
		pending = self.fetch_pending()
		failed = []
		for o in pending:
			if (not self.depends_on(o, failed)):
				try:
					self.sync_record(o)
					o.enacted = datetime.now() # Is this the same timezone? XXX
					o.save(update_fields=['enacted'])
				except:
					failed.append(o)


	def __call__(self):
		return self.call()
