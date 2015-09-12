import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
django.setup()

# python  ./manage.py sqlflush | python ./manage.py dbshell

os.system("python /opt/xos/manage.py sqlflush | python /opt/xos/manage.py dbshell")

ADMIN_USERNAME = "padmin@vicci.org"
ADMIN_PASSWORD = "letmein"
FLAVORS = ["m1.small", "m1.medium", "m1.large"]
SITE_ROLES = ["admin", "pi", "tech"]
SLICE_ROLES = ["admin", "access"]
DEPLOYMENT_ROLES = ["admin"]

d = Deployment(name="MyDeployment")
d.save()

s = Site(name="MySite", enabled=True, login_base="mysite", is_public=True, abbreviated_name="mysite")
s.save()

sd = SiteDeployment(site=s, deployment=d)
sd.save();

u = User(email = ADMIN_USERNAME, password=ADMIN_PASSWORD, is_admin=True, is_active=True, site=s, firstname="XOS",
         lastname="admin")
u.save()

for flavor_name in FLAVORS:
    f = Flavor(name=flavor_name, flavor=flavor_name)
    f.save()
    f.deployments.add(d)
    f.save()

for site_role_name in SITE_ROLES:
    sr = SiteRole(role=site_role_name)
    sr.save()

for slice_role_name in SLICE_ROLES:
    sr = SliceRole(role=slice_role_name)
    sr.save()

for deployment_role_name in DEPLOYMENT_ROLES:
    dr = DeploymentRole(role=deployment_role_name)
    dr.save()

DashboardView(name="xsh", url="template:xsh", enabled=True).save()
DashboardView(name="Customize", url="template:customize", enabled=True).save()
tv=DashboardView(name="Tenant", url="template:xosTenant", enabled=True)
tv.save()
tv.deployments.add(d)
tv.save()
DashboardView(name="Developer", url="template:xosDeveloper_datatables", enabled=True).save()

ServiceClass(name="Best Effort", description="Best Effort").save()

NetworkTemplate(name="Private", description="A private virtual network", visibility="private", translation="none", topology_kind="bigswitch", controller_kind="none").save()
NetworkTemplate(name="Public shared IPv4", description="Connect a instance to the public network", visibility="private", translation="NAT", shared_network_name="nat-net", topology_kind="bigswitch", controller_kind="none").save()
NetworkTemplate(name="Public dedicated IPv4", description="Connect a instance to the public network", visibility="public", translation="none", shared_network_name="ext-net", topology_kind="bigswitch", controller_kind="none").save()

