
def handle(site):
    from core.models import Controller, ControllerSite, Site 

    # site = Site.get(site_id)
    # make sure site has a ControllerSite record for each controller
    ctrl_sites = ControllerSite.objects.filter(site=site)
    existing_controllers = [cs.controller for cs in ctrl_sites]

    all_controllers = Controller.objects.all()
    for ctrl in all_controllers:
        if ctrl not in existing_controllers:
            ctrl_site = ControllerSite(controller=ctrl, site=site)
            ctrl_site.save() 
