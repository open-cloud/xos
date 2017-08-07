
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
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from services.hpc.models import *
from services.volt.models import *
from services.vsg.models import *
import time
django.setup()

def main():
    printed = False

    if len(sys.argv)!=4:
        print >> sys.stderr, "syntax: wait_for_object_creation.py <class> <filter_field_name> <filter_field_value>"
        print >> sys.stderr, "example: wait_for_object_creation.py Image name vsg-1.0"
        sys.exit(-1)

    cls = globals()[sys.argv[1]]

    while True:
        objs = cls.objects.filter(**{sys.argv[2]: sys.argv[3]})
        if objs:
            print "Object", objs[0], "is ready"
            return
        if not printed:
            print "Waiting for %s with field %s=%s to be created" % (sys.argv[1], sys.argv[2], sys.argv[3])
            printed=True
        time.sleep(1)

if __name__ == "__main__":
   main()

