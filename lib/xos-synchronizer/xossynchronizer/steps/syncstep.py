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


from __future__ import absolute_import

from functools import reduce

from xosconfig import Config


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def elim_dups(backend_str):
    strs = backend_str.split(" // ")
    strs2 = f7(strs)
    return " // ".join(strs2)


def deepgetattr(obj, attr):
    return reduce(getattr, attr.split("."), obj)


def obj_class_name(obj):
    return getattr(obj, "model_name", obj.__class__.__name__)


class InnocuousException(Exception):
    pass


class DeferredException(Exception):
    pass


class FailedDependency(Exception):
    pass


class SyncStep(object):
    """ An XOS Sync step.

    Attributes:
        psmodel        Model name the step synchronizes
        dependencies    list of names of models that must be synchronized first if the current model depends on them
    """

    slow = False

    def get_prop(self, prop):
        # NOTE config_dir is never define, is this used?
        sync_config_dir = Config.get("config_dir")
        prop_config_path = "/".join(sync_config_dir, self.name, prop)
        return open(prop_config_path).read().rstrip()

    def __init__(self, **args):
        """Initialize a sync step
           Keyword arguments:
               model_accessor: class used to access models
               driver: used by openstack synchronizer (DEPRECATED)
               error_map: used by openstack synchronizer (DEPRECATED)
        """
        self.model_accessor = args.get("model_accessor")
        self.driver = args.get("driver")
        self.error_map = args.get("error_map")

        assert self.model_accessor is not None

        try:
            self.soft_deadline = int(self.get_prop("soft_deadline_seconds"))
        except BaseException:
            self.soft_deadline = 5  # 5 seconds

        if "log" in args:
            self.log = args.get("log")

        return

    @property
    def observes_classes(self):
        """ Return a list of classes that this syncstep observes. The "observes" class member can be either a list of
            items or a single item. Those items may be either classes or names of classes. This function always returns
            a list of classes.
        """
        if not self.observes:
            return []
        if isinstance(self.observes, list):
            observes = self.observes
        else:
            observes = [self.observes]
        result = []
        for class_or_name in observes:
            if isinstance(class_or_name, str):
                result.append(self.model_accessor.get_model_class(class_or_name))
            else:
                result.append(class_or_name)
        return result

    def fetch_pending(self, deletion=False):
        # This is the most common implementation of fetch_pending
        # Steps should override it if they have their own logic
        # for figuring out what objects are outstanding.

        return self.model_accessor.fetch_pending(self.observes_classes, deletion)

    def sync_record(self, o):
        self.log.debug("In abstract sync record", **o.tologdict())
        # This method should be overridden by the service

    def delete_record(self, o):
        self.log.debug("In abstract delete record", **o.tologdict())
        # This method should be overridden by the service
