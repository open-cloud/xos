from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.planetstack.api.auth import auth_check
from plstackapi.planetstack.models import User
 

def add_user(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    user = User(**fields)
    nova_fields = {'name': user.email[:self.email.find('@')],
                   'email': user.email, 
                   'password': user.name,
                   'enabled': user.enabled}    
    tenant = driver.create_user(**nova_fields)
    user.user_id=user.id
    user.save()
    return user

def update_user(auth, id, **fields):
    driver = OpenStackDriver(client = auth_check(auth))
    users = User.objects.filter(id=id)
    if not users:
        return

    user = users[0]
    nova_fields = {}
    if 'email' in fields:
        nova_fields['name'] = fields['email'][:self.email.find('@')]
        nova_fields['email'] = fields['email']
    if 'password' in fields:
        nova_fields['password'] = fields['password']
    if 'enabled' in fields:
        nova_fields['enabled'] = fields['enabled']
    driver.update_user(user.user_id, **nova_fields)
    user.update(**fields)
    return user 

def delete_user(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    users = Users.objects.filter(**filter)
    for user in users:
        driver.delete_user(id=user.user_id) 
        user.delete()
    return 1

def get_users(auth, filter={}):
    client = auth_check(auth)
    users = User.objects.filter(**filter)
    return users             
        

    
