from xos.config import Config
from xos.logger import Logger, logging, logger

class ErrorMapper:
	def __init__(self, error_map_file):
		self.error_map = {}
		try:
			error_map_lines = open(error_map_file).read().splitlines()
			for l in error_map_lines:
				if (not l.startswith('#')):
					splits = l.split('->')
					k,v = map(lambda i:i.rstrip(),splits)
					self.error_map[k]=v
		except:
			logging.info('Could not read error map')


	def map(self, error):
		return self.error_map[error]






