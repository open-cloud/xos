from core.models.slice import Slice, SlicePrivilege
from plus import PlusObjectMixin

class SlicePlus(Slice, PlusObjectMixin):
    class Meta:
        proxy = True

    def getSliceInfo(self, user=None):
        used_sites = {}
        used_deployments = {}
        sliverCount = 0
        for sliver in self.slivers.all():
            site = sliver.node.site_deployment.site
            deployment = sliver.node.site_deployment.deployment
            used_sites[site.name] = used_sites.get(site.name, 0) + 1
            used_deployments[deployment.name] = used_deployments.get(deployment.name, 0) + 1
            sliverCount = sliverCount + 1

        roles = []
        if (user!=None):
            roles = [x.role.role for x in self.sliceprivileges.filter(user=user)]

        return {"sitesUsed": used_sites,
                "deploymentsUsed": used_deployments,
                "sliverCount": sliverCount,
                "siteCount": len(used_sites.keys()),
                "roles": roles}

    @property
    def site_allocation(self):
        return self.getSliceInfo()["sitesUsed"]

    @site_allocation.setter
    def site_allocation(self, value):
        print "XXX set sitesUsed to", value

    @property
    def users(self):
        user_ids = []
        for priv in SlicePrivilege.objects.filter(slice=self):
            if not (priv.user.id in user_ids):
                user_ids.append(priv.user.id)
        return user_ids

    @users.setter
    def users(self, value):
        print "XXX set users to", value

    @property
    def network_ports(self):
        # XXX this assumes there is only one network that can have ports bound
        # to it for a given slice. This is intended for the tenant view, which
        # will obey this field.
        networkPorts = ""
        for networkSlice in self.networkslices.all():
            network = networkSlice.network
            if network.ports:
                networkPorts = network.ports

        return networkPorts

    @network_ports.setter
    def network_ports(self, value):
        print "XXX set networkPorts to", value

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SlicePlus.objects.all()
        else:
            slice_ids = [sp.slice.id for sp in SlicePrivilege.objects.filter(user=user)]
            qs = SlicePlus.objects.filter(id__in=slice_ids)
        return qs
