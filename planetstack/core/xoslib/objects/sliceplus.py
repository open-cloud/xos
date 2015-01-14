from core.models import Slice, SlicePrivilege, SliceRole, Sliver, Site, Node, User
from plus import PlusObjectMixin
from operator import itemgetter, attrgetter

class SlicePlus(Slice, PlusObjectMixin):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(SlicePlus, self).__init__(*args, **kwargs)
        self._update_site_allocation = None
        self._update_users = None

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
        self._update_site_allocation = value
        #print "XXX set sitesUsed to", value

    @property
    def users(self):
        user_ids = []
        for priv in SlicePrivilege.objects.filter(slice=self):
            if not (priv.user.id in user_ids):
                user_ids.append(priv.user.id)
        return user_ids

    @users.setter
    def users(self, value):
        self._update_users = value
        #print "XXX set users to", value

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

    def get_node_allocation(self, siteList):
        siteIDList = [site.id for site in siteList]
        nodeList = []
        for node in Node.objects.all():
            if (node.site_deployment.site.id in siteIDList):
                node.sliverCount = 0
                for sliver in node.slivers.all():
                     if sliver.slice.id == self.id:
                         node.sliverCount = node.sliverCount + 1
                nodeList.append(node)
        return nodeList

    def save(self, *args, **kwargs):
        super(SlicePlus, self).save(*args, **kwargs)

        if self._update_site_allocation:
            self.save_site_allocation(noAct=True)

        if self._update_users:
            self.save_users(noAct=True)

        if self._update_site_allocation:
            self.save_site_allocation()

        if self._update_users:
            self.save_users()

    def save_site_allocation(self, noAct = False):
        new_site_allocation = self._update_site_allocation

        all_slice_slivers = self.slivers.all()
        for site_name in new_site_allocation.keys():
            desired_allocation = new_site_allocation[site_name]

            # make a list of the slivers for this site
            slivers = []
            for sliver in all_slice_slivers:
                if sliver.node.site_deployment.site.name == site_name:
                    slivers.append(sliver)

            # delete extra slivers
            while (len(slivers) > desired_allocation):
                sliver = slivers.pop()
                print "deleting sliver", sliver
                if (not noAct):
                    sliver.delete()

            # add more slivers
            if (len(slivers) < desired_allocation):
                site = Site.objects.get(name = site_name)
                nodes = self.get_node_allocation([site])

                if (not nodes):
                    raise ValueError("no nodes in site %s" % site_name)

                while (len(slivers) < desired_allocation):
                    # pick the least allocated node
                    nodes = sorted(nodes, key=attrgetter("sliverCount"))
                    node = nodes[0]

                    sliver = Sliver(name=node.name,
                            slice=self,
                            node=node,
                            image = self.default_image,
                            flavor = self.default_flavor,
                            creator = self.creator,
                            deployment = node.site_deployment.deployment)
                    slivers.append(sliver)
                    if (not noAct):
                        sliver.save()

                    print "added sliver", sliver

                    node.sliverCount = node.sliverCount + 1

    def save_users(self, noAct = False):
        new_users = self._update_users

        default_role = SliceRole.objects.get(role="default")

        slice_privs = self.sliceprivileges.all()
        slice_user_ids = [priv.user.id for priv in slice_privs]

        for user_id in new_users:
            if (user_id not in slice_user_ids):
                print "XXX", user_id
                priv = SlicePrivilege(slice=self, user=User.objects.get(id=user_id), role=default_role)
                if (not noAct):
                    priv.save()

                print "added user id", user_id

        for priv in slice_privs:
             if (priv.role.id != default_role.id):
                 # only mess with 'default' users; don't kill an admin
                 continue

             if (priv.user.id not in new_users):
                 if (not noAct):
                     priv.delete()

                 print "deleted user id", user_id





