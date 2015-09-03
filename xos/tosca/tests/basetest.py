import os
import sys

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

    def make_nodetemplate(self, name, type, props={}, reqs=[]):
        yml = "    %s:\n      type: %s\n"  % (name, type)
        if props:
            yml = yml + "      properties:\n"
            for (k,v) in props.items():
                yml = yml + "          %s: %s\n" % (k, v)
        return yml

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

    def try_to_delete(self, cls, **kwargs):
        objs = cls.objects.filter(**kwargs)
        for obj in objs:
            obj.delete(purge=True)

    def execute(self, yml):
        u = User.objects.get(email=self.username)

        #print self.base_yaml+yml

        xt = XOSTosca(self.base_yaml+yml, parent_dir=parentdir, log_to_console=True)
        xt.execute(u)

    def runtest(self):
        for test in self.tests:
            print "running", test
            self.cleanup()
            try:
                getattr(self,test)()
            finally:
                self.cleanup()

    def cleanup(self):
        pass
