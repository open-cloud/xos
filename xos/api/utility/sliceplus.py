from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.exceptions import APIException
from core.models import *
from django.forms import widgets
from core.xoslib.objects.sliceplus import SlicePlus
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
import json
from core.models import Slice, SlicePrivilege, SliceRole, Instance, Site, Node, User
from operator import itemgetter, attrgetter
from api.xosapi_helpers import PlusObjectMixin, PlusModelSerializer

# rest_framework 3.x
IdField = serializers.ReadOnlyField
WritableField = serializers.Field
DictionaryField = serializers.DictField
ListField = serializers.ListField


class SlicePlus(Slice, PlusObjectMixin):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(SlicePlus, self).__init__(*args, **kwargs)
        self._update_users = None
        self._sliceInfo = None
        self.getSliceInfo()
        self._instance_status = self._sliceInfo["instanceStatus"]
        self._instance_distribution = self._sliceInfo["sitesUsed"]
        self._initial_instance_distribution = self._instance_distribution
        self._network_ports = self._sliceInfo["networkPorts"]
        self._initial_network_ports = self._network_ports
        self._current_user_roles = self._sliceInfo["roles"]

    def getSliceInfo(self, user=None):
        if not self._sliceInfo:
            site_status = {}
            used_sites = {}
            ready_sites = {}
            used_deployments = {}
            instanceCount = 0
            instance_status = {}
            sshCommands = []
            for instance in self.instances.all():
                site = instance.node.site_deployment.site
                deployment = instance.node.site_deployment.deployment
                used_sites[site.name] = used_sites.get(site.name, 0) + 1
                used_deployments[deployment.name] = used_deployments.get(deployment.name, 0) + 1
                instanceCount = instanceCount + 1

                if instance.backend_status:
                    status = instance.backend_status[0]
                else:
                    status = "none"

                if not status in instance_status:
                    instance_status[status] = 0
                instance_status[status] = instance_status[status] + 1

                sshCommand = instance.get_ssh_command()
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

            self._sliceInfo = {
                    "sitesUsed": used_sites,
                    "sitesReady": ready_sites,
                    "instanceStatus": instance_status,
                    "deploymentsUsed": used_deployments,
                    "instanceCount": instanceCount,
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
    def instance_distribution_ready(self):
        return self._sliceInfo["sitesReady"]

    @property
    def instance_total_ready(self):
        return sum(self._sliceInfo["sitesReady"].values())

    @property
    def current_user_roles(self):
        return self._current_user_roles

    @property
    def instance_distribution(self):
        return self._instance_distribution

    @instance_distribution.setter
    def instance_distribution(self, value):
        self._instance_distribution = value

    @property
    def instance_total(self):
        return sum(self._instance_distribution.values())

    @property
    def instance_status(self):
        return self._instance_status

    @property
    def user_names(self):
        return [user["name"] for user in self.getSliceInfo()["users"].values()]

    @user_names.setter
    def user_names(self, value):
        pass  # it's read-only

    @property
    def users(self):
        return [user["id"] for user in self.getSliceInfo()["users"].values()]

    @users.setter
    def users(self, value):
        self._update_users = value

    @property
    def network_ports(self):
        return self._network_ports

    @network_ports.setter
    def network_ports(self, value):
        self._network_ports = value

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
                node.instanceCount = 0
                for instance in node.instances.all():
                    if instance.slice.id == self.id:
                        node.instanceCount = node.instanceCount + 1
                nodeList.append(node)
        return nodeList

    def save(self, *args, **kwargs):
        if (not hasattr(self, "caller")) or self.caller==None:
            raise APIException("no self.caller in SlicePlus.save")

        updated_image = self.has_field_changed("default_image")
        updated_flavor = self.has_field_changed("default_flavor")

        super(SlicePlus, self).save(*args, **kwargs)

        # try things out first

        updated_sites = (self._instance_distribution != self._initial_instance_distribution) or updated_image or updated_flavor
        if updated_sites:
            self.save_instance_distribution(noAct=True, reset=(updated_image or updated_flavor))

        if self._update_users:
            self.save_users(noAct=True)

        if (self._network_ports != self._initial_network_ports):
            self.save_network_ports(noAct=True)

        # now actually save them

        if updated_sites:
            self.save_instance_distribution(reset=(updated_image or updated_flavor))

        if self._update_users:
            self.save_users()

        if (self._network_ports != self._initial_network_ports):
            self.save_network_ports()

    def save_instance_distribution(self, noAct = False, reset=False):
        print "save_instance_distribution, reset=",reset

        if (not self._instance_distribution):
            # Must be a instance that was just created, and has not instance_distribution
            # field.
            return

        all_slice_instances = self.instances.all()
        for site_name in self._instance_distribution.keys():
            desired_allocation = self._instance_distribution[site_name]

            # make a list of the instances for this site
            instances = []
            for instance in all_slice_instances:
                if instance.node.site_deployment.site.name == site_name:
                    instances.append(instance)

            # delete extra instances
            while (reset and len(instances) > 0) or (len(instances) > desired_allocation):
                instance = instances.pop()
                if (not noAct):
                    print "deleting instance", instance
                    instance.delete()
                else:
                    print "would delete instance", instance

            # add more instances
            if (len(instances) < desired_allocation):
                site = Site.objects.get(name=site_name)
                nodes = self.get_node_allocation([site])

                if (not nodes):
                    raise APIException(detail="no nodes in site %s" % site_name)

                while (len(instances) < desired_allocation):
                    # pick the least allocated node
                    nodes = sorted(nodes, key=attrgetter("instanceCount"))
                    node = nodes[0]

                    instance = Instance(name=node.name,
                                        slice=self,
                                        node=node,
                                        image=self.default_image,
                                        flavor=self.default_flavor,
                                        creator=self.creator,
                                        deployment=node.site_deployment.deployment)
                    instance.caller = self.caller
                    instances.append(instance)
                    if (not noAct):
                        print "added instance", instance
                        instance.save()
                    else:
                        print "would add instance", instance

                    node.instanceCount = node.instanceCount + 1

    def save_users(self, noAct=False):
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
            if network.template.translation == "NAT":
                network.ports = self._network_ports
                network.caller = self.caller
                if (not noAct):
                    network.save()
                return

        # uh oh, we didn't find a network

        raise APIException(detail="No network was found that ports could be set on")


class SlicePlusIdSerializer(PlusModelSerializer):
        id = IdField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        network_ports = serializers.CharField(required=False)
        instance_distribution = DictionaryField(required=False)
        instance_distribution_ready = DictionaryField(read_only=True)
        instance_total = serializers.IntegerField(read_only=True)
        instance_total_ready = serializers.IntegerField(read_only=True)
        instance_status = DictionaryField(read_only=True)
        users = ListField(required=False)
        user_names = ListField(required=False)  # readonly = True ?
        current_user_can_see = serializers.SerializerMethodField("getCurrentUserCanSee")

        def getCurrentUserCanSee(self, slice):
            # user can 'see' the slice if he is the creator or he has a role
            current_user = self.context['request'].user
            if (slice.creator and slice.creator == current_user):
                return True
            return (len(slice.getSliceInfo(current_user)["roles"]) > 0)

        def getSliceInfo(self, slice):
            return slice.getSliceInfo(user=self.context['request'].user)

        def getHumanReadableName(self, obj):
            return str(obj)

        networks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

        class Meta:
            model = SlicePlus
            fields = ('humanReadableName', 'id', 'created', 'updated', 'enacted', 'name', 'enabled', 'omf_friendly',
                      'description', 'slice_url', 'site', 'max_instances', 'service', 'network', 'mount_data_sets',
                      'default_image', 'default_flavor',
                      'serviceClass', 'creator',

                      # these are the value-added fields from SlicePlus
                      'networks', 'network_ports', 'backendIcon', 'backendHtml',
                      'current_user_roles',  'instance_distribution', 'instance_distribution_ready', 'instance_total',
                      'instance_total_ready', 'instance_status', 'users', "user_names", "current_user_can_see")


class SlicePlusList(XOSListCreateAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "list"
    method_name = "slicesplus"

    def get_queryset(self):
        current_user_can_see = self.request.query_params.get('current_user_can_see', False)
        site_filter = self.request.query_params.get('site', False)

        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")

        slices = SlicePlus.select_by_user(self.request.user)

        if (site_filter and not current_user_can_see):
            slices = SlicePlus.objects.filter(site=site_filter)

        # If current_user_can_see is set, then filter the queryset to return
        # only those slices that the user is either creator or has privilege
        # on.
        if (current_user_can_see):
            slice_ids = []
            for slice in slices:
                if (self.request.user == slice.creator) or (len(slice.getSliceInfo(self.request.user)["roles"]) > 0):
                    slice_ids.append(slice.id)
            if (site_filter):
                slices = SlicePlus.objects.filter(id__in=slice_ids, site=site_filter)
            else:
                slices = SlicePlus.objects.filter(id__in=slice_ids)

        return slices


class SlicePlusDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "detail"
    method_name = "slicesplus"

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        return SlicePlus.select_by_user(self.request.user)
