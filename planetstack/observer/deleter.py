import os
import base64
from planetstack.config import Config

class Deleter:
	model=None # Must be overridden

	def call(self,pk):
		# Fetch object from PlanetStack db and delete it
		pass

	def __call__(self):
		return self.call()
