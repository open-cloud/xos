import os
import sys

# XXX - deal with what I think is a bug in OpenStack's tosca engine
os.system("cat definitions/TOSCA_definition_1_0.yaml definitions/xos.yaml >  /opt/tosca/translator/toscalib/elements/TOSCA_definition_1_0.yaml")

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

    xt = XOSTosca(file(template_name).read(), parent_dir=currentdir)
    xt.destroy(u)

if __name__=="__main__":
    main()
