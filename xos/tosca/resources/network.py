
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from xosresource import XOSResource
from core.models import Slice,User,Network,NetworkTemplate,NetworkSlice,Service,ServiceInstanceLink

class XOSNetwork(XOSResource):
    provides = ["tosca.nodes.network.Network", "tosca.nodes.network.Network.XOS"]
    xos_model = Network
    copyin_props = ["ports", "labels"]

    def get_xos_args(self):
        args = super(XOSNetwork, self).get_xos_args()

        args["autoconnect"] = False

        slice_name = self.get_requirement("tosca.relationships.MemberOfSlice")
        if slice_name:
            args["owner"] = self.get_xos_object(Slice, name=slice_name)

        net_template_name = self.get_requirement("tosca.relationships.UsesNetworkTemplate")
        if net_template_name:
            args["template"] = self.get_xos_object(NetworkTemplate, name=net_template_name)

        if self.nodetemplate.type == "tosca.nodes.network.Network.XOS":
            # copy simple string properties from the template into the arguments
            for prop in ["ports", "labels", "permit_all_slices"]:
                v = self.get_property(prop)
                if v:
                    args[prop] = v
        else:
            # tosca.nodes.network.Network is not as rich as an XOS network. So
            # we have to manually fill in some defaults.
            args["permit_all_slices"] = True

        cidr = self.get_property_default("cidr", None)
        if cidr:
            args["subnet"] = cidr
        print "DEF_RES_CIDR", cidr 

        start_ip = self.get_property_default("start_ip", None)
        if start_ip:
            args["start_ip"] = start_ip 
        print "DEF_RES_IP", start_ip 

        end_ip = self.get_property_default("end_ip", None)
        if end_ip:
            args["end_ip"] = end_ip

        return args

    def postprocess(self, obj):
        for sliceName in self.get_requirements("tosca.relationships.ConnectsToSlice"):
            slice = self.get_xos_object(Slice, name=sliceName)
            netSlices = NetworkSlice.objects.filter(network=obj, slice = slice)
            if not netSlices:
                self.info("Attached Network %s to Slice %s" % (obj, slice))
                ns = NetworkSlice(network = obj, slice=slice)
                ns.save()

        # this is really for vRouter
        for provider_service_name in self.get_requirements("tosca.relationships.TenantOfService"):
            provider_service = self.get_xos_object(Service, name=provider_service_name)

            existing_links = ServiceInstanceLink.objects.filter(subscriber_network = obj, provider_service_instance__owner=provider_service)

            if existing_links:
                self.info("Tenancy relationship from %s to %s already exists" % (str(obj), str(provider_service)))
            else:
                # TODO: Break hardcoded dependencies
                # TODO: Rethink relationship between networks and vrouter tenants
                if provider_service.kind == "vROUTER":
                    # DEPRECATED
                    from services.vrouter.models import VRouterService
                    si = VRouterService.objects.get(id=provider_service.id).get_tenant(address_pool_name="addresses_"+obj.name)
                elif provider_service.kind == "addressmanager":
                    from services.addressmanager.models import AddressManagerService
                    si = AddressManagerService.objects.get(id=provider_service.id).get_service_instance(address_pool_name="addresses_"+obj.name)
                else:
                    # Hardcoded dependency, will be obsoleted by new Tosca engine
                    raise Exception(
                        "The only network tenancy relationships that are allowed are to vRouter and AddressManager services")

                si.save()
                link = ServiceInstanceLink(provider_service_instance=si, subscriber_network=obj)
                link.save()

                obj.subnet = si.cidr

                self.info("Created Tenancy relationship from %s to %s" % (str(obj), str(provider_service)))


    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()

        if not xos_args.get("owner", None):
            raise Exception("Must specify slice when creating network")
        if not xos_args.get("template", None):
            raise Exception("Must specify network template when creating network")

        # XXX TODO: investigate using transaction.atomic instead of setting
        #   no_sync and no_policy

        network = Network(**xos_args)
        network.caller = self.user
        network.no_sync = True        # postprocess might set the cidr
        network.no_policy = True
        network.save()

        self.postprocess(network)

        network.no_sync = False
        network.no_policy = False
        network.save()

        self.info("Created Network '%s' owned by Slice '%s'" % (str(network), str(network.owner)))

    def delete(self, obj):
        super(XOSNetwork, self).delete(obj)



