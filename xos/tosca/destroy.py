
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
import sys

# add the parent directory to sys.path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
django.setup()

from core.models import User
from tosca.engine import XOSTosca

def main():
    if len(sys.argv)<3:
        print "Syntax: destroy.py <username> <yaml-template-name>"
        sys.exit(-1)

    username = sys.argv[1]
    template_name = sys.argv[2]

    u = User.objects.get(email=username)

    if template_name=="-":
        tosca_source = sys.stdin.read()
    else:
        tosca_source = file(template_name).read()

    xt = XOSTosca(tosca_source, parent_dir=currentdir, log_to_console=True)
    xt.destroy(u)

if __name__=="__main__":
    main()
