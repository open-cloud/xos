#!/usr/bin/python

import time
import traceback
import commands
import threading
import json
import pdb

from datetime import datetime
from collections import defaultdict

# Topological sort
# Notes:
# - Uses a stack instead of recursion
# - Forfeits optimization involving tracking currently visited nodes
def toposort(g, steps=None):
	# Get set of all nodes, including those without outgoing edges
	keys = set(g.keys())
	values = set({})
	for v in g.values():
		values=values | set(v)
	
	all_nodes=list(keys|values)
	if (not steps):
		steps = all_nodes

	# Final order
	order = []

	# DFS stack, not using recursion
	stack = []

	# Unmarked set
	unmarked = all_nodes

	# visiting = [] - skip, don't expect 1000s of nodes, |E|/|V| is small

	while unmarked:
		stack.insert(0,unmarked[0]) # push first unmarked

		while (stack):
			n = stack[0]
			add = True
			try:
				for m in g[n]:
					if (m in unmarked):
						if (m not in stack):
							add = False
							stack.insert(0,m)
						else:
							# Should not happen, if so there's a loop
							print 'Loop at %s'%m
			except KeyError:
				pass
			if (add):
				if (n in steps):
					order.append(n)
				item = stack.pop(0)
				unmarked.remove(item)

	noorder = list(set(steps) - set(order))
	return order + noorder

def main():
	graph_file=open('planetstack.deps').read()
	g = json.loads(graph_file)
	print toposort(g)

if (__name__=='__main__'):
	main()

#print toposort({'a':'b','b':'c','c':'d','d':'c'},['d','c','b','a'])
