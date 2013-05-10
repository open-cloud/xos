from types import StringTypes
import re
from django.contrib.auth import authenticate
from openstack.manager import OpenStackManager
from core.models import SitePrivilege
from core.api.users import _get_users
from core.api.sites import _get_sites
from core.api.roles import _get_roles


def _get_site_privileges(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        site_privileges = SitePrivilege.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        site_privileges = SitePrivilege.objects.filter(name=filter)
    elif isinstance(filter, dict):
        site_privileges = SitePrivilege.objects.filter(**filter)
    else:
        site_privileges = []
    return site_privileges
 
def add_site_privilege(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))

    users = _get_user(fields.get('user')) 
    sites = _get_slice(fields.get('site')) 
    roles = _get_role(fields.get('role'))
    
    if users: fields['user'] = users[0]     
    if slices: fields['site'] = sites[0] 
    if roles: fields['role'] = roles[0]
 
    auth['tenant'] = sites[0].login_base
    site_privilege = SitePrivilege(**fields)
    site_privilege.os_manager = OpenStackManager(auth=auth, caller = user) 
    site_privilege.save()
    return site_privilege

def update_site_privilege(auth, id, **fields):
    return  

def delete_site_privilege(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    manager = OpenStackManager(auth=auth, caller = user)

    site_privileges = _get_site_privileges(filter)
    for site_privilege in site_privileges:
        auth['tenant'] = user.site.login_base
        site_privilege.os_manager = OpenStackManager(auth=auth, caller = user)
        site_privilege.delete()
    return 1

def get_site_privileges(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    users = _get_users(filter.get('user'))
    sites = _get_slices(filter.get('site'))
    roles = _get_roles(filter.get('role'))

    if users: filter['user'] = users[0]
    if sites: filter['site'] = sites[0]
    if roles: filter['role'] = roles[0]
    
    site_privileges = _get_site_privileges(filter)
    return site_privileges             
        

    
