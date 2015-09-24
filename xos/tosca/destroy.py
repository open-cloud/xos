import os
import sys

# add the parent directory to sys.path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# a bit of a hack for developing -- run m4 to generate xos.yaml from xos.m4
os.system("m4 %s/custom_types/xos.m4 > %s/custom_types/xos.yaml" % (currentdir, currentdir))

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

    xt = XOSTosca(file(template_name).read(), parent_dir=currentdir, log_to_console=True)
    xt.destroy(u)

if __name__=="__main__":
    main()
