from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager

def auth_check(username, password, tenant):
    client = OpenStackClient(username=username,
                             password=password,
                             tenant=tenant)
    client.authenticate()
    return client
