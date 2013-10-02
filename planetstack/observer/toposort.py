#!/usr/bin/python

import time
import traceback
import commands
import threading
import json

from datetime import datetime
from collections import defaultdict

def toposort(g, steps=None):
	if (not steps):
		keys = set(g.keys())
		values = set({})
		for v in g.values():
			values=values | set(v)
		
		steps=list(keys|values)

	reverse = {}

	for k,v in g.items():
		for rk in v:
			try:
				reverse[rk].append(k)
			except:
				reverse[rk]=k

	sources = []
	for k,v in g.items():
		if not reverse.has_key(k):
			sources.append(k)

	for k,v in reverse.iteritems():
		if (not v):
			sources.append(k)

	rev_order = []
	marked = []
	while sources:
		n = sources.pop(0)
		try:
			for m in g[n]:
				if m not in marked:
					sources.append(m)
					marked.append(m)
		except KeyError:
			pass
		if (n in steps):
			rev_order.append(n)
	order = rev_order.reverse()

	return order

graph_file=open('model-deps').read()
g = json.loads(graph_file)
print toposort(g)

#print toposort({'a':'b','b':'c','c':'d','d':'c'},['d','c','b','a'])
