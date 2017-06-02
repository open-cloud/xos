#!/usr/bin/env python

# This code has to be cleaned up and wrapped in a class

import json
import pdb
from xosconfig import Config

class DependencyWalker:
    def __init__(self, deps_str=None, root=None, depth=-1):
        self.missing_links = {}

        if not deps_str:
            # The 'link' graph is different from the dependenciy graph. 
            # It includes back-links as well. This is a .json file.
            # Dependencies are in the format: k
            dep_graph_file = Config.get('link_graph')
            deps_str = open(dep_graph_file).read()
            pass

        self.dependencies = json.loads(deps_str) # FIXME
        self.compute_inverse_dependencies()
        self.root = root
        self.depth = depth
        self.queue = []
        self.visited = []

        self.set_forwards()


    def set_forwards(self):
        self.active_dependencies = {k: [v[0] for v in vlst] for k, vlst in self.dependencies.items()}


    def set_backwards(self):
        self.active_dependencies = {k: [v[0] for v in vlst] for k, vlst in self.inv_dependencies.items()}


    def compute_inverse_dependencies(self):
        # Compute inverse dependencies 
        # Note that these are not identical as "rlinks". rlinks are reverse links declared explicitly in xproto
        # These are just an inversion of forward dependencies.

        inv_dependencies = {}
        for k, vals in self.dependencies.items():
            for dep in vals:
                inv_dependencies.setdefault(dep[0], set([])).add(k) 

        self.inv_dependencies = inv_dependencies


    def __iter__(self):
        try:
            queue = []
            for v in self.active_dependencies[self.root]:
                if v not in queue:
                    queue.append(v)
            self.queue = zip([self.depth]*len(queue), queue)
        except KeyError, TypeError:
            self.queue = []

        return self


    def next(self):
        if not self.queue:
            raise StopIteration
        else:
            depth, n = self.queue.pop()

            try:
                # Nothing more to see
                if depth==0:
                    raise KeyError

                peers = self.active_dependencies[n]
            except KeyError:
                peers = []

            self.visited.append(n)

            unseen_peers = [i for i in peers if i not in self.visited and i not in [j[1] for j in self.queue]]
            self.queue.extend([(depth-1,v) for v in unseen_peers])

            return n

if __name__=='__main__':
    x = raw_input()
    dg = DependencyWalker('Slice', int(x))
    for i in dg:
        print i
