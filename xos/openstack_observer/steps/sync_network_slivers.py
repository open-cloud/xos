import os
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import Controller
from core.models.network import *
from util.logger import observer_logger as logger

class SyncNetworkInstances(OpenStackSyncStep):
    requested_interval = 0 # 3600
    provides=[NetworkInstance]
    observes=NetworkInstance

    #     The way it works is to enumerate the all of the ports that quantum
    #     has, and then work backward from each port's network-id to determine
    #     which Network is associated from the port.

    def call(self, **args):
        logger.info("sync'ing network instances")

        networkInstances = NetworkInstance.objects.all()
        networkInstances_by_id = {}
        networkInstances_by_port = {}
        for networkInstance in networkInstances:
            networkInstances_by_id[networkInstance.id] = networkInstance
            networkInstances_by_port[networkInstance.port_id] = networkInstance

        networks = Network.objects.all()
        networks_by_id = {}
        for network in networks:
            for nd in network.controllernetworks.all():
                networks_by_id[nd.net_id] = network

        #logger.info("networks_by_id = ")
        #for (network_id, network) in networks_by_id.items():
        #    logger.info("   %s: %s" % (network_id, network.name))

        instances = Instance.objects.all()
        instances_by_instance_uuid = {}
        for instance in instances:
            instances_by_instance_uuid[instance.instance_uuid] = instance

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
            if port["id"] in networkInstances_by_port:
                # we already have it
                #logger.info("already accounted for port %s" % port["id"])
                continue

            if port["device_owner"] != "compute:nova":
                # we only want the ports that connect to instances
                #logger.info("port %s is not a compute port, it is a %s" % (port["id"], port["device_owner"]))
                continue

            instance = instances_by_instance_uuid.get(port['device_id'], None)
            if not instance:
                logger.info("no instance for port %s device_id %s" % (port["id"], port['device_id']))
                continue

            network = networks_by_id.get(port['network_id'], None)
            if not network:
                # maybe it's public-nat or public-dedicated. Search the templates for
                # the id, then see if the instance's slice has some network that uses
                # that template
                template = templates_by_id.get(port['network_id'], None)
                if template and instance.slice:
                    for candidate_network in instance.slice.networks.all():
                         if candidate_network.template == template:
                             network=candidate_network
            if not network:
                logger.info("no network for port %s network %s" % (port["id"], port["network_id"]))

                # we know it's associated with a instance, but we don't know
                # which network it is part of.

                continue

            if network.template.shared_network_name:
                # If it's a shared network template, then more than one network
                # object maps to the quantum network. We have to do a whole bunch
                # of extra work to find the right one.
                networks = network.template.network_set.all()
                network = None
                for candidate_network in networks:
                    if (candidate_network.owner == instance.slice):
                        print "found network", candidate_network
                        network = candidate_network

                if not network:
                    logger.info("failed to find the correct network for a shared template for port %s network %s" % (port["id"], port["network_id"]))
                    continue

            if not port["fixed_ips"]:
                logger.info("port %s has no fixed_ips" % port["id"])
                continue

            ip=port["fixed_ips"][0]["ip_address"]
            logger.info("creating NetworkInstance (%s, %s, %s, %s)" % (str(network), str(instance), ip, str(port["id"])))

            ns = NetworkInstance(network=network,
                               instance=instance,
                               ip=ip,
                               port_id=port["id"])

            try:
                ns.save()
            except:
                logger.log_exc("failed to save networkinstance %s" % str(ns))
                continue

        # For networkInstances that were created by the user, find that ones
        # that don't have neutron ports, and create them.
        for networkInstance in NetworkInstance.objects.filter(port_id__isnull=True, instance__isnull=False):
            #logger.info("working on networkinstance %s" % networkInstance)
            controller = instance.node.site_deployment.controller
            if controller:
                cn=networkInstance.network.controllernetworks.filter(controller=controller)
                if not cn:
                    logger.log_exc("no controllernetwork for %s" % networkInstance)
                    continue
                cn=cn[0]
                try:
                    driver = self.driver.admin_driver(controller = controller,tenant='admin')
                    port = driver.shell.quantum.create_port({"port": {"network_id": cn.net_id}})["port"]
                    networkInstance.port_id = port["id"]
                    if port["fixed_ips"]:
                        networkInstance.ip = port["fixed_ips"][0]["ip_address"]
                except:
                    logger.log_exc("failed to create neutron port for %s" % networkInstance)
                    continue
                networkInstance.save()

        # Now, handle port forwarding
        # We get the list of NetworkInstances again, since we might have just
        # added a few. Then, for each one of them we find it's quantum port and
        # make sure quantum's nat:forward_ports argument is the same.

        for networkInstance in NetworkInstance.objects.all():
            try:
                nat_list = networkInstance.network.nat_list
            except (TypeError, ValueError), e:
                logger.info("Failed to decode nat_list: %s" % str(e))
                continue

            if not networkInstance.port_id:
                continue

            neutron_port = ports_by_id.get(networkInstance.port_id, None)
            if not neutron_port:
                continue

            neutron_nat_list = neutron_port.get("nat:forward_ports", None)
            if not neutron_nat_list:
                # make sure that None and the empty set are treated identically
                neutron_nat_list = []

            if (neutron_nat_list != nat_list):
                logger.info("Setting nat:forward_ports for port %s network %s instance %s to %s" % (str(networkInstance.port_id), str(networkInstance.network.id), str(networkInstance.instance), str(nat_list)))
                try:
                    driver = self.driver.admin_driver(controller=networkInstance.instance.node.site_deployment.controller,tenant='admin')
                    driver.shell.quantum.update_port(networkInstance.port_id, {"port": {"nat:forward_ports": nat_list}})
                except:
                    logger.log_exc("failed to update port with nat_list %s" % str(nat_list))
                    continue
            else:
                #logger.info("port %s network %s instance %s nat %s is already set" % (str(networkInstance.port_id), str(networkInstance.network.id), str(networkInstance.instance), str(nat_list)))
                pass

    def delete_record(self, network_instance):
        # Nothing to do, this is an OpenCloud object
        pass

