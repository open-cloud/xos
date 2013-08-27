import time
import traceback
import commands
import threading
import json

from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
from openstack.manager import OpenStackManager
from util.logger import Logger, logging, logger
#from timeout import timeout


logger = Logger(logfile='observer.log', level=logging.INFO)

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

class PlanetStackObserver:
	sync_steps = ['SyncNetworks','SyncNetworkSlivers','SyncSites','SyncSitePrivileges','SyncSlices','SyncSliceMemberships','SyncSlivers','SyncSliverIps']

    def __init__(self):
        self.manager = OpenStackManager()
        # The Condition object that gets signalled by Feefie events
		self.load_sync_steps()
        self.event_cond = threading.Condition()
		self.load_enacted()

    def wait_for_event(self, timeout):
        self.event_cond.acquire()
        self.event_cond.wait(timeout)
        self.event_cond.release()
        
    def wake_up(self):
        logger.info('Wake up routine called. Event cond %r'%self.event_cond)
        self.event_cond.acquire()
        self.event_cond.notify()
        self.event_cond.release()

	def load_sync_steps(self):
		dep_path = Config().pl_dependency_path
		try:
			# This contains dependencies between records, not sync steps
			self.model_dependency_graph = json.loads(open(dep_path).read())
		except Exception,e:
			raise e

		backend_path = Config().backend_dependency_path
		try:
			# This contains dependencies between backend records
			self.backend_dependency_graph = json.loads(open(backend_path).read())
		except Exception,e:
			raise e

		provides_dict = {}
		for s in sync_steps:
			for m in s.provides:
				provides_dict[m]=s.__name__
				
		step_graph = {}
		for k,v in model_dependency_graph.iteritems():
			try:
				source = provides_dict[k]
				for m in v:
					try:
						dest = provides_dict[m]
					except KeyError:
						# no deps, pass
					step_graph[source]=dest
					
			except KeyError:
				pass
				# no dependencies, pass
		
		if (backend_dependency_graph):
			backend_dict = {}
			for s in sync_steps:
				for m in s.serves:
					backend_dict[m]=s.__name__
					
			for k,v in backend_dependency_graph.iteritems():
				try:
					source = backend_dict[k]
					for m in v:
						try:
							dest = backend_dict[m]
						except KeyError:
							# no deps, pass
						step_graph[source]=dest
						
				except KeyError:
					pass
					# no dependencies, pass

		dependency_graph = step_graph

		self.ordered_steps = toposort(dependency_graph, steps)
		

    def run(self):
        if not self.manager.enabled or not self.manager.has_openstack:
            return

		
        while True:
            try:
                start_time=time.time()
                
                logger.info('Waiting for event')
                tBeforeWait = time.time()
                self.wait_for_event(timeout=300)

				for S in self.ordered_steps:
					sync_step = S()
					sync_step()

                # Enforce 5 minutes between wakeups
                tSleep = 300 - (time.time() - tBeforeWait)
                if tSleep > 0:
                    logger.info('Sleeping for %d seconds' % tSleep)
                    time.sleep(tSleep)

                logger.info('Observer woke up')
            except:
                logger.log_exc("Exception in observer run loop")
                traceback.print_exc()
