# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO:
# Add unit tests:
# - 2 sets of Instance, ControllerSlice, ControllerNetworks - delete and create case

from __future__ import absolute_import

import json
import threading
import time
from collections import defaultdict

from multistructlog import create_logger
from networkx import (
    DiGraph,
    NetworkXNoPath,
    NodeNotFound,
    all_shortest_paths,
    weakly_connected_component_subgraphs,
)
from networkx.algorithms.dag import topological_sort
from xosconfig import Config
from xossynchronizer.steps.syncstep import (
    DeferredException,
    InnocuousException,
    SyncStep,
)
from six.moves import range

log = create_logger(Config().get("logging"))


class StepNotReady(Exception):
    pass


class ExternalDependencyFailed(Exception):
    pass


# FIXME: Move drivers into a context shared across sync steps.


class NoOpDriver:
    def __init__(self):
        self.enabled = True
        self.dependency_graph = None


# Everyone gets NoOpDriver by default. To use a different driver, call
# set_driver() below.
DRIVER = NoOpDriver()

DIRECT_EDGE = 1
PROXY_EDGE = 2


def set_driver(x):
    global DRIVER
    DRIVER = x


class XOSObserver(object):
    sync_steps = []

    def __init__(self, sync_steps, model_accessor, log=log):
        self.log = log
        self.model_accessor = model_accessor

        self.step_lookup = {}
        self.sync_steps = sync_steps
        self.load_sync_steps()

        self.load_dependency_graph()

        self.event_cond = threading.Condition()

        self.driver = DRIVER
        self.observer_name = Config.get("name")

    def wait_for_event(self, timeout):
        self.event_cond.acquire()
        self.event_cond.wait(timeout)
        self.event_cond.release()

    def wake_up(self):
        self.log.debug("Wake up routine called")
        self.event_cond.acquire()
        self.event_cond.notify()
        self.event_cond.release()

    def load_dependency_graph(self):

        try:
            if Config.get("dependency_graph"):
                self.log.debug(
                    "Loading model dependency graph",
                    path=Config.get("dependency_graph"),
                )
                dep_graph_str = open(Config.get("dependency_graph")).read()
            else:
                self.log.debug("Using default model dependency graph", graph={})
                dep_graph_str = "{}"

            # joint_dependencies is of the form { Model1 -> [(Model2, src_port, dst_port), ...] }
            # src_port is the field that accesses Model2 from Model1
            # dst_port is the field that accesses Model1 from Model2
            static_dependencies = json.loads(dep_graph_str)
            dynamic_dependencies = (
                []
            )  # Dropped Service and ServiceInstance dynamic dependencies

            joint_dependencies = dict(
                list(static_dependencies.items()) + dynamic_dependencies
            )

            model_dependency_graph = DiGraph()
            for src_model, deps in joint_dependencies.items():
                for dep in deps:
                    dst_model, src_accessor, dst_accessor = dep
                    if src_model != dst_model:
                        edge_label = {
                            "src_accessor": src_accessor,
                            "dst_accessor": dst_accessor,
                        }
                        model_dependency_graph.add_edge(
                            src_model, dst_model, **edge_label
                        )

            model_dependency_graph_rev = model_dependency_graph.reverse(copy=True)
            self.model_dependency_graph = {
                # deletion
                True: model_dependency_graph_rev,
                False: model_dependency_graph,
            }
            self.log.debug("Loaded dependencies", edges=model_dependency_graph.edges())
        except Exception as e:
            self.log.exception("Error loading dependency graph", e=e)
            raise e

    def load_sync_steps(self):
        model_to_step = defaultdict(list)
        external_dependencies = []

        for s in self.sync_steps:
            if not isinstance(s.observes, list):
                observes = [s.observes]
            else:
                observes = s.observes
            for m in observes:
                if isinstance(m, str):
                    # observes is a string that names the model
                    model_to_step[m].append(s.__name__)
                else:
                    # observes is the model class
                    model_to_step[m.__name__].append(s.__name__)

            try:
                external_dependencies.extend(s.external_dependencies)
            except AttributeError:
                pass

            self.step_lookup[s.__name__] = s

        self.model_to_step = model_to_step
        self.external_dependencies = list(set(external_dependencies))
        self.log.info(
            "Loaded external dependencies", external_dependencies=external_dependencies
        )
        self.log.info("Loaded model_map", **model_to_step)

    def reset_model_accessor(self, o=None):
        try:
            self.model_accessor.reset_queries()
        except BaseException:
            # this shouldn't happen, but in case it does, catch it...
            if o:
                logdict = o.tologdict()
            else:
                logdict = {}

            self.log.error("exception in reset_queries", **logdict)

    def delete_record(self, o, dr_log=None):

        if dr_log is None:
            dr_log = self.log

        if getattr(o, "backend_need_reap", False):
            # the object has already been deleted and marked for reaping
            self.model_accessor.journal_object(o, "syncstep.call.already_marked_reap")
        else:
            step = getattr(o, "synchronizer_step", None)
            if not step:
                raise ExternalDependencyFailed

            self.model_accessor.journal_object(o, "syncstep.call.delete_record")

            dr_log.debug("Deleting object", **o.tologdict())

            step.log = dr_log.new(step=step)
            step.delete_record(o)
            step.log = dr_log

            dr_log.debug("Deleted object", **o.tologdict())

            self.model_accessor.journal_object(o, "syncstep.call.delete_set_reap")
            o.backend_need_reap = True
            o.save(update_fields=["backend_need_reap"])

    def sync_record(self, o, sr_log=None):
        try:
            step = o.synchronizer_step
        except AttributeError:
            step = None

        if step is None:
            raise ExternalDependencyFailed

        if sr_log is None:
            sr_log = self.log

        # Mark this as an object that will require delete. Do
        # this now rather than after the syncstep,
        if not (o.backend_need_delete):
            o.backend_need_delete = True
            o.save(update_fields=["backend_need_delete"])

        self.model_accessor.journal_object(o, "syncstep.call.sync_record")

        sr_log.debug("Syncing object", **o.tologdict())

        step.log = sr_log.new(step=step)
        step.sync_record(o)
        step.log = sr_log

        sr_log.debug("Synced object", **o.tologdict())

        o.enacted = max(o.updated, o.changed_by_policy)
        scratchpad = {"next_run": 0, "exponent": 0, "last_success": time.time()}
        o.backend_register = json.dumps(scratchpad)
        o.backend_status = "OK"
        o.backend_code = 1
        self.model_accessor.journal_object(o, "syncstep.call.save_update")
        o.save(
            update_fields=[
                "enacted",
                "backend_status",
                "backend_register",
                "backend_code",
            ]
        )

        if hasattr(step, "after_sync_save"):
            step.log = sr_log.new(step=step)
            step.after_sync_save(o)
            step.log = sr_log

        sr_log.info("Saved sync object", o=o)

    """ This function needs a cleanup. FIXME: Rethink backend_status, backend_register """

    def handle_sync_exception(self, o, e):
        self.log.exception("sync step failed!", e=e, **o.tologdict())

        if hasattr(e, "message"):
            status = str(e.message)
        else:
            status = str(e)

        if isinstance(e, InnocuousException):
            code = 1
        elif isinstance(e, DeferredException):
            # NOTE if the synchronization is Deferred it means that synchronization is still in progress
            code = 0
        else:
            code = 2

        self.set_object_error(o, status, code)

        dependency_error = "Failed due to error in model %s id %d: %s" % (
            o.leaf_model_name,
            o.id,
            status,
        )
        return dependency_error, code

    def set_object_error(self, o, status, code):
        if o.backend_status:
            error_list = o.backend_status.split(" // ")
        else:
            error_list = []

        if status not in error_list:
            error_list.append(status)

        # Keep last two errors
        error_list = error_list[-2:]

        o.backend_code = code
        o.backend_status = " // ".join(error_list)

        try:
            scratchpad = json.loads(o.backend_register)
            scratchpad["exponent"]
        except BaseException:
            scratchpad = {
                "next_run": 0,
                "exponent": 0,
                "last_success": time.time(),
                "failures": 0,
            }

        # Second failure
        if scratchpad["exponent"]:
            if code == 1:
                delay = scratchpad["exponent"] * 60  # 1 minute
            else:
                delay = scratchpad["exponent"] * 600  # 10 minutes

            # cap delays at 8 hours
            if delay > 8 * 60 * 60:
                delay = 8 * 60 * 60
            scratchpad["next_run"] = time.time() + delay

        scratchpad["exponent"] += 1

        try:
            scratchpad["failures"] += 1
        except KeyError:
            scratchpad["failures"] = 1

        scratchpad["last_failure"] = time.time()

        o.backend_register = json.dumps(scratchpad)

        # TOFIX:
        # DatabaseError: value too long for type character varying(140)
        if self.model_accessor.obj_exists(o):
            try:
                o.backend_status = o.backend_status[:1024]
                o.save(
                    update_fields=["backend_status", "backend_register"],
                    always_update_timestamp=True,
                )
            except BaseException as e:
                self.log.exception("Could not update backend status field!", e=e)
                pass

    def sync_cohort(self, cohort, deletion):
        threading.current_thread().is_sync_thread = True

        sc_log = self.log.new(thread_id=threading.current_thread().ident)

        try:
            sc_log.debug("Starting to work on cohort", cohort=cohort, deletion=deletion)

            cohort_emptied = False
            dependency_error = None
            dependency_error_code = None

            itty = iter(cohort)

            while not cohort_emptied:
                try:
                    self.reset_model_accessor()
                    o = next(itty)

                    if dependency_error:
                        self.set_object_error(
                            o, dependency_error, dependency_error_code
                        )
                        continue

                    try:
                        if deletion:
                            self.delete_record(o, sc_log)
                        else:
                            self.sync_record(o, sc_log)
                    except ExternalDependencyFailed:
                        dependency_error = (
                            "External dependency on object %s id %d not met"
                            % (o.leaf_model_name, o.id)
                        )
                        dependency_error_code = 1
                    except (DeferredException, InnocuousException, Exception) as e:
                        dependency_error, dependency_error_code = self.handle_sync_exception(
                            o, e
                        )

                except StopIteration:
                    sc_log.debug("Cohort completed", cohort=cohort, deletion=deletion)
                    cohort_emptied = True
        finally:
            self.reset_model_accessor()
            self.model_accessor.connection_close()

    def run(self):
        # Cleanup: Move self.driver into a synchronizer context
        # made available to every sync step.
        if not self.driver.enabled:
            self.log.warning("Driver is not enabled. Not running sync steps.")
            return

        while True:
            self.log.debug("Waiting for event or timeout")
            self.wait_for_event(timeout=5)
            self.log.debug("Synchronizer awake")

            self.run_once()

    def fetch_pending(self, deletion=False):
        pending_objects = []
        pending_steps = []
        step_list = list(self.step_lookup.values())

        for e in self.external_dependencies:
            s = SyncStep
            if isinstance(e, str):
                # external dependency is a string that names a model class
                s.observes = self.model_accessor.get_model_class(e)
            else:
                # external dependency is a model class
                s.observes = e
            step_list.append(s)

        for step_class in step_list:
            step = step_class(driver=self.driver, model_accessor=self.model_accessor)
            step.log = self.log.new(step=step)

            if not hasattr(step, "call"):
                pending = step.fetch_pending(deletion)
                for obj in pending:
                    step = step_class(
                        driver=self.driver, model_accessor=self.model_accessor
                    )
                    step.log = self.log.new(step=step)
                    obj.synchronizer_step = step

                pending_objects.extend(pending)
            else:
                # Support old and broken legacy synchronizers
                # This needs to be dropped soon.
                pending_steps.append(step)

        self.log.debug(
            "Fetched pending data",
            pending_objects=pending_objects,
            legacy_steps=pending_steps,
        )
        return pending_objects, pending_steps

    def linked_objects(self, o):
        if o is None:
            return [], None
        try:
            o_lst = [oa for oa in o.all()]
            edge_type = PROXY_EDGE
        except (AttributeError, TypeError):
            o_lst = [o]
            edge_type = DIRECT_EDGE
        return o_lst, edge_type

    """ Automatically test if a real dependency path exists between two objects. e.g.
        given an Instance, and a ControllerSite, the test amounts to:
            instance.slice.site == controller.site

        Then the two objects are related, and should be put in the same cohort.
        If the models of the two objects are not dependent, then the check trivially
        returns False.
    """

    def same_object(self, o1, o2):
        if not o1 or not o2:
            return False, None

        o1_lst, edge_type = self.linked_objects(o1)

        try:
            found = next(
                obj
                for obj in o1_lst
                if obj.leaf_model_name == o2.leaf_model_name and obj.pk == o2.pk
            )
        except AttributeError as e:
            self.log.exception("Compared objects could not be identified", e=e)
            raise e
        except StopIteration:
            # This is a temporary workaround to establish dependencies between
            # deleted proxy objects. A better solution would be for the ORM to
            # return the set of deleted objects via foreign keys. At that point,
            # the following line would change back to found = False
            # - Sapan

            found = getattr(o2, "deleted", False)

        return found, edge_type

    def concrete_path_exists(self, o1, o2):
        try:
            m1 = o1.leaf_model_name
            m2 = o2.leaf_model_name
        except AttributeError:
            # One of the nodes is not in the dependency graph
            # No dependency
            return False, None

        if m1.endswith("ServiceInstance") and m2.endswith("ServiceInstance"):
            return getattr(o2, "dependent", None) == o1, DIRECT_EDGE

        # FIXME: Dynamic dependency check
        G = self.model_dependency_graph[False]
        paths = all_shortest_paths(G, m1, m2)

        try:
            any(paths)
            paths = all_shortest_paths(G, m1, m2)
        except (NetworkXNoPath, NodeNotFound):
            # Easy. The two models are unrelated.
            return False, None

        for p in paths:
            src_object = o1
            edge_type = DIRECT_EDGE

            for i in range(len(p) - 1):
                src = p[i]
                dst = p[i + 1]
                edge_label = G[src][dst]
                sa = edge_label["src_accessor"]
                try:
                    dst_accessor = getattr(src_object, sa)
                    dst_objects, link_edge_type = self.linked_objects(dst_accessor)
                    if link_edge_type == PROXY_EDGE:
                        edge_type = link_edge_type

                    """

                    True       			If no linked objects and deletion
                    False      			If no linked objects
                    True       			If multiple linked objects
                    <continue traversal> 	If single linked object

                    """

                    if dst_objects == []:
                        # Workaround for ORM not returning linked deleted
                        # objects
                        if o2.deleted:
                            return True, edge_type
                        else:
                            dst_object = None
                    elif len(dst_objects) > 1:
                        # Multiple linked objects. Assume anything could be among those multiple objects.
                        raise AttributeError
                    else:
                        dst_object = dst_objects[0]
                except AttributeError as e:
                    if sa != "fake_accessor":
                        self.log.debug(
                            "Could not check object dependencies, making conservative choice %s",
                            e,
                            src_object=src_object,
                            sa=sa,
                            o1=o1,
                            o2=o2,
                        )
                    return True, edge_type

                src_object = dst_object

                if not src_object:
                    break

            verdict, edge_type = self.same_object(src_object, o2)
            if verdict:
                return verdict, edge_type

            # Otherwise try other paths

        return False, None

    """

    This function implements the main scheduling logic
    of the Synchronizer. It divides incoming work (dirty objects)
    into cohorts of dependent objects, and runs each such cohort
    in its own thread.

    Future work:

    * Run event thread in parallel to the scheduling thread, and
      add incoming objects to existing cohorts. Doing so should
      greatly improve synchronizer performance.
    * A single object might need to be added to multiple cohorts.
      In this case, the last cohort handles such an object.
    * This algorithm is horizontal-scale-ready. Multiple synchronizers
      could run off a shared runqueue of cohorts.

    """

    def compute_dependent_cohorts(self, objects, deletion):
        n = len(objects)
        r = list(range(n))

        oG = DiGraph()

        for i in r:
            oG.add_node(i)

        try:
            for i0 in range(n):
                for i1 in range(n):
                    if i0 != i1:
                        if deletion:
                            path_args = (objects[i1], objects[i0])
                        else:
                            path_args = (objects[i0], objects[i1])

                        is_connected, edge_type = self.concrete_path_exists(*path_args)
                        if is_connected:
                            try:
                                edge_type = oG[i1][i0]["type"]
                                if edge_type == PROXY_EDGE:
                                    oG.remove_edge(i1, i0)
                                    oG.add_edge(i0, i1, type=edge_type)
                            except KeyError:
                                oG.add_edge(i0, i1, type=edge_type)
        except KeyError:
            pass

        components = weakly_connected_component_subgraphs(oG)
        cohort_indexes = [reversed(list(topological_sort(g))) for g in components]
        cohorts = [
            [objects[i] for i in cohort_index] for cohort_index in cohort_indexes
        ]

        return cohorts

    def run_once(self):
        self.load_dependency_graph()

        try:
            # Why are we checking the DB connection here?
            self.model_accessor.check_db_connection_okay()

            # Two passes. One for sync, the other for deletion.
            for deletion in (False, True):
                objects_to_process = []

                objects_to_process, steps_to_process = self.fetch_pending(deletion)
                dependent_cohorts = self.compute_dependent_cohorts(
                    objects_to_process, deletion
                )

                threads = []
                self.log.debug("In run once inner loop", deletion=deletion)

                for cohort in dependent_cohorts:
                    thread = threading.Thread(
                        target=self.sync_cohort,
                        name="synchronizer",
                        args=(cohort, deletion),
                    )

                    threads.append(thread)

                # Start threads
                for t in threads:
                    t.start()

                self.reset_model_accessor()

                # Wait for all threads to finish before continuing with the run
                # loop
                for t in threads:
                    t.join()

                # Run legacy synchronizers, which do everything in call()
                for step in steps_to_process:
                    try:
                        step.call(deletion=deletion)
                    except Exception as e:
                        self.log.exception("Legacy step failed", step=step, e=e)

        except Exception as e:
            self.log.exception(
                "Core error. This seems like a misconfiguration or bug. This error will not be relayed to the user!",
                e=e,
            )
            self.log.error("Exception in observer run loop")
