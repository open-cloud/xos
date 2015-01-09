from core.models.slice import Slice
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
    def networkPorts(self):
        # XXX this assumes there is only one network that can have ports bound
        # to it for a given slice. This is intended for the tenant view, which
        # will obey this field.
        networkPorts = ""
        for networkSlice in self.networkslices.all():
            network = networkSlice.network
            if network.ports:
                networkPorts = network.ports

        return networkPorts

    @networkPorts.setter
    def networkPorts(self, value):
        print "XXX set networkPorts to", value

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SlicePlus.objects.all()
        else:
            slice_ids = [sp.slice.id for sp in SlicePrivilege.objects.filter(user=user)]
            qs = SlicePlus.objects.filter(id__in=slice_ids)
        return qs
