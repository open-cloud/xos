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
from xosgenx.generator import XOSGenerator

CWD = OUTPUT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
SWAGGER_DOCS_DIR = os.path.abspath(CWD + '/../swagger/specs')
ORCHESTRATION_DIR = os.path.abspath(CWD + "/../../../")
SERVICE_DIR = os.path.abspath(ORCHESTRATION_DIR + "/xos_services")

XOS_XPROTO = os.path.abspath(CWD + "/../../xos/core/models/core.xproto")

class Args:
    pass

def generate_swagger_docs(xproto):

    # if not os.path.isfile(xproto):
    #     print "ERROR: Couldn't find xproto file for %s at: %s" % (service, xproto)
    #     return

    print "Generating swagger docs for %s" % (xproto)
    args = Args()
    args.files = xproto
    args.target = 'swagger.xtarget'
    args.output = SWAGGER_DOCS_DIR
    args.write_to_file = "single"
    args.dest_file = "swagger.yaml"
    args.quiet = False
    try:
        XOSGenerator.generate(args)
    except Exception, e:
        print "ERROR: Couldn't generate swagger specs"
        print e

def main():

    # generate_swagger_docs('core', XOS_XPROTO)
    protos = [XOS_XPROTO]

    services = os.listdir(SERVICE_DIR)
    for service in services:
        xos_folder = os.path.abspath(SERVICE_DIR + "/%s/xos" % service);
        if os.path.isdir(xos_folder):
            for file in os.listdir(xos_folder):
                if 'xproto' in file and "monitoring" not in file:
                    proto = os.path.abspath(xos_folder + "/%s" % file)
                    # generate_swagger_docs(service, proto)
                    if os.path.isfile(proto):
                        protos.append(proto)
                    else:
                        print "ERROR: Couldn't find xproto file for %s at: %s" % (service, file)
                else:
                    "WARNING: %s does not have an xproto file" % service
        else:
            print "WARNING: %s does not have an XOS folder" % service
    generate_swagger_docs(protos)


if __name__ == '__main__':
    main()