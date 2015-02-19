from core.models import Slice, SlicePrivilege, SliceRole, Sliver, Site, Node, User
from plus import PlusObjectMixin
from operator import itemgetter, attrgetter
from rest_framework.exceptions import APIException

class SlicePlus(Slice, PlusObjectMixin):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(SlicePlus, self).__init__(*args, **kwargs)
        self._update_users = None
        self._sliceInfo = None
        self.getSliceInfo()
        self._site_allocation = self._sliceInfo["sitesUsed"]
        self._initial_site_allocation = self._site_allocation
        self._network_ports = self._sliceInfo["networkPorts"]
        self._initial_network_ports = self._network_ports

    def getSliceInfo(self, user=None):
        if not self._sliceInfo:
            used_sites = {}
            ready_sites = {}
            used_deployments = {}
            sliverCount = 0
            sshCommands = []
            for sliver in self.slivers.all():
                site = sliver.node.site_deployment.site
                deployment = sliver.node.site_deployment.deployment
                used_sites[site.name] = used_sites.get(site.name, 0) + 1
                used_deployments[deployment.name] = used_deployments.get(deployment.name, 0) + 1
                sliverCount = sliverCount + 1

                sshCommand = sliver.get_ssh_command()
                if sshCommand:
                    sshCommands.append(sshCommand)

                    ready_sites[site.name] = ready_sites.get(site.name, 0) + 1

            users = {}
            for priv in SlicePrivilege.objects.filter(slice=self):
                if not (priv.user.id in users.keys()):
                    users[priv.user.id] = {"name": priv.user.email, "id": priv.user.id, "roles": []}
                users[priv.user.id]["roles"].append(priv.role.role)

            # XXX this assumes there is only one network that can have ports bound
            # to it for a given slice. This is intended for the tenant view, which
            # will obey this field.
            networkPorts = ""
            for networkSlice in self.networkslices.all():
                network = networkSlice.network
                if (network.owner.id != self.id):
                    continue
                if network.ports:
                    networkPorts = network.ports

            self._sliceInfo= {"sitesUsed": used_sites,
                    "sitesReady": ready_sites,
                    "deploymentsUsed": used_deployments,
                    "sliverCount": sliverCount,
                    "siteCount": len(used_sites.keys()),
                    "users": users,
                    "roles": [],
                    "sshCommands": sshCommands,
                    "networkPorts": networkPorts}

        if user:
            auser = self._sliceInfo["users"].get(user.id, None)
            if (auser):
                self._sliceInfo["roles"] = auser["roles"]

        return self._sliceInfo

    @property
    def site_ready(self):
        return self.getSliceInfo()["sitesReady"]

    @site_ready.setter
    def site_ready(self, value):
        pass

    @property
    def site_allocation(self):
        return self._site_allocation

    @site_allocation.setter
    def site_allocation(self, value):
        self._site_allocation = value

    @property
    def user_names(self):
        return [user["name"] for user in self.getSliceInfo()["users"].values()]

    @user_names.setter
    def user_names(self, value):
        pass # it's read-only

    @property
    def users(self):
        return [user["id"] for user in self.getSliceInfo()["users"].values()]

    @users.setter
    def users(self, value):
        self._update_users = value
        #print "XXX set users to", value

    @property
    def network_ports(self):
        return self._network_ports

    @network_ports.setter
    def network_ports(self, value):
        self._network_ports = value
        #print "XXX set networkPorts to", value

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
        if (not hasattr(self,"caller")) or self.caller==None:
            raise APIException("no self.caller in SlicePlus.save")

        updated_image = self.has_field_changed("default_image")
        updated_flavor = self.has_field_changed("default_flavor")

        super(SlicePlus, self).save(*args, **kwargs)

        # try things out first

        updated_sites = (self._site_allocation != self._initial_site_allocation) or updated_image or updated_flavor
        if updated_sites:
            self.save_site_allocation(noAct=True, reset=(updated_image or updated_flavor))

        if self._update_users:
            self.save_users(noAct=True)

        if (self._network_ports != self._initial_network_ports):
            self.save_network_ports(noAct=True)

        # now actually save them

        if updated_sites:
            self.save_site_allocation(reset=(updated_image or updated_flavor))

        if self._update_users:
            self.save_users()

        if (self._network_ports != self._initial_network_ports):
            self.save_network_ports()

    def save_site_allocation(self, noAct = False, reset=False):
        print "save_site_allocation, reset=",reset

        if (not self._site_allocation):
            # Must be a sliver that was just created, and has not site_allocation
            # field.
            return

        all_slice_slivers = self.slivers.all()
        for site_name in self._site_allocation.keys():
            desired_allocation = self._site_allocation[site_name]

            # make a list of the slivers for this site
            slivers = []
            for sliver in all_slice_slivers:
                if sliver.node.site_deployment.site.name == site_name:
                    slivers.append(sliver)

            # delete extra slivers
            while (reset and len(slivers)>0) or (len(slivers) > desired_allocation):
                sliver = slivers.pop()
                if (not noAct):
                    print "deleting sliver", sliver
                    sliver.delete()
                else:
                    print "would delete sliver", sliver

            # add more slivers
            if (len(slivers) < desired_allocation):
                site = Site.objects.get(name = site_name)
                nodes = self.get_node_allocation([site])

                if (not nodes):
                    raise APIException(detail="no nodes in site %s" % site_name)

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
                    sliver.caller = self.caller
                    slivers.append(sliver)
                    if (not noAct):
                        print "added sliver", sliver
                        sliver.save()
                    else:
                        print "would add sliver", sliver

                    node.sliverCount = node.sliverCount + 1

    def save_users(self, noAct = False):
        new_users = self._update_users

        try:
            default_role = SliceRole.objects.get(role="access")
        except:
            default_role = SliceRole.objects.get(role="default")

        slice_privs = self.sliceprivileges.all()
        slice_user_ids = [priv.user.id for priv in slice_privs]

        for user_id in new_users:
            if (user_id not in slice_user_ids):
                priv = SlicePrivilege(slice=self, user=User.objects.get(id=user_id), role=default_role)
                priv.caller = self.caller
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

    def save_network_ports(self, noAct=False):
        # First search for any network that already has a filled in 'ports'
        # field. We'll assume there can only be one, so it must be the right
        # one.
        for networkSlice in self.networkslices.all():
            network = networkSlice.network
            if (network.owner.id != self.id):
                continue
            if network.ports:
                network.ports = self._network_ports
                network.caller = self.caller
                if (not noAct):
                    network.save()
                return

        # Now try a network that is a "NAT", since setting ports on a non-NAT
        # network doesn't make much sense.
        for networkSlice in self.networkslices.all():
            network = networkSlice.network
            if (network.owner.id != self.id):
                continue
            if network.template.translation=="NAT":
                network.ports = self._network_ports
                network.caller = self.caller
                if (not noAct):
                    network.save()
                return

        # uh oh, we didn't find a network

        raise APIException(detail="No network was found that ports could be set on")





