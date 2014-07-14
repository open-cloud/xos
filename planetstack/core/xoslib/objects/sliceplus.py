from core.models.slice import Slice

class SlicePlus(Slice):
    class Meta:
        proxy = True

    def getSliceInfo(self, user=None):
        used_sites = {}
        used_deployments = {}
        sliverCount = 0
        for sliver in self.slivers.all():
            site = sliver.node.site
            deployment = sliver.node.deployment
            used_sites[site.name] = used_sites.get(site.name, 0) + 1
            used_deployments[deployment.name] = used_deployments.get(deployment.name, 0) + 1
            sliverCount = sliverCount + 1

        roles = []
        if (user!=None):
            roles = [x.role for x in self.slice_privileges.filter(user=user)]

        return {"sitesUsed": used_sites,
                "deploymentsUsed": used_deployments,
                "sliverCount": sliverCount,
                "siteCount": len(used_sites.keys()),
                "roles": roles}

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SlicePlus.objects.all()
        else:
            slice_ids = [sp.slice.id for sp in SlicePrivilege.objects.filter(user=user)]
            qs = SlicePlus.objects.filter(id__in=slice_ids)
        return qs
