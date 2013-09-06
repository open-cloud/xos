#!/usr/bin/python

import time
import traceback
import commands
import threading
import json

from datetime import datetime
from collections import defaultdict

def toposort(g, steps):
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

	order = []
	marked = []
	while sources:
		n = sources.pop()
		try:
			for m in g[n]:
				if m not in marked:
					sources.append(m)
					marked.append(m)
		except KeyError:
			pass
		if (n in steps):
			order.append(n)

	return order

print toposort({'a':'b','b':'c','c':'d','d':'c'},['d','c','b','a'])
