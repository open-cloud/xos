from core.models import *

def handle(site):
    """ 
    ensure ControllerSiteDeployment object exists for each of the site's SiteDeployment objects
    """
    from core.models import SiteDeployments, Controller, ControllerSiteDeployments 
    from collections import defaultdict
    
    # get current controller site deployments	
    ctrl_site_deployments = ControllerSiteDeployments.objects.filter(site_deployment__site = site)
    ctrl_site_deployments_dict = {} 
    for ctrl_site_depl in controller_site_deployments:
        ctrl_site_deployments_dict[ctrl_site_depl.site_deployment] = ctrl_cite_depl

    # get current site deployments
    site_deployments = SiteDeployments.objects.filter(site=site)
 
    # for each site deployment, if there is no controller site deployment create one 
    for site_deployment in site_deployments:
        if site_deployment not in ctrl_site_deployments_dict:
            ctrl_site_deployment = ControllerSiteDeployment(
                site_deployment=site_deployment,
                controller=site_deployment.controller,
            )
            ctrl_site_deployment.save()         
