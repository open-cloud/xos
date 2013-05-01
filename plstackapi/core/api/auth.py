from plstackapi.openstack.client import OpenStackClient

def auth_check(username, password, tenant):
    client = OpenStackClient(username=username,
                             password=password,
                             tenant=tenant)
    client.authenticate()
    return client
