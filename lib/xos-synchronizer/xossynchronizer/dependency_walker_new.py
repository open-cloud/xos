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

# TODO: Moved this into the synchronizer, as it appeared to require model
#       access. Verify whether or not that's true and reconcile with
#       generate/dependency_walker.py

from __future__ import absolute_import, print_function

import json

from multistructlog import create_logger
from xosconfig import Config

log = create_logger(Config().get("logging"))

missing_links = {}

if Config.get("dependency_graph"):
    dep_data = open(Config.get("dependency_graph")).read()
else:
    dep_data = "{}"

dependencies = json.loads(dep_data)
dependencies = {k: [item[0] for item in items] for k, items in dependencies.items()}

inv_dependencies = {}
for k, lst in dependencies.items():
    for v in lst:
        try:
            inv_dependencies[v].append(k)
        except KeyError:
            inv_dependencies[v] = [k]


def plural(name):
    if name.endswith("s"):
        return name + "es"
    else:
        return name + "s"


def walk_deps(fn, object):
    model = object.__class__.__name__
    try:
        deps = dependencies[model]
    except BaseException:
        deps = []
    return __walk_deps(fn, object, deps)


def walk_inv_deps(fn, object):
    model = object.__class__.__name__
    try:
        deps = inv_dependencies[model]
    except BaseException:
        deps = []
    return __walk_deps(fn, object, deps)


def __walk_deps(fn, object, deps):
    model = object.__class__.__name__
    ret = []
    for dep in deps:
        # print "Checking dep %s"%dep
        peer = None
        link = dep.lower()
        try:
            peer = getattr(object, link)
        except AttributeError:
            link = plural(link)
            try:
                peer = getattr(object, link)
            except AttributeError:
                if model + "." + link not in missing_links:
                    print("Model %s missing link for dependency %s" % (model, link))
                    log.exception(
                        "WARNING: Model missing link for dependency.",
                        model=model,
                        link=link,
                    )
                    missing_links[model + "." + link] = True

        if peer:
            try:
                peer_objects = peer.all()
            except AttributeError:
                peer_objects = [peer]
            except BaseException:
                peer_objects = []

            for o in peer_objects:
                if hasattr(o, "updated"):
                    fn(o, object)
                    ret.append(o)
                # Uncomment the following line to enable recursion
                # walk_inv_deps(fn, o)
    return ret
