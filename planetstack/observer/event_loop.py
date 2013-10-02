import time
import traceback
import commands
import threading
import json

from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
#from openstack.manager import OpenStackManager
from openstack.driver import OpenStackDriver
from util.logger import Logger, logging, logger
#from timeout import timeout
from planetstack.config import Config
from observer.steps import *

debug_mode = False

logger = Logger(logfile='observer.log', level=logging.INFO)

class StepNotReady(Exception):
    pass

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
        order.append(n)

    order.extend(set(steps)-set(order))
    return order

class PlanetStackObserver:
    sync_steps = [SyncNetworks,SyncNetworkSlivers,SyncSites,SyncSitePrivileges,SyncSlices,SyncSliceMemberships,SyncSlivers,SyncSliverIps,SyncExternalRoutes,SyncUsers,GarbageCollector]

    def __init__(self):
        # The Condition object that gets signalled by Feefie events
        self.step_lookup = {}
        self.load_sync_steps()
        self.event_cond = threading.Condition()
        self.driver = OpenStackDriver()

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
        dep_path = Config().observer_backend_dependency_graph
        try:
            # This contains dependencies between records, not sync steps
            self.model_dependency_graph = json.loads(open(dep_path).read())
        except Exception,e:
            raise e

        try:
            backend_path = Config().observer_pl_dependency_graph
            # This contains dependencies between backend records
            self.backend_dependency_graph = json.loads(open(backend_path).read())
        except Exception,e:
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

        dependency_graph = step_graph

        self.ordered_steps = toposort(dependency_graph, map(lambda s:s.__name__,self.sync_steps))
        print "Order of steps=",self.ordered_steps
        self.load_run_times()
        

    def check_duration(self, step, duration):
        try:
            if (duration > step.deadline):
                logger.info('Sync step %s missed deadline, took %.2f seconds'%(step.name,duration))
        except AttributeError:
            # S doesn't have a deadline
            pass

    def update_run_time(self, step):
        self.last_run_times[step.__name__]=time.time()

    def check_schedule(self, step):
        time_since_last_run = time.time() - self.last_run_times[step.__name__]
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



    def save_run_times(self):
        run_times = json.dumps(self.last_run_times)
        open('/tmp/observer_run_times','w').write(run_times)

    def check_class_dependency(self, step, failed_steps):
        for failed_step in failed_steps:
            step.dependencies = self.model_dependency_graph.get(step.provides[0].__name__, [])
            if (failed_step in step.dependencies):
                raise StepNotReady

    def run(self):
        if not self.driver.enabled or not self.driver.has_openstack:
            return
        while True:
            try:
                logger.info('Waiting for event')
                tBeforeWait = time.time()
                self.wait_for_event(timeout=30)
                logger.info('Observer woke up')

                # Set of whole steps that failed
                failed_steps = []

                # Set of individual objects within steps that failed
                failed_step_objects = []

                for S in self.ordered_steps:
                    step = self.step_lookup[S]
                    start_time=time.time()
                    
                    sync_step = step(driver=self.driver)
                    sync_step.__name__ = step.__name__
                    #sync_step.dependencies = self.dependencies[sync_step.name]
                    sync_step.debug_mode = debug_mode

                    should_run = False
                    try:
                        # Various checks that decide whether
                        # this step runs or not
                        self.check_class_dependency(sync_step, failed_steps) # dont run Slices if Sites failed
                        self.check_schedule(sync_step) # dont run sync_network_routes if time since last run < 1 hour
                        should_run = True
                    except StepNotReady:
                        logging.info('Step not ready: %s'%sync_step.__name__)
                        failed_steps.append(sync_step)
                    except:
                        failed_steps.append(sync_step)

                    if (should_run):
                        try:
                            duration=time.time() - start_time

                            # ********* This is the actual sync step
                            failed_objects = sync_step(failed=failed_step_objects)


                            self.check_duration(sync_step, duration)
                            if failed_objects:
                                failed_step_objects.extend(failed_objects)
                            self.update_run_time(sync_step)
                        except:
                            raise
                            failed_steps.append(S)
                self.save_run_times()
            except:
                logger.log_exc("Exception in observer run loop")
                traceback.print_exc()
