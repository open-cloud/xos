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
import traceback


from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
from django.db import connection
from django.db import reset_queries
#from openstack.manager import OpenStackManager
from openstack.driver import OpenStackDriver
from xos.logger import Logger, logging, logger
#from timeout import timeout
from xos.config import Config, XOS_DIR
from synchronizers.base.steps import *
from syncstep import SyncStep
from toposort import toposort
from synchronizers.base.error_mapper import *
from synchronizers.openstack.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.steps.sync_object import SyncObject
from django.utils import timezone
from diag import update_diag

# Load app models

try:
    app_module_names = Config().observer_applist.split(',')
except AttributeError:
    app_module_names = []

if (type(app_module_names)!=list):
    app_module_names=[app_module_names]

app_modules = []

for m in app_module_names:
    model_path = m+'.models'
    module = __import__(model_path,fromlist=[m])
    app_modules.append(module)


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
				ig[v0]=[k]
	return ig

class XOSObserver:
	sync_steps = []


	def __init__(self):
		# The Condition object that gets signalled by Feefie events
		self.step_lookup = {}
		self.load_sync_step_modules()
		self.load_sync_steps()
		self.event_cond = threading.Condition()

		self.driver_kind = getattr(Config(), "observer_driver", "openstack")
		self.observer_name = getattr(Config(), "observer_name", "")
		if self.driver_kind=="openstack":
			self.driver = OpenStackDriver()
		else:
			self.driver = NoOpDriver()

        def consolePrint(self, what):
            if getattr(Config(), "observer_console_print", True):
                print what

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
				step_dir = XOS_DIR + "/synchronizers/openstack/steps"

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
                phantom_steps = []
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
							if (not provides_dict.has_key(m)):
                                                                try:
								    step_graph[source]+=['#%s'%m]
                                                                except:
                                                                    step_graph[source]=['#%s'%m]

                                                                phantom_steps+=['#%s'%m]
							pass
					
			except KeyError:
				pass
				# no dependencies, pass
		

		self.dependency_graph = step_graph
		self.deletion_dependency_graph = invert_graph(step_graph)

		pp = pprint.PrettyPrinter(indent=4)
                logger.info(pp.pformat(step_graph))
		self.ordered_steps = toposort(self.dependency_graph, phantom_steps+map(lambda s:s.__name__,self.sync_steps))
		self.ordered_steps = [i for i in self.ordered_steps if i!='SyncObject']

		logger.info("Order of steps=%s" % self.ordered_steps)

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
			jrun_times = open('/tmp/%sobserver_run_times'%self.observer_name).read()
			self.last_run_times = json.loads(jrun_times)
		except:
			self.last_run_times={}
			for e in self.ordered_steps:
				self.last_run_times[e]=0
		try:
			jrun_times = open('/tmp/%sobserver_deletion_run_times'%self.observer_name).read()
			self.last_deletion_run_times = json.loads(jrun_times)
		except:
			self.last_deletion_run_times={}
			for e in self.ordered_steps:
				self.last_deletion_run_times[e]=0

        def lookup_step_class(self,s):
		if ('#' in s):
			return SyncObject
		else:
			step = self.step_lookup[s]
		return step

	def lookup_step(self,s):
		if ('#' in s):
			objname = s[1:]
			so = SyncObject()
			
                        try:
			    obj = globals()[objname]
                        except:
                            for m in app_modules:
                                if (hasattr(m,objname)):
                                    obj = getattr(m,objname)

			so.provides=[obj]
			so.observes=[obj]
			step = so
		else:
			step_class = self.step_lookup[s]
                        step = step_class(driver=self.driver,error_map=self.error_mapper)
		return step
			
	def save_run_times(self):
		run_times = json.dumps(self.last_run_times)
		open('/tmp/%sobserver_run_times'%self.observer_name,'w').write(run_times)

		deletion_run_times = json.dumps(self.last_deletion_run_times)
		open('/tmp/%sobserver_deletion_run_times'%self.observer_name,'w').write(deletion_run_times)

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
		step = self.lookup_step_class(S)
		start_time=time.time()

                logger.info("Starting to work on step %s, deletion=%s" % (step.__name__, str(deletion)))
		
		dependency_graph = self.dependency_graph if not deletion else self.deletion_dependency_graph
                step_conditions = self.step_conditions# if not deletion else self.deletion_step_conditions
                step_status = self.step_status# if not deletion else self.deletion_step_status

		# Wait for step dependencies to be met
		try:
			deps = dependency_graph[S]
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

				cond = step_conditions[d]
				cond.acquire()
				if (step_status[d] is STEP_STATUS_WORKING):
                                        logger.info("  step %s wait on dep %s" % (step.__name__, d))
					cond.wait()
                                        logger.info("  step %s wait on dep %s cond returned" % (step.__name__, d))
				elif step_status[d] == STEP_STATUS_OK:
					go = True
				else:
                                        logger.info("  step %s has failed dep %s" % (step.__name__, d))
					go = False
                        		failed_dep = d
				cond.release()
				if (not go):
					break
		else:
			go = True

		if (not go):
                        logger.info("Step %s skipped" % step.__name__)
                        self.consolePrint(bcolors.FAIL + "Step %r skipped on %r" % (step,failed_dep) + bcolors.ENDC)
                        # SMBAKER: sync_step was not defined here, so I changed
                        #    this from 'sync_step' to 'step'. Verify.
			self.failed_steps.append(step)
			my_status = STEP_STATUS_KO
		else:
			sync_step = self.lookup_step(S)
			sync_step. __name__= step.__name__
			sync_step.dependencies = []
			try:
				mlist = sync_step.provides

                                try:
                                    for m in mlist:
                                            lst =  self.model_dependency_graph[m.__name__]
                                            nlst = map(lambda(a,b):b,lst)
                                            sync_step.dependencies.extend(nlst)
                                except Exception,e:
                                    raise e

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

					logger.info('Executing step %s, deletion=%s' % (sync_step.__name__, deletion))

					self.consolePrint(bcolors.OKBLUE + "Executing step %s" % sync_step.__name__ + bcolors.ENDC)
					failed_objects = sync_step(failed=list(self.failed_step_objects), deletion=deletion)

					self.check_duration(sync_step, duration)

					if failed_objects:
						self.failed_step_objects.update(failed_objects)

                                        logger.info("Step %r succeeded, deletion=%s" % (sync_step.__name__, deletion))
                                        self.consolePrint(bcolors.OKGREEN + "Step %r succeeded" % sync_step.__name__ + bcolors.ENDC)
					my_status = STEP_STATUS_OK
					self.update_run_time(sync_step,deletion)
				except Exception,e:
                        		self.consolePrint(bcolors.FAIL + "Model step %r failed" % (sync_step.__name__) + bcolors.ENDC)
					logger.error('Model step %r failed. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!' % (sync_step.__name__, e))
					logger.log_exc("Exception in sync step")
					self.failed_steps.append(S)
					my_status = STEP_STATUS_KO
			else:
                                logger.info("Step %r succeeded due to non-run" % step)
				my_status = STEP_STATUS_OK

		try:
			my_cond = step_conditions[S]
			my_cond.acquire()
			step_status[S]=my_status
			my_cond.notify_all()
			my_cond.release()
		except KeyError,e:
			logger.info('Step %r is a leaf' % step)
			pass
            finally:
                try:
                    reset_queries()
                except:
                    # this shouldn't happen, but in case it does, catch it...
                    logger.log_exc("exception in reset_queries")

                connection.close()

	def run(self):
		if not self.driver.enabled:
			return

		if (self.driver_kind=="openstack") and (not self.driver.has_openstack):
			return

		while True:
                    logger.info('Waiting for event')
                    self.wait_for_event(timeout=5)
                    logger.info('Observer woke up')

                    self.run_once()

        def check_db_connection_okay(self):
            # django implodes if the database connection is closed by docker-compose
            try:
                diag = Diag.objects.filter(name="foo").first()
            except Exception, e:
                from django import db
                if "connection already closed" in traceback.format_exc():
                   logger.error("XXX connection already closed")
                   try:
