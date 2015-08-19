import os
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import Controller
from core.models.network import *
from util.logger import observer_logger as logger

class SyncNetworkSlivers(OpenStackSyncStep):
    requested_interval = 0 # 3600
    provides=[NetworkSliver]
    observes=NetworkSliver

    #     The way it works is to enumerate the all of the ports that quantum
    #     has, and then work backward from each port's network-id to determine
    #     which Network is associated from the port.

    def call(self, **args):
        logger.info("sync'ing network slivers")

        networkSlivers = NetworkSliver.objects.all()
        networkSlivers_by_id = {}
        networkSlivers_by_port = {}
        for networkSliver in networkSlivers:
            networkSlivers_by_id[networkSliver.id] = networkSliver
            networkSlivers_by_port[networkSliver.port_id] = networkSliver

        networks = Network.objects.all()
        networks_by_id = {}
        for network in networks:
            for nd in network.controllernetworks.all():
                networks_by_id[nd.net_id] = network

        #logger.info("networks_by_id = ")
        #for (network_id, network) in networks_by_id.items():
        #    logger.info("   %s: %s" % (network_id, network.name))

        slivers = Sliver.objects.all()
        slivers_by_instance_uuid = {}
        for sliver in slivers:
            slivers_by_instance_uuid[sliver.instance_uuid] = sliver

        # Get all ports in all controllers

        ports_by_id = {}
        templates_by_id = {}
        for controller in Controller.objects.all():
            if not controller.admin_tenant:
                logger.info("controller %s has no admin_tenant" % controller)
                continue
            try:
                driver = self.driver.admin_driver(controller = controller,tenant='admin')
                ports = driver.shell.quantum.list_ports()["ports"]
            except:
                logger.log_exc("failed to get ports from controller %s" % controller)
                continue

            for port in ports:
                ports_by_id[port["id"]] = port

            # public-nat and public-dedicated networks don't have a net-id anywhere
            # in the data model, so build up a list of which ids map to which network
            # templates.
            try:
                neutron_networks = driver.shell.quantum.list_networks()["networks"]
            except:
                print "failed to get networks from controller %s" % controller
                continue
            for network in neutron_networks:
                for template in NetworkTemplate.objects.all():
                    if template.shared_network_name == network["name"]:
                        templates_by_id[network["id"]] = template

        for port in ports_by_id.values():
            #logger.info("port %s" % str(port))
            if port["id"] in networkSlivers_by_port:
                # we already have it
                #logger.info("already accounted for port %s" % port["id"])
                continue

            if port["device_owner"] != "compute:nova":
                # we only want the ports that connect to instances
                #logger.info("port %s is not a compute port, it is a %s" % (port["id"], port["device_owner"]))
                continue

            sliver = slivers_by_instance_uuid.get(port['device_id'], None)
            if not sliver:
                logger.info("no sliver for port %s device_id %s" % (port["id"], port['device_id']))
                continue

            network = networks_by_id.get(port['network_id'], None)
            if not network:
                # maybe it's public-nat or public-dedicated. Search the templates for
                # the id, then see if the sliver's slice has some network that uses
                # that template
                template = templates_by_id.get(port['network_id'], None)
                if template and sliver.slice:
                    for candidate_network in sliver.slice.networks.all():
                         if candidate_network.template == template:
                             network=candidate_network
            if not network:
                logger.info("no network for port %s network %s" % (port["id"], port["network_id"]))

                # we know it's associated with a sliver, but we don't know
                # which network it is part of.

                continue

            if network.template.shared_network_name:
                # If it's a shared network template, then more than one network
                # object maps to the quantum network. We have to do a whole bunch
                # of extra work to find the right one.
                networks = network.template.network_set.all()
                network = None
                for candidate_network in networks:
                    if (candidate_network.owner == sliver.slice):
                        print "found network", candidate_network
                        network = candidate_network

                if not network:
                    logger.info("failed to find the correct network for a shared template for port %s network %s" % (port["id"], port["network_id"]))
                    continue

            if not port["fixed_ips"]:
                logger.info("port %s has no fixed_ips" % port["id"])
                continue

            ip=port["fixed_ips"][0]["ip_address"]
            logger.info("creating NetworkSliver (%s, %s, %s, %s)" % (str(network), str(sliver), ip, str(port["id"])))

            ns = NetworkSliver(network=network,
                               sliver=sliver,
                               ip=ip,
                               port_id=port["id"])

            try:
                ns.save()
            except:
                logger.log_exc("failed to save networksliver %s" % str(ns))
                continue

        # For networkSlivers that were created by the user, find that ones
        # that don't have neutron ports, and create them.
        for networkSliver in NetworkSliver.objects.filter(port_id__isnull=True, sliver__isnull=False):
            #logger.info("XXX working on networksliver %s" % networkSliver)
            controller = sliver.node.site_deployment.controller
            if controller:
                cn=networkSliver.network.controllernetworks.filter(controller=controller)
                if not cn:
                    logger.log_exc("no controllernetwork for %s" % networkSliver)
                    continue
                cn=cn[0]
                try:
                    # We need to use a client driver that specifies the tenant
                    # of the destination sliver. Nova-compute will not connect
                    # ports to slivers if the port's tenant does not match
                    # the sliver's tenant.

                    # A bunch of stuff to compensate for OpenStackDriver.client_driveR()
                    # not being in working condition.
                    from openstack.client import OpenStackClient
                    from openstack.driver import OpenStackDriver
                    caller = networkSliver.network.owner.creator
                    auth = {'username': caller.email,
                            'password': caller.remote_password,
                            'tenant': networkSliver.sliver.slice.name} # networkSliver.network.owner.name}
                    client = OpenStackClient(controller=controller, **auth) # cacert=self.config.nova_ca_ssl_cert,
                    driver = OpenStackDriver(client=client)

                    port = driver.shell.quantum.create_port({"port": {"network_id": cn.net_id}})["port"]
                    networkSliver.port_id = port["id"]
                    if port["fixed_ips"]:
                        networkSliver.ip = port["fixed_ips"][0]["ip_address"]
                except:
                    logger.log_exc("failed to create neutron port for %s" % networkSliver)
                    continue
                networkSliver.save()

        # Now, handle port forwarding
        # We get the list of NetworkSlivers again, since we might have just
        # added a few. Then, for each one of them we find it's quantum port and
        # make sure quantum's nat:forward_ports argument is the same.

        for networkSliver in NetworkSliver.objects.all():
            try:
                nat_list = networkSliver.network.nat_list
            except (TypeError, ValueError), e:
                logger.info("Failed to decode nat_list: %s" % str(e))
                continue

            if not networkSliver.port_id:
                continue

            neutron_port = ports_by_id.get(networkSliver.port_id, None)
            if not neutron_port:
                continue

            neutron_nat_list = neutron_port.get("nat:forward_ports", None)
            if not neutron_nat_list:
                # make sure that None and the empty set are treated identically
                neutron_nat_list = []

            if (neutron_nat_list != nat_list):
                logger.info("Setting nat:forward_ports for port %s network %s sliver %s to %s" % (str(networkSliver.port_id), str(networkSliver.network.id), str(networkSliver.sliver), str(nat_list)))
                try:
                    driver = self.driver.admin_driver(controller=networkSliver.sliver.node.site_deployment.controller,tenant='admin')
                    driver.shell.quantum.update_port(networkSliver.port_id, {"port": {"nat:forward_ports": nat_list}})
                except:
                    logger.log_exc("failed to update port with nat_list %s" % str(nat_list))
                    continue
            else:
                #logger.info("port %s network %s sliver %s nat %s is already set" % (str(networkSliver.port_id), str(networkSliver.network.id), str(networkSliver.sliver), str(nat_list)))
                pass

    def delete_record(self, network_sliver):
        # Nothing to do, this is an OpenCloud object
        pass

