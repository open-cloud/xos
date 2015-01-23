
def handle(controller):
    from core.models import Controller, Site, ControllerSite, Slice, ControllerSlice, User, ControllerUser
    from collections import defaultdict

    # relations for all sites
    ctrls_by_site = defaultdict(list)
    ctrl_sites = ControllerSite.objects.all()
    for ctrl_site in ctrl_sites:
        ctrls_by_site[ctrl_site.site].append(ctrl_site.controller)
    sites = Site.objects.all()
    for site in sites:
        if site not in ctrls_by_site or \
            controller not in ctrls_by_site[site]:
            controller_site = ControllerSite(controller=controller, site=site)
            controller_site.save()
    # relations for all slices
    ctrls_by_slice = defaultdict(list)
    ctrl_slices = ControllerSlice.objects.all()
    for ctrl_slice in ctrl_slices:
        ctrls_by_slice[ctrl_slice.slice].append(ctrl_slice.controller)
    slices = Slice.objects.all()
    for slice in slices:
        if slice not in ctrls_by_slice or \
            controller not in ctrls_by_slice:
            controller_slice = ControllerSlice(controller=controller, slice=slice)
            controller_slice.save()
    # relations for all users
    ctrls_by_user = defaultdict(list)
    ctrl_users = ControllerUser.objects.all()
    for ctrl_user in ctrl_users:
        ctrls_by_user[ctrl_user.user].append(ctrl_user.controller)
    users = User.objects.all()
    for user in users:
        if user not in ctrls_by_user or \
            controller not in ctrls_by_user[user]:
            controller_user = ControllerUser(controller=controller, user=user)
            controller_user.save()