#                       if db.connection:
#                           db.connection.close()
                       db.close_connection()
                   except:
                        logger.log_exc("XXX we failed to fix the failure")
                else:
                   logger.log_exc("XXX some other error")

        def run_once(self):
                try:
                        self.check_db_connection_okay()

                        loop_start = time.time()
                        error_map_file = getattr(Config(), "error_map_path", XOS_DIR + "/error_map.txt")
                        self.error_mapper = ErrorMapper(error_map_file)

                        # Two passes. One for sync, the other for deletion.
                        for deletion in [False,True]:
                                # Set of individual objects within steps that failed
                                self.failed_step_objects = set()

                                # Set up conditions and step status
                                # This is needed for steps to run in parallel
                                # while obeying dependencies.

                                providers = set()
                                dependency_graph = self.dependency_graph if not deletion else self.deletion_dependency_graph

                                for v in dependency_graph.values():
                                        if (v):
                                                providers.update(v)

                                self.step_conditions = {}
                                self.step_status = {}

                                for p in list(providers):
                                        self.step_conditions[p] = threading.Condition()

                                        self.step_status[p] = STEP_STATUS_WORKING

                                self.failed_steps = []

                                threads = []
                                logger.info('Deletion=%r...'%deletion)
                                schedule = self.ordered_steps if not deletion else reversed(self.ordered_steps)

                                for S in schedule:
                                        thread = threading.Thread(target=self.sync, name='synchronizer', args=(S, deletion))

                                        logger.info('Deletion=%r...'%deletion)
                                        threads.append(thread)

                                # Start threads
                                for t in threads:
                                        t.start()

                                # another spot to clean up debug state
                                try:
                                    reset_queries()
                                except:
                                    # this shouldn't happen, but in case it does, catch it...
                                    logger.log_exc("exception in reset_queries")

                                # Wait for all threads to finish before continuing with the run loop
                                for t in threads:
                                        t.join()

                        self.save_run_times()

                        loop_end = time.time()

                        update_diag(loop_end=loop_end, loop_start=loop_start, backend_status="1 - Bottom Of Loop")

                except Exception, e:
                        logger.error('Core error. This seems like a misconfiguration or bug: %r. This error will not be relayed to the user!' % e)
                        logger.log_exc("Exception in observer run loop")
                        traceback.print_exc()
                        update_diag(backend_status="2 - Exception in Event Loop")
