from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import DeploymentNetwork
 

def add_deployment_network(auth, name):
    auth_check(auth)    
    deployment = DeploymentNetwork(name=name)
    deployment.save()
    return deployment

def delete_deployment_network(auth, filter={}):
    auth_check(auth)   
    deployments = DeploymentNetwork.objects.filter(**filter)
    for deployment in deployments:
        deployment.delete()
    return 1

def get_deployment_networks(auth, filter={}):
    auth_check(auth)   
    deployments = DeploymentNetwork.objects.filter(**filter)
    return deployments             
        

    
