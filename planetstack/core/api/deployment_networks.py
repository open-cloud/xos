from types import StringTypes
from openstack.client import OpenStackClient
from openstack.driver import OpenStackDriver
from core.api.auth import auth_check
from core.models import DeploymentNetwork

def _get_deployment_networks(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        deployment_networks = DeploymentNetwork.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        deployment_networks = DeploymentNetwork.objects.filter(name=filter)
    elif isinstance(filter, dict):
        deployment_networks = DeploymentNetwork.objects.filter(**filter)
    else:
        deployment_networks = []
    return deployment_networks 

def add_deployment_network(auth, name):
    auth_check(auth)    
    deployment = DeploymentNetwork(name=name)
    deployment.save()
    return deployment

def delete_deployment_network(auth, filter={}):
    auth_check(auth)   
    deployments = _get_deployment_networks(filter)
    for deployment in deployments:
        deployment.delete()
    return 1

def get_deployment_networks(auth, filter={}):
    auth_check(auth)   
    deployments = _get_deployment_networks(filter)
    return deployments             
        

    
