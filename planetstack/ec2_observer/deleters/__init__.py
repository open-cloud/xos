import os

deleters = {}
_path = os.path.join('.',os.path.dirname(__file__))

_files = os.listdir(_path)
_files = filter(lambda x:x.endswith('deleter.py'),_files)
_files = map(lambda x:x.rstrip('.py'),_files)

"""
for f in _files:
	m = __import__(f)
	deleter = getattr(m,f.title().replace('_',''))
	try:
		deleters[deleter.model].append(deleter)
	except KeyError:
		deleters[deleter.model]=[deleter]
"""
