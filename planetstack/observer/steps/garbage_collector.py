import os
import base64
from planetstack.config import Config

class GarbageCollector(SyncStep):
	requested_interval = 86400
	provides=[]

	def call(self):
		pass
        
