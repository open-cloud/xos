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

from __future__ import print_function

import os
import traceback
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

CWD = OUTPUT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
SWAGGER_DOCS_DIR = os.path.abspath(CWD + '/../swagger/specs')
REPO_DIR = os.path.abspath(CWD + "/../../../")

class Args:
    pass


def generate_swagger_docs(xproto):

    # if not os.path.isfile(xproto):
    #     print "ERROR: Couldn't find xproto file for %s at: %s" % (service, xproto)
    #     return

    print("Generating swagger docs for %s" % (xproto))
    args = XOSProcessorArgs()
    args.files = xproto
    args.target = 'swagger.xtarget'
    args.output = SWAGGER_DOCS_DIR
    args.write_to_file = "single"
    args.dest_file = "swagger.yaml"
    args.quiet = False
    try:
        XOSProcessor.process(args)
    except Exception:
        print("ERROR: Couldn't generate swagger specs")
        traceback.print_exc()


def get_xproto_recursively(root):
    files = []
    items = os.listdir(root)
    # iterate over the content of the folder excluding hidden items
    for item in [i for i in items if i[0] is not "."]:
        if ("venv" in item) or ("virtualenv" in item):
            # avoid recursing through virtual env directories
            continue
        if "xos-genx-tests" in item:
            # don't generate docs for xosgenx's unit tests
            continue
        if "xos-tosca" in item:
            # don't generate docs for xos-tosca's unit tests
            continue
        item_abs_path = os.path.abspath(root + "/" + item)
        if os.path.isdir(item_abs_path):
            files = files + get_xproto_recursively(item_abs_path)
        elif os.path.isfile(item_abs_path) and ".xproto" in item_abs_path:
            files.append(item_abs_path)

    protos = sorted([f for f in files if "xproto" in f])

    # remove the core xproto...
    core_proto = None
    for proto in protos[:]:
        if "core.xproto" in proto:
            protos.remove(proto)
            core_proto = proto

    # ... and put it at the front of the list
    if core_proto:
        protos = [core_proto] + protos

    return protos


if __name__ == '__main__':
    protos = get_xproto_recursively(REPO_DIR)
    generate_swagger_docs(protos)
