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

import os
import subprocess

try:
    # Python 2 has separate pickle and cPickle
    # pylint: disable=W1648
    import cPickle
except ImportError:
    # Python 3 will use cPickle by dfault
    import pickle as cPickle

"""
    Support for autogenerating mock_modelaccessor.

    Each unit test might have its own requirements for the set of xprotos that make
    up its model testing framework. These should always include the core, and
    optionally include one or more services.
"""


def build_mock_modelaccessor(
    dest_dir, xos_dir, services_dir, service_xprotos, target="mock_classes.xtarget"
):
    # TODO: deprecate the dest_dir argument

    # force modelaccessor to be found in /tmp
    dest_dir = "/tmp/mock_modelaccessor"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    dest_fn = os.path.join(dest_dir, "mock_modelaccessor.py")

    args = ["xosgenx", "--target", target]
    args.append(os.path.join(xos_dir, "core/models/core.xproto"))
    for xproto in service_xprotos:
        args.append(os.path.join(services_dir, xproto))

    # Check to see if we've already run xosgenx. If so, don't run it again.
    context_fn = dest_fn + ".context"
    this_context = (xos_dir, services_dir, service_xprotos, target)

    if os.path.exists(context_fn):
        try:
            context = cPickle.loads(open(context_fn, 'rb').read())
            if context == this_context:
                return
        except (cPickle.UnpicklingError, EOFError, ValueError):
            # Something went wrong with the file read or depickling
            pass

    if os.path.exists(context_fn):
        os.remove(context_fn)

    if os.path.exists(dest_fn):
        os.remove(dest_fn)

    p = subprocess.Popen(
        " ".join(args) + " > " + dest_fn,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (stdoutdata, stderrdata) = p.communicate()
    if (p.returncode != 0) or (not os.path.exists(dest_fn)):
        raise Exception(
            "Failed to create mock model accessor, returncode=%d, stdout=%s"
            % (p.returncode, stdoutdata)
        )

    # Save the context of this invocation of xosgenx
    open(context_fn, "wb").write(cPickle.dumps(this_context))


# generate model from xproto
def get_models_fn(services_dir, service_name, xproto_name):
    name = os.path.join(service_name, "xos", xproto_name)
    if os.path.exists(os.path.join(services_dir, name)):
        return name
    else:
        name = os.path.join(service_name, "xos", "synchronizer", "models", xproto_name)
        if os.path.exists(os.path.join(services_dir, name)):
            return name
    raise Exception("Unable to find service=%s xproto=%s" % (service_name, xproto_name))


# END generate model from xproto


def mock_modelaccessor_config(test_dir, services):
    """ Automatically configure the mock modelaccessor.

        We start from the test directory, and then back up until we find the orchestration directory. From there we
        can find the other xproto (core, services) that we need to build the mock modelaccessor.
    """

    orchestration_dir = test_dir
    while not orchestration_dir.endswith("orchestration"):
        # back up a level
        orchestration_dir = os.path.dirname(orchestration_dir)
        if len(orchestration_dir) < 10:
            raise Exception("Failed to autodiscovery repository tree")

    xos_dir = os.path.join(orchestration_dir, "xos", "xos")
    services_dir = os.path.join(orchestration_dir, "xos-services")

    service_xprotos = []
    for (service_name, xproto_name) in services:
        service_xprotos.append(get_models_fn(services_dir, service_name, xproto_name))

    build_mock_modelaccessor(None, xos_dir, services_dir, service_xprotos)
