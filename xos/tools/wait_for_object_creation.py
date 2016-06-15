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

