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

import os
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

CWD = OUTPUT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
SWAGGER_DOCS_DIR = os.path.abspath(CWD + '/../swagger/specs')
ORCHESTRATION_DIR = os.path.abspath(CWD + "/../../../")
SERVICE_DIR = os.path.abspath(ORCHESTRATION_DIR + "/xos_services")
PROFILE_DIR = os.path.abspath(ORCHESTRATION_DIR + "/profiles")

XOS_XPROTO = os.path.abspath(CWD + "/../../xos/core/models/core.xproto")

class Args:
    pass

def generate_swagger_docs(xproto):

    # if not os.path.isfile(xproto):
    #     print "ERROR: Couldn't find xproto file for %s at: %s" % (service, xproto)
    #     return

    print "Generating swagger docs for %s" % (xproto)
    args = XOSProcessorArgs()
    args.files = xproto
    args.target = 'swagger.xtarget'
    args.output = SWAGGER_DOCS_DIR
    args.write_to_file = "single"
    args.dest_file = "swagger.yaml"
    args.quiet = False
    try:
        XOSProcessor.process(args)
    except Exception, e:
        print "ERROR: Couldn't generate swagger specs"
        print e

def get_xproto_recursively(root):
    files = []
    items = os.listdir(root)
    # iterate over the content of the folder excluding hidden items
    for item in [i for i in items if i[0] is not "."]:
        item_abs_path = os.path.abspath(root + "/" + item)
        if os.path.isdir(item_abs_path):
            files = files + get_xproto_recursively(item_abs_path)
        elif os.path.isfile(item_abs_path):
            files.append(item_abs_path)

    return [f for f in files if "xproto" in f]


def main():

    protos = [XOS_XPROTO]

    service_protos = get_xproto_recursively(SERVICE_DIR)

    profile_protos = get_xproto_recursively(PROFILE_DIR)

    generate_swagger_docs(protos + service_protos + profile_protos)


if __name__ == '__main__':
    main()
