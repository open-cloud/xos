
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
import random
import string
import sys
import tempfile

# add the parent parent directory to sys.path
# XXX this is very hackish :(
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
parentparentdir = os.path.dirname(parentdir)
sys.path.append(parentparentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
django.setup()

from tosca.engine import XOSTosca
from core.models import User

class BaseToscaTest(object):
    username = "padmin@vicci.org"
    current_test = ""
    base_yaml = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: tosca test case

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
"""

    def __init__(self):
        self.runtest()

    def make_nodetemplate(self, name, type, props={}, reqs=[], caps={}, artifacts={}):
        yml = "    %s:\n      type: %s\n"  % (name, type)
        if props:
            yml = yml + "      properties:\n"
            for (k,v) in props.items():
                yml = yml + "          %s: %s\n" % (k, v)

        if reqs:
            yml = yml + "      requirements:\n"
            i=0
            for (name,relat) in reqs:
                yml = yml + "        - req%d:\n" % i
                yml = yml + "              node: %s\n" % name
                yml = yml + "              relationship: %s\n" % relat
                i = i + 1

        if caps:
            yml = yml + "      capabilities:\n"
            for (cap,capdict) in caps.items():
               yml = yml + "        %s:\n" % cap
               yml = yml + "          properties:\n"
               for (k,v) in capdict.items():
                   yml = yml + "            %s: %s\n" % (k,v)

        if artifacts:
            yml = yml + "      artifacts:\n"
            for (k,v) in artifacts.items():
                yml = yml + "        %s: %s\n" % (k,v)

        return yml

    def make_compute(self, slice, name, caps={}, props={}, reqs=[], num_cpus="1", disk_size="10 GB", mem_size="4 MB", isolation="vm"):
        reqs = reqs[:]
        props = props.copy()
        caps = caps.copy()

        if isolation=="container":
            type = "tosca.nodes.Compute.Container"
        elif isolation=="container_vm":
            type = "tosca.nodes.Compute.ContainerVM"
        else:
            type = "tosca.nodes.Compute"

        caps.update( {"host": {"num_cpus": num_cpus, "disk_size": disk_size, "mem_size": mem_size},
                      "os": {"architecture": "x86_64", "type": "linux", "distribution": "rhel", "version": "6.5"}} )
        reqs.append( (slice, "tosca.relationships.MemberOfSlice") )

        return self.make_nodetemplate(name, type,
                                      caps= caps,
                                      props = props,
                                      reqs= reqs)

    def make_user_template(self):
        return self.make_nodetemplate("test@user.com", "tosca.nodes.User",
             props = {"firstname": "test", "lastname": "user", "password": "letmein"},
             reqs = [("testsite", "tosca.relationships.MemberOfSite")])

    def make_random_string(self,desired_len):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(desired_len))

    def assert_noobj(self, cls, name):
        objs = cls.objects.filter(name=name)
        assert(not objs)

    def assert_obj(self, cls, name, **kwargs):
        obj = cls.objects.get(name=name)
        assert(obj)
        for (k,v) in kwargs.items():
            if (getattr(obj,k,None) != v):
                print "Object %s property '%s' is '%s' and should be '%s'" % (obj, k, getattr(obj,k,None), v)
                assert(False)
        return obj

    def try_to_delete(self, cls, purge=True, **kwargs):
        for obj in cls.objects.filter(**kwargs):
            obj.delete(purge=purge)

        if purge:
            for obj in cls.deleted_objects.filter(**kwargs):
                obj.delete(purge=True)

    def execute(self, yml):
        u = User.objects.get(email=self.username)

        # save test tosca to a temporary file
        (tf_h, tf_p) = tempfile.mkstemp(dir="/tmp/", prefix=("tosca_test_%s_" % self.current_test))
        # print "Saving TOSCA to file: '%s'" % tf_p
        os.write(tf_h, self.base_yaml+yml)
        os.close(tf_h)

        xt = XOSTosca(self.base_yaml+yml, parent_dir=parentdir, log_to_console=False)
        xt.execute(u)

    def destroy(self, yml):
        u = User.objects.get(email=self.username)

        #print self.base_yaml+yml

        xt = XOSTosca(self.base_yaml+yml, parent_dir=parentdir, log_to_console=False)
        xt.destroy(u)

    def runtest(self):
        for test in self.tests:
            self.current_test = test.replace(' ','_')
            print "running", test
            self.cleanup()
            getattr(self,test)()

        self.cleanup()

    def cleanup(self):
        pass
