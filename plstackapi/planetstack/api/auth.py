from plstackapi.openstack.driver import OpenStackDriver

def auth_check(auth):
    client = OpenStackDriver(username=auth['Username'],
                             password=auth['AuthString'],
                             tenant=auth['LoginBase'])
    client.authenticate()
    return client
