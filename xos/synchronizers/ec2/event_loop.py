import os
import imp
import inspect
import time
import traceback
import commands
import threading
import json
import pdb

from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
#from openstack.manager import OpenStackManager
from openstack.driver import OpenStackDriver
from xos.logger import Logger, logging, logger
#from timeout import timeout
from xos.config import Config, XOS_DIR
from synchronizers.base.steps import *
from syncstep import SyncStep
from toposort import toposort
from synchronizers.base.error_mapper import *

debug_mode = False

logger = Logger(level=logging.INFO)

class StepNotReady(Exception):
	pass

class NoOpDriver:
	def __init__(self):
		 self.enabled = True
		 self.dependency_graph = None

STEP_STATUS_WORKING=1
STEP_STATUS_OK=2
STEP_STATUS_KO=3

def invert_graph(g):
	ig = {}
	for k,v in g.items():
		for v0 in v:
			try:
				ig[v0].append(k)
			except:
				ig=[k]
	return ig

class XOSObserver:
	#sync_steps = [SyncNetworks,SyncNetworkInstances,SyncSites,SyncSitePrivilege,SyncSlices,SyncSliceMemberships,SyncInstances,SyncInstanceIps,SyncExternalRoutes,SyncUsers,SyncRoles,SyncNodes,SyncImages,GarbageCollector]
	sync_steps = []

	
	def __init__(self):
		# The Condition object that gets signalled by Feefie events
		self.step_lookup = {}
		self.load_sync_step_modules()
		self.load_sync_steps()
		self.event_cond = threading.Condition()

		self.driver_kind = getattr(Config(), "observer_driver", "openstack")
		if self.driver_kind=="openstack":
			self.driver = OpenStackDriver()
		else:
			self.driver = NoOpDriver()

	def wait_for_event(self, timeout):
		self.event_cond.acquire()
		self.event_cond.wait(timeout)
		self.event_cond.release()

	def wake_up(self):
		logger.info('Wake up routine called. Event cond %r'%self.event_cond)
		self.event_cond.acquire()
		self.event_cond.notify()
		self.event_cond.release()

	def load_sync_step_modules(self, step_dir=None):
		if step_dir is None:
			if hasattr(Config(), "observer_steps_dir"):
				step_dir = Config().observer_steps_dir
			else:
				step_dir = XOS_DIR + "/observer/steps"

		for fn in os.listdir(step_dir):
			pathname = os.path.join(step_dir,fn)
			if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
				module = imp.load_source(fn[:-3],pathname)
				for classname in dir(module):
					c = getattr(module, classname, None)

					# make sure 'c' is a descendent of SyncStep and has a
					# provides field (this eliminates the abstract base classes
					# since they don't have a provides)

					if inspect.isclass(c) and issubclass(c, SyncStep) and hasattr(c,"provides") and (c not in self.sync_steps):
						self.sync_steps.append(c)
		logger.info('loaded sync steps: %s' % ",".join([x.__name__ for x in self.sync_steps]))
		# print 'loaded sync steps: %s' % ",".join([x.__name__ for x in self.sync_steps])

	def load_sync_steps(self):
		dep_path = Config().observer_dependency_graph
		logger.info('Loading model dependency graph from %s' % dep_path)
		try:
			# This contains dependencies between records, not sync steps
			self.model_dependency_graph = json.loads(open(dep_path).read())
		except Exception,e:
			raise e

		try:
			backend_path = Config().observer_pl_dependency_graph
			logger.info('Loading backend dependency graph from %s' % backend_path)
			# This contains dependencies between backend records
			self.backend_dependency_graph = json.loads(open(backend_path).read())
		except Exception,e:
			logger.info('Backend dependency graph not loaded')
			# We can work without a backend graph
			self.backend_dependency_graph = {}

		provides_dict = {}
		for s in self.sync_steps:
			self.step_lookup[s.__name__] = s 
			for m in s.provides:
				try:
					provides_dict[m.__name__].append(s.__name__)
				except KeyError:
					provides_dict[m.__name__]=[s.__name__]

		step_graph = {}
		for k,v in self.model_dependency_graph.iteritems():
			try:
				for source in provides_dict[k]:
					for m in v:
						try:
							for dest in provides_dict[m]:
								# no deps, pass
								try:
									if (dest not in step_graph[source]):
										step_graph[source].append(dest)
								except:
									step_graph[source]=[dest]
						except KeyError:
							pass
					
			except KeyError:
				pass
				# no dependencies, pass
		
		#import pdb
		#pdb.set_trace()
		if (self.backend_dependency_graph):
			backend_dict = {}
			for s in self.sync_steps:
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
							pass
						step_graph[source]=dest
						
				except KeyError:
					pass
					# no dependencies, pass

		self.dependency_graph = step_graph
		self.deletion_dependency_graph = invert_graph(step_graph)

		self.ordered_steps = toposort(self.dependency_graph, map(lambda s:s.__name__,self.sync_steps))
		print "Order of steps=",self.ordered_steps
		self.load_run_times()
		

	def check_duration(self, step, duration):
		try:
			if (duration > step.deadline):
				logger.info('Sync step %s missed deadline, took %.2f seconds'%(step.name,duration))
		except AttributeError:
			# S doesn't have a deadline
			pass

	def update_run_time(self, step, deletion):
		if (not deletion):
			self.last_run_times[step.__name__]=time.time()
		else:
			self.last_deletion_run_times[step.__name__]=time.time()


	def check_schedule(self, step, deletion):
		last_run_times = self.last_run_times if not deletion else self.last_deletion_run_times

		time_since_last_run = time.time() - last_run_times.get(step.__name__, 0)
		try:
			if (time_since_last_run < step.requested_interval):
				raise StepNotReady
		except AttributeError:
			logger.info('Step %s does not have requested_interval set'%step.__name__)
			raise StepNotReady
	
	def load_run_times(self):
		try:
			jrun_times = open('/tmp/observer_run_times').read()
			self.last_run_times = json.loads(jrun_times)
		except:
			self.last_run_times={}
			for e in self.ordered_steps:
				self.last_run_times[e]=0
		try:
			jrun_times = open('/tmp/observer_deletion_run_times').read()
			self.last_deletion_run_times = json.loads(jrun_times)
		except:
			self.last_deletion_run_times={}
			for e in self.ordered_steps:
				self.last_deletion_run_times[e]=0


	def save_run_times(self):
		run_times = json.dumps(self.last_run_times)
		open('/tmp/observer_run_times','w').write(run_times)

		deletion_run_times = json.dumps(self.last_deletion_run_times)
		open('/tmp/observer_deletion_run_times','w').write(deletion_run_times)

	def check_class_dependency(self, step, failed_steps):
		step.dependenices = []
		for obj in step.provides:
			step.dependenices.extend(self.model_dependency_graph.get(obj.__name__, []))
		for failed_step in failed_steps:
			if (failed_step in step.dependencies):
				raise StepNotReady

	def sync(self, S, deletion):
		step = self.step_lookup[S]
		start_time=time.time()
		
		dependency_graph = self.dependency_graph if not deletion else self.deletion_dependency_graph

		# Wait for step dependencies to be met
		try:
			deps = self.dependency_graph[S]
			has_deps = True
		except KeyError:
			has_deps = False

		if (has_deps):
			for d in deps:
				cond = self.step_conditions[d]
				cond.acquire()
				if (self.step_status[d] is STEP_STATUS_WORKING):
					cond.wait()
				cond.release()
			go = self.step_status[d] == STEP_STATUS_OK
		else:
			go = True

		if (not go):
			self.failed_steps.append(sync_step)
			my_status = STEP_STATUS_KO
		else:
			sync_step = step(driver=self.driver,error_map=self.error_mapper)
			sync_step.__name__ = step.__name__
			sync_step.dependencies = []
			try:
				mlist = sync_step.provides
				
				for m in mlist:
					sync_step.dependencies.extend(self.model_dependency_graph[m.__name__])
			except KeyError:
				pass
			sync_step.debug_mode = debug_mode

			should_run = False
			try:
				# Various checks that decide whether
				# this step runs or not
				self.check_class_dependency(sync_step, self.failed_steps) # dont run Slices if Sites failed
				self.check_schedule(sync_step, deletion) # dont run sync_network_routes if time since last run < 1 hour
				should_run = True
			except StepNotReady:
				logging.info('Step not ready: %s'%sync_step.__name__)
				self.failed_steps.append(sync_step)
				my_status = STEP_STATUS_KO
			except Exception,e:
				logging.error('%r',e)
				logger.log_exc("sync step failed: %r. Deletion: %r"%(sync_step,deletion))
				self.failed_steps.append(sync_step)
				my_status = STEP_STATUS_KO

			if (should_run):
				try:
					duration=time.time() - start_time

					logger.info('Executing step %s' % sync_step.__name__)

					failed_objects = sync_step(failed=list(self.failed_step_objects), deletion=deletion)

					self.check_duration(sync_step, duration)

					if failed_objects:
						self.failed_step_objects.update(failed_objects)

					my_status = STEP_STATUS_OK
					self.update_run_time(sync_step,deletion)
				except Exception,e:
					logging.error('Model step failed. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!',e)
					logger.log_exc(e)
					self.failed_steps.append(S)
					my_status = STEP_STATUS_KO
			else:
				my_status = STEP_STATUS_OK
		
		try:
			my_cond = self.step_conditions[S]
			my_cond.acquire()
			self.step_status[S]=my_status
			my_cond.notify_all()
			my_cond.release()
		except KeyError,e:
			logging.info('Step %r is a leaf')
			pass

	def run(self):
		if not self.driver.enabled:
			return

		if (self.driver_kind=="openstack") and (not self.driver.has_openstack):
			return

		while True:
			try:
				error_map_file = getattr(Config(), "error_map_path", XOS_DIR + "/error_map.txt")
				self.error_mapper = ErrorMapper(error_map_file)

				# Set of whole steps that failed
				self.failed_steps = []

				# Set of individual objects within steps that failed
				self.failed_step_objects = set()

				# Set up conditions and step status
				# This is needed for steps to run in parallel
				# while obeying dependencies.

				providers = set()
				for v in self.dependency_graph.values():
					if (v):
						providers.update(v)

				self.step_conditions = {}
				self.step_status = {}
				for p in list(providers):
					self.step_conditions[p] = threading.Condition()
					self.step_status[p] = STEP_STATUS_WORKING


				logger.info('Waiting for event')
				tBeforeWait = time.time()
				self.wait_for_event(timeout=30)
				logger.info('Observer woke up')

				# Two passes. One for sync, the other for deletion.
				for deletion in [False,True]:
					threads = []
					logger.info('Deletion=%r...'%deletion)
					schedule = self.ordered_steps if not deletion else reversed(self.ordered_steps)

					for S in schedule:
						thread = threading.Thread(target=self.sync, args=(S, deletion))

						logger.info('Deletion=%r...'%deletion)
						threads.append(thread)

					# Start threads 
					for t in threads:
						t.start()

					# Wait for all threads to finish before continuing with the run loop
					for t in threads:
						t.join()

				self.save_run_times()
			except Exception, e:
				logging.error('Core error. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!',e)
				logger.log_exc("Exception in observer run loop")
				traceback.print_exc()
