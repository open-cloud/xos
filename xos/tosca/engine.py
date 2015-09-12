import os
import pdb
import sys
import tempfile
import traceback

sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,Instance,User,Flavor,Node,Image
from nodeselect import XOSNodeSelector
from imageselect import XOSImageSelector

import resources

class XOSTosca(object):
    def __init__(self, tosca_yaml, parent_dir=None, log_to_console = False):
        # TOSCA will look for imports using a relative path from where the
        # template file is located, so we have to put the template file
        # in a specific place.
        if not parent_dir:
            parent_dir = os.getcwd()

        tmp_pathname = None
        try:
            (tmp_handle, tmp_pathname) = tempfile.mkstemp(dir=parent_dir)
            os.write(tmp_handle, tosca_yaml)
            os.close(tmp_handle)

            self.template = ToscaTemplate(tmp_pathname)
        except:
            traceback.print_exc()
            raise
        finally:
            if tmp_pathname:
                os.remove(tmp_pathname)

        self.log_to_console = log_to_console
        self.log_msgs = []

        self.compute_dependencies()

        self.deferred_sync = []

        self.ordered_nodetemplates = []
        self.ordered_names = self.topsort_dependencies()
        self.log("ordered_names: %s" % self.ordered_names)
        for name in self.ordered_names:
            if name in self.nodetemplates_by_name:
                self.ordered_nodetemplates.append(self.nodetemplates_by_name[name])

        #pdb.set_trace()

    def log(self, msg):
        if self.log_to_console:
            print msg
        self.log_msgs.append(msg)

    def compute_dependencies(self):
        nodetemplates_by_name = {}
        for nodetemplate in self.template.nodetemplates:
            nodetemplates_by_name[nodetemplate.name] = nodetemplate

        self.nodetemplates_by_name = nodetemplates_by_name

        for nodetemplate in self.template.nodetemplates:
            nodetemplate.dependencies = []
            nodetemplate.dependencies_names = []
            for reqs in nodetemplate.requirements:
                for (k,v) in reqs.items():
                    name = v["node"]
                    if (name in nodetemplates_by_name):
                        nodetemplate.dependencies.append(nodetemplates_by_name[name])
                        nodetemplate.dependencies_names.append(name)

                    # go another level deep, as our requirements can have requirements...
                    for sd_req in v.get("requirements",[]):
                        for (sd_req_k, sd_req_v) in sd_req.items():
                            name = sd_req_v["node"]
                            if (name in nodetemplates_by_name):
                                nodetemplate.dependencies.append(nodetemplates_by_name[name])
                                nodetemplate.dependencies_names.append(name)


    def topsort_dependencies(self):
        # stolen from observer
        g = self.nodetemplates_by_name

	# Get set of all nodes, including those without outgoing edges
	keys = set(g.keys())
	values = set({})
	for v in g.values():
		values=values | set(v.dependencies_names)

	all_nodes=list(keys|values)
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
				for m in g[n].dependencies_names:
					if (m in unmarked):
					    add = False
					    stack.insert(0,m)
			except KeyError:
				pass
			if (add):
				if (n in steps and n not in order):
					order.append(n)
				item = stack.pop(0)
				try:
					unmarked.remove(item)
				except ValueError:
					pass

	noorder = list(set(steps) - set(order))
	return order + noorder

    def execute(self, user):
        for nodetemplate in self.ordered_nodetemplates:
            self.execute_nodetemplate(user, nodetemplate)

        for obj in self.deferred_sync:
            self.log("Saving deferred sync obj %s" % obj)
            obj.no_sync = False
            obj.save()

    def execute_nodetemplate(self, user, nodetemplate):
        if nodetemplate.type in resources.resources:
            cls = resources.resources[nodetemplate.type]
            #print "work on", cls.__name__, nodetemplate.name
            obj = cls(user, nodetemplate, self)
            obj.create_or_update()
            self.deferred_sync = self.deferred_sync + obj.deferred_sync

    def destroy(self, user):
        nodetemplates = self.ordered_nodetemplates
        models = []
        for nodetemplate in nodetemplates:
            if nodetemplate.type in resources.resources:
                cls = resources.resources[nodetemplate.type]
                obj = cls(user, nodetemplate, self)
                for model in obj.get_existing_objs():
                    models.append( (obj, model) )
        models.reverse()
        for (resource,model) in models:
            resource.delete(model)

    def name_to_xos_class(self, user, name):
        nt = self.nodetemplates_by_name.get(name)
        if not nt:
            raise Exception("failed to find nodetemplate %s" % name)

        cls = resources.resources.get(nt.type)
        if not cls:
            raise Exception("nodetemplate %s's type does not resolve to a known resource type" % name)

        return (nt, cls, cls.xos_model)

    def name_to_xos_model(self, user, name):
        (nt, cls, model_class) = self.name_to_xos_class(user, name)
        obj = cls(user, nt, self)
        existing_objs = obj.get_existing_objs()
        if not existing_objs:
            raise Exception("failed to find xos %s %s" % (cls.__name__, name))
        return existing_objs[0]

