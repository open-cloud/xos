#!/usr/bin/python

import os
import imp
from planetstack.config import Config
import inspect
import time
import traceback
import commands
import threading
import json
import pdb
from core.models import *

missing_links={}

try:
	dep_data = open(Config().dependency_graph).read()
except:
	dep_data = open('/opt/planetstack/model-deps').read()

dependencies = json.loads(dep_data)

inv_dependencies = {}
for k, lst in dependencies.items():
	for v in lst:
		try:
			inv_dependencies[v].append(k)
		except KeyError:
			inv_dependencies[v]=[k]
	

def plural(name):
	if (name.endswith('s')):
		return name+'es'
	else:
		return name+'s'


def walk_deps(fn, object):
	model = object.__class__.__name__
	try:	
		deps = dependencies[model]
	except:
		deps = []
	__walk_deps(fn, object, deps)

def walk_inv_deps(fn, object):
	model = object.__class__.__name__
	try:	
		deps = inv_dependencies[model]
	except:
		deps = []
	__walk_deps(fn, object, deps)

def __walk_deps(fn, object, deps):
	model = object.__class__.__name__

	for dep in deps:
		#print "Checking dep %s"%dep
		peer=None
		link = dep.lower()
		try:
			peer = getattr(object, link)
		except AttributeError:
			link = plural(link)
			try:
				peer = getattr(object, link)
			except AttributeError:
				if not missing_links.has_key(model+'.'+link):
					print "Model %s missing link for dependency %s"%(model, link)
					missing_links[model+'.'+link]=True

		if (peer):
			try:
				peer_objects = peer.all()
			except:
				peer_objects = [peer]

			for o in peer_objects:
				fn(o, object)
				# walk_inv_deps(fn, o)

def p(x):
	print x,x.__class__.__name__
	return

def main():
	#pdb.set_trace()
	import django
	django.setup()
	s = Site.objects.filter(login_base='onlab')
	#pdb.set_trace()
	walk_inv_deps(p,s[0])
	
if __name__=='__main__':
	main()
