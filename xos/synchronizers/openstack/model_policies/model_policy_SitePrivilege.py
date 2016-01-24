def handle(site_privilege):
    from core.models import Controller, SitePrivilege, ControllerSitePrivilege
    
    # site_privilege = SitePrivilege.get(site_privilege_id)
    # apply site privilage at all controllers
    controller_site_privileges = ControllerSitePrivilege.objects.filter(
        site_privilege = site_privilege,
        )
    existing_controllers = [sp.controller for sp in controller_site_privileges]
    all_controllers = Controller.objects.all()
    for controller in all_controllers:
        if controller not in existing_controllers:
            ctrl_site_priv = ControllerSitePrivilege(controller=controller, site_privilege=site_privilege)
            ctrl_site_priv.save()  

