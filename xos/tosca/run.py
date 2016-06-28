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
        print "Syntax: run.py <username> <yaml-template-name>"
        sys.exit(-1)

    username = sys.argv[1]
    template_name = sys.argv[2]

    if username.lower()=="none":
        u=None
    else:
        u = User.objects.get(email=username)

    if template_name=="-":
        tosca_source = sys.stdin.read()
    else:
        tosca_source = file(template_name).read()

    xt = XOSTosca(tosca_source, parent_dir=currentdir, log_to_console=True)
    xt.execute(u)

if __name__=="__main__":
    main()
