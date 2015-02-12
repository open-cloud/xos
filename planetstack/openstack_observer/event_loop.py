import os
import imp
import inspect
import time
import sys
import traceback
import commands
import threading
import json
import pdb
import pprint


from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
from django.db import connection
#from openstack.manager import OpenStackManager
from openstack.driver import OpenStackDriver
from util.logger import Logger, logging, logger
#from timeout import timeout
from xos.config import Config, XOS_DIR
from observer.steps import *
from syncstep import SyncStep
from toposort import toposort
from observer.error_mapper import *
from openstack_observer.openstacksyncstep import OpenStackSyncStep


debug_mode = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

class PlanetStackObserver:
	#sync_steps = [SyncNetworks,SyncNetworkSlivers,SyncSites,SyncSitePrivilege,SyncSlices,SyncSliceMemberships,SyncSlivers,SyncSliverIps,SyncExternalRoutes,SyncUsers,SyncRoles,SyncNodes,SyncImages,GarbageCollector]
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

					if inspect.isclass(c) and (issubclass(c, SyncStep) or issubclass(c,OpenStackSyncStep)) and hasattr(c,"provides") and (c not in self.sync_steps):
						self.sync_steps.append(c)
		logger.info('loaded sync steps: %s' % ",".join([x.__name__ for x in self.sync_steps]))
		# print 'loaded sync steps: %s' % ",".join([x.__name__ for x in self.sync_steps])

	def load_sync_steps(self):
		dep_path = Config().observer_dependency_graph
		logger.info('Loading model dependency graph from %s' % dep_path)
		try:
			# This contains dependencies between records, not sync steps
			self.model_dependency_graph = json.loads(open(dep_path).read())
			for left,lst in self.model_dependency_graph.items():
                                new_lst = [] 
				for k in lst:
					try:
                                                tup = (k,k.lower())
                                                new_lst.append(tup)
						deps = self.model_dependency_graph[k]
					except:
						self.model_dependency_graph[k] = []

                                self.model_dependency_graph[left] = new_lst
		except Exception,e:
			raise e

		try:
			backend_path = Config().observer_pl_dependency_graph
			logger.info('Loading backend dependency graph from %s' % backend_path)
			# This contains dependencies between backend records
			self.backend_dependency_graph = json.loads(open(backend_path).read())
			for k,v in self.backend_dependency_graph.items():
				try:
					self.model_dependency_graph[k].extend(v)
				except KeyError:
					self.model_dependency_graphp[k] = v

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
		for k,v in self.model_dependency_graph.items():
			try:
				for source in provides_dict[k]:
					if (not v):
						step_graph[source] = []
		
					for m,_ in v:
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
		

		self.dependency_graph = step_graph
		self.deletion_dependency_graph = invert_graph(step_graph)

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(step_graph)
		self.ordered_steps = toposort(self.dependency_graph, map(lambda s:s.__name__,self.sync_steps))
		#self.ordered_steps = ['SyncRoles', 'SyncControllerSites', 'SyncControllerSitePrivileges','SyncImages', 'SyncControllerImages','SyncControllerUsers','SyncControllerUserSitePrivileges','SyncControllerSlices', 'SyncControllerSlicePrivileges', 'SyncControllerUserSlicePrivileges', 'SyncControllerNetworks','SyncSlivers']
		#self.ordered_steps = ['SyncControllerSites','SyncControllerUsers','SyncControllerSlices','SyncControllerNetworks']

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
		        lst = self.model_dependency_graph.get(obj.__name__, [])
			nlst = map(lambda(a,b):b,lst)
			step.dependenices.extend(nlst)
		for failed_step in failed_steps:
			if (failed_step in step.dependencies):
				raise StepNotReady

	def sync(self, S, deletion):
            try:
		step = self.step_lookup[S]
		start_time=time.time()

                logger.info("Starting to work on step %s" % step.__name__)
		
		dependency_graph = self.dependency_graph if not deletion else self.deletion_dependency_graph

		# Wait for step dependencies to be met
		try:
			deps = self.dependency_graph[S]
			has_deps = True
		except KeyError:
			has_deps = False

		go = True

                failed_dep = None
		if (has_deps):
			for d in deps:
                                if d==step.__name__:
                                    logger.info("   step %s self-wait skipped" % step.__name__)
				    go = True
                                    continue

				cond = self.step_conditions[d]
				cond.acquire()
				if (self.step_status[d] is STEP_STATUS_WORKING):
                                        logger.info("  step %s wait on dep %s" % (step.__name__, d))
					cond.wait()
				elif self.step_status[d] == STEP_STATUS_OK:
					go = True
				else:
					go = False
                        		failed_dep = d
				cond.release()
				if (not go):
					break
		else:
			go = True

		if (not go):
                        print bcolors.FAIL + "Step %r skipped on %r" % (step,failed_dep) + bcolors.ENDC
                        # SMBAKER: sync_step was not defined here, so I changed
                        #    this from 'sync_step' to 'step'. Verify.
			self.failed_steps.append(step)
			my_status = STEP_STATUS_KO
		else:
			sync_step = step(driver=self.driver,error_map=self.error_mapper)
			sync_step. __name__= step.__name__
			sync_step.dependencies = []
			try:
				mlist = sync_step.provides

				for m in mlist:
				        lst =  self.model_dependency_graph[m.__name__]
			                nlst = map(lambda(a,b):b,lst)
					sync_step.dependencies.extend(nlst)
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
				logger.info('Step not ready: %s'%sync_step.__name__)
				self.failed_steps.append(sync_step)
				my_status = STEP_STATUS_KO
			except Exception,e:
				logger.error('%r' % e)
				logger.log_exc("sync step failed: %r. Deletion: %r"%(sync_step,deletion))
				self.failed_steps.append(sync_step)
				my_status = STEP_STATUS_KO

			if (should_run):
				try:
					duration=time.time() - start_time

					logger.info('Executing step %s' % sync_step.__name__)

					print bcolors.OKBLUE + "Executing step %s" % sync_step.__name__ + bcolors.ENDC
					failed_objects = sync_step(failed=list(self.failed_step_objects), deletion=deletion)

					self.check_duration(sync_step, duration)

					if failed_objects:
						self.failed_step_objects.update(failed_objects)

                                        logger.info("Step %r succeeded" % step)
                                        print bcolors.OKGREEN + "Step %r succeeded" % step + bcolors.ENDC
					my_status = STEP_STATUS_OK
					self.update_run_time(sync_step,deletion)
				except Exception,e:
                        		print bcolors.FAIL + "Model step %r failed" % (step) + bcolors.ENDC
					logger.error('Model step %r failed. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!' % (step, e))
					logger.log_exc(e)
					self.failed_steps.append(S)
					my_status = STEP_STATUS_KO
			else:
                                logger.info("Step %r succeeded due to non-run" % step)
				my_status = STEP_STATUS_OK

		try:
			my_cond = self.step_conditions[S]
			my_cond.acquire()
			self.step_status[S]=my_status
			my_cond.notify_all()
			my_cond.release()
		except KeyError,e:
			logger.info('Step %r is a leaf' % step)
			pass
            finally:
                connection.close()

	def run(self):
		if not self.driver.enabled:
			return

		if (self.driver_kind=="openstack") and (not self.driver.has_openstack):
			return

		while True:
			try:
				loop_start = time.time()
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
				loop_end = time.time()
				open('/tmp/observer_last_run','w').write(json.dumps({'last_run': loop_end, 'last_duration':loop_end - loop_start}))
			except Exception, e:
				logger.error('Core error. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!' % e)
				logger.log_exc("Exception in observer run loop")
				traceback.print_exc()
