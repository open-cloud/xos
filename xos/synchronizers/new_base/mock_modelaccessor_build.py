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

import os, cPickle, subprocess

"""
    Support for autogenerating mock_modelaccessor.

    Each unit test might have its own requirements for the set of xprotos that make
    up its model testing framework. These should always include the core, and   
    optionally include one or more services. 
"""

def build_mock_modelaccessor(xos_dir, services_dir, service_xprotos, target="mock_classes.xtarget"):
    dest_fn = os.path.join(xos_dir, "synchronizers", "new_base", "mock_modelaccessor.py")

    args = ["xosgenx", "--target", target]
    args.append(os.path.join(xos_dir, "core/models/core.xproto"))
    for xproto in service_xprotos:
        args.append(os.path.join(services_dir, xproto))

    # Check to see if we've already run xosgenx. If so, don't run it again.
    context_fn = dest_fn + ".context"
    this_context = (xos_dir, services_dir, service_xprotos, target)
    need_xosgenx = True
    if os.path.exists(context_fn):
        try:
            context = cPickle.loads(open(context_fn).read())
            if (context == this_context):
                return
        except (cPickle.UnpicklingError, EOFError):
            # Something went wrong with the file read or depickling
            pass

    if os.path.exists(context_fn):
        os.remove(context_fn)

    if os.path.exists(dest_fn):
        os.remove(dest_fn)

    p = subprocess.Popen(" ".join(args) + " > " + dest_fn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdoutdata, stderrdata) = p.communicate();
    if (p.returncode!=0) or (not os.path.exists(dest_fn)):
        raise Exception("Failed to create mock model accessor, returncode=%d, stdout=%s" % (p.returncode, stdoutdata))

    # Save the context of this invocation of xosgenx
    open(context_fn, "w").write(cPickle.dumps(this_context))
