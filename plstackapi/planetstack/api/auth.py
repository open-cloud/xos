from plstackapi.openstack.client import OpenStackClient

def auth_check(auth):
    client = OpenStackClient(username=auth['Username'],
                             password=auth['AuthString'],
                             tenant=auth['LoginBase'])
    client.authenticate()
    return client
