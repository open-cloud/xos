import hashlib
import os
import socket
import sys
import base64
import time
import re
import json
from collections import OrderedDict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.ansible import run_template
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice, Controller, ControllerSlice, ControllerUser, Node, TenantAttribute, Tag
from services.onos.models import ONOSService, ONOSApp
from xos.logger import Logger, logging
from services.vrouter.models import VRouterService
from services.vtn.models import VTNService
from services.volt.models import VOLTService, VOLTDevice, AccessDevice

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncONOSApp(SyncInstanceUsingAnsible):
    provides=[ONOSApp]
    observes=ONOSApp
    requested_interval=0
    template_name = "sync_onosapp.yaml"
    #service_key_name = "/opt/xos/synchronizers/onos/onos_key"

    def __init__(self, *args, **kwargs):
        super(SyncONOSApp, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = ONOSApp.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = ONOSApp.get_deleted_tenant_objects()

        return objs

    def get_instance(self, o):
        # We assume the ONOS service owns a slice, so pick one of the instances
        # inside that slice to sync to.

        serv = self.get_onos_service(o)

        if serv.no_container:
            raise Exception("get_instance() was called on a service that was marked no_container")

        if serv.slices.exists():
            slice = serv.slices.all()[0]
            if slice.instances.exists():
                return slice.instances.all()[0]

        return None

    def get_onos_service(self, o):
        if not o.provider_service:
            return None

        onoses = ONOSService.get_service_objects().filter(id=o.provider_service.id)
        if not onoses:
            return None

        return onoses[0]

    def is_no_container(self, o):
        return self.get_onos_service(o).no_container

    def skip_ansible_fields(self, o):
        return self.is_no_container(o)

    def get_files_dir(self, o):
        if not hasattr(Config(), "observer_steps_dir"):
            # make steps_dir mandatory; there's no valid reason for it to not
            # be defined.
            raise Exception("observer_steps_dir is not defined in config file")

        step_dir = Config().observer_steps_dir

        return os.path.join(step_dir, "..", "files", str(self.get_onos_service(o).id), o.name)

    def get_cluster_configuration(self, o):
        instance = self.get_instance(o)
        if not instance:
           raise Exception("No instance for ONOS App")
        node_ips = [socket.gethostbyname(instance.node.name)]

        ipPrefix = ".".join(node_ips[0].split(".")[:3]) + ".*"
        result = '{ "nodes": ['
        result = result + ",".join(['{ "ip": "%s"}' % ip for ip in node_ips])
        result = result + '], "ipPrefix": "%s"}' % ipPrefix
        return result

    def get_dynamic_parameter_value(self, o, param):
        instance = self.get_instance(o)
        if not instance:
           raise Exception("No instance for ONOS App")
        if param == 'rabbit_host':
            return instance.controller.rabbit_host
        if param == 'rabbit_user':
            return instance.controller.rabbit_user
        if param == 'rabbit_password':
            return instance.controller.rabbit_password
        if param == 'keystone_tenant_id':
            cslice = ControllerSlice.objects.get(slice=instance.slice)
            if not cslice:
                raise Exception("Controller slice object for %s does not exist" % instance.slice.name)
            return cslice.tenant_id
        if param == 'keystone_user_id':
            cuser = ControllerUser.objects.get(user=instance.creator)
            if not cuser:
                raise Exception("Controller user object for %s does not exist" % instance.creator)
            return cuser.kuser_id

    def get_node_tag(self, o, node, tagname):
        tags = Tag.select_by_content_object(node).filter(name=tagname)
        return tags[0].value

    # Scan attrs for attribute name
    # If it's not present, save it as a TenantAttribute
    def attribute_default(self, tenant, attrs, name, default):
        if name in attrs:
            value = attrs[name]
        else:
            value = default
            logger.info("saving default value %s for attribute %s" % (value, name))
            ta = TenantAttribute(tenant=tenant, name=name, value=value)
            ta.save()
        return value

    # This function currently assumes a single Deployment and Site
    def get_vtn_config(self, o, attrs):

        privateGatewayMac = None
        localManagementIp = None
        ovsdbPort = None
        sshPort = None
        sshUser = None
        sshKeyFile = None
        mgmtSubnetBits = None
        xosEndpoint = None
        xosUser = None
        xosPassword = None

        # VTN-specific configuration from the VTN Service
        vtns = VTNService.get_service_objects().all()
        if vtns:
            vtn = vtns[0]
            privateGatewayMac = vtn.privateGatewayMac
            localManagementIp = vtn.localManagementIp
            ovsdbPort = vtn.ovsdbPort
            sshPort = vtn.sshPort
            sshUser = vtn.sshUser
            sshKeyFile = vtn.sshKeyFile
            mgmtSubnetBits = vtn.mgmtSubnetBits
            xosEndpoint = vtn.xosEndpoint
            xosUser = vtn.xosUser
            xosPassword = vtn.xosPassword

        # OpenStack endpoints and credentials
        keystone_server = "http://keystone:5000/v2.0/"
        user_name = "admin"
        password = "ADMIN_PASS"
        controllers = Controller.objects.all()
        if controllers:
            controller = controllers[0]
            keystone_server = controller.auth_url
            user_name = controller.admin_user
            tenant_name = controller.admin_tenant
            password = controller.admin_password

        data = {
            "apps" : {
                "org.onosproject.cordvtn" : {
                    "cordvtn" : {
                        "privateGatewayMac" : privateGatewayMac,
                        "localManagementIp": localManagementIp,
                        "ovsdbPort": ovsdbPort,
                        "ssh": {
                            "sshPort": sshPort,
                            "sshUser": sshUser,
                            "sshKeyFile": sshKeyFile
                        },
                        "openstack": {
                            "endpoint": keystone_server,
                            "tenant": tenant_name,
                            "user": user_name,
                            "password": password
                        },
                        "xos": {
                            "endpoint": xosEndpoint,
                            "user": xosUser,
                            "password": xosPassword
                        },
                        "publicGateways": [],
                        "nodes" : []
                    }
                }
            }
        }

        # Generate apps->org.onosproject.cordvtn->cordvtn->nodes
        nodes = Node.objects.all()
        for node in nodes:
            nodeip = socket.gethostbyname(node.name)

            try:
                bridgeId = self.get_node_tag(o, node, "bridgeId")
                dataPlaneIntf = self.get_node_tag(o, node, "dataPlaneIntf")
                dataPlaneIp = self.get_node_tag(o, node, "dataPlaneIp")
            except:
                logger.error("not adding node %s to the VTN configuration" % node.name)
                continue

            node_dict = {
                "hostname": node.name,
                "hostManagementIp": "%s/%s" % (nodeip, mgmtSubnetBits),
                "bridgeId": bridgeId,
                "dataPlaneIntf": dataPlaneIntf,
                "dataPlaneIp": dataPlaneIp
            }
            data["apps"]["org.onosproject.cordvtn"]["cordvtn"]["nodes"].append(node_dict)

        # Generate apps->org.onosproject.cordvtn->cordvtn->publicGateways
        # Pull the gateway information from vRouter
        vrouters = VRouterService.get_service_objects().all()
        if vrouters:
            for gateway in vrouters[0].get_gateways():
                gatewayIp = gateway['gateway_ip'].split('/',1)[0]
                gatewayMac = gateway['gateway_mac']
                gateway_dict = {
                    "gatewayIp": gatewayIp,
                    "gatewayMac": gatewayMac
                }
                data["apps"]["org.onosproject.cordvtn"]["cordvtn"]["publicGateways"].append(gateway_dict)

        return json.dumps(data, indent=4, sort_keys=True)

    def get_volt_network_config(self, o, attrs):
        try:
            volt = VOLTService.get_service_objects().all()[0]
        except:
            return None

        devices = []
        for voltdev in volt.volt_devices.all():
            access_devices = []
            for access in voltdev.access_devices.all():
                access_device = {
                    "uplink" : access.uplink,
                    "vlan" : access.vlan
                }
                access_devices.append(access_device)

            if voltdev.access_agent:
                agent = voltdev.access_agent
                olts = {}
                for port_mapping in agent.port_mappings.all():
                    olts[port_mapping.port] = port_mapping.mac
                agent_config = {
                    "olts" : olts,
                    "mac" : agent.mac
                }

            device = {
                voltdev.openflow_id : {
                    "accessDevice" : access_devices,
                    "accessAgent" : agent_config
                },
                "basic" : {
                    "driver" : voltdev.driver
                }
            }
            devices.append(device)

        data = {
            "devices" : devices
        }
        return json.dumps(data, indent=4, sort_keys=True)

    def get_volt_component_config(self, o, attrs):
        data = {
            "org.ciena.onos.ext_notifier.KafkaNotificationBridge":{
                "rabbit.user": "<rabbit_user>",
                "rabbit.password": "<rabbit_password>",
                "rabbit.host": "<rabbit_host>",
                "publish.kafka": "false",
                "publish.rabbit": "true",
                "volt.events.rabbit.topic": "notifications.info",
                "volt.events.rabbit.exchange": "voltlistener",
                "volt.events.opaque.info": "{project_id: <keystone_tenant_id>, user_id: <keystone_user_id>}",
                "publish.volt.events": "true"
            }
        }
        return json.dumps(data, indent=4, sort_keys=True)

    def get_vrouter_network_config(self, o, attrs):
        # From the onosproject wiki:
        # https://wiki.onosproject.org/display/ONOS/vRouter
        data = {
            "devices" : {
                "of:00000000000000b1" : {
                    "basic" : {
                        "driver" : "softrouter"
                    }
                }
            },
            "ports" : {
                "of:00000000000000b1/1" : {
                    "interfaces" : [
                        {
                            "name" : "b1-1",
                            "ips"  : [ "10.0.1.2/24" ],
                            "mac"  : "00:00:00:00:00:01"
                        }
                    ]
                },
                "of:00000000000000b1/2" : {
                    "interfaces" : [
                        {
                            "name" : "b1-2",
                            "ips"  : [ "10.0.2.2/24" ],
                            "mac"  : "00:00:00:00:00:01"
                        }
                    ]
                },
                "of:00000000000000b1/3" : {
                    "interfaces" : [
                        {
                            "name" : "b1-3",
                            "ips"  : [ "10.0.3.2/24" ],
                            "mac"  : "00:00:00:00:00:01"
                        }
                    ]
                },
                "of:00000000000000b1/4" : {
                    "interfaces" : [
                        {
                            "name" : "b1-4",
                            "ips"  : [ "10.0.4.2/24" ],
                            "mac"  : "00:00:00:00:00:02",
                            "vlan" : "100"
                        }
                    ]
                }
            },
            "apps" : {
                "org.onosproject.router" : {
                    "router" : {
                        "controlPlaneConnectPoint" : "of:00000000000000b1/5",
                        "ospfEnabled" : "true",
                        "interfaces" : [ "b1-1", "b1-2", "b1-2", "b1-4" ]
                    }
                }
            }
        }
        return json.dumps(data, indent=4, sort_keys=True)

    def write_configs(self, o):
        o.config_fns = []
        o.rest_configs = []
        o.component_configs = []
        o.files_dir = self.get_files_dir(o)

        if not os.path.exists(o.files_dir):
            os.makedirs(o.files_dir)

        # Combine the service attributes with the tenant attributes. Tenant
        # attribute can override service attributes.
        attrs = o.provider_service.serviceattribute_dict
        attrs.update(o.tenantattribute_dict)

        ordered_attrs = attrs.keys()

        onos = self.get_onos_service(o)
        if onos.node_key:
            file(os.path.join(o.files_dir, "node_key"),"w").write(onos.node_key)
            o.node_key_fn="node_key"
        else:
            o.node_key_fn=None

        o.early_rest_configs=[]
        if ("cordvtn" in o.dependencies) and (not self.is_no_container(o)):
            # For VTN, since it's running in a docker host container, we need
            # to make sure it configures the cluster using the right ip addresses.
            # NOTE: rest_onos/v1/cluster/configuration/ will reboot the cluster and
            #   must go first.
            name="rest_onos/v1/cluster/configuration/"
            value= self.get_cluster_configuration(o)
            fn = name[5:].replace("/","_")
            endpoint = name[5:]
            file(os.path.join(o.files_dir, fn),"w").write(" " +value)
            o.early_rest_configs.append( {"endpoint": endpoint, "fn": fn} )

        # Generate config files and save them to the appropriate tenant attributes
        configs = []
        for key, value in attrs.iteritems():
            if key == "autogenerate" and value:
                for config in value.split(','):
                    configs.append(config.strip())

        for label in configs:
            config = None
            value = None
            if label == "vtn-network-cfg":
                # Generate the VTN config file... where should this live?
                config = "rest_onos/v1/network/configuration/"
                value = self.get_vtn_config(o, attrs)
            elif label == "volt-network-cfg":
                config = "rest_onos/v1/network/configuration/"
                value = self.get_volt_network_config(o, attrs)
            elif label == "volt-component-cfg":
                config = "component_config"
                value = self.get_volt_component_config(o, attrs)
            elif label == "vrouter-network-cfg":
                config = "rest_onos/v1/network/configuration/"
                value = self.get_vrouter_network_config(o, attrs)

            if config:
                tas = TenantAttribute.objects.filter(tenant=o, name=config)
                if tas:
                    ta = tas[0]
                    if ta.value != value:
                        logger.info("updating %s with autogenerated config" % config)
                        ta.value = value
                        ta.save()
                        attrs[config] = value
                else:
                    logger.info("saving autogenerated config %s" % config)
                    ta = TenantAttribute(tenant=o, name=config, value=value)
                    ta.save()
                    attrs[config] = value

        for name in attrs.keys():
            value = attrs[name]
            if name.startswith("config_"):
                fn = name[7:] # .replace("_json",".json")
                o.config_fns.append(fn)
                file(os.path.join(o.files_dir, fn),"w").write(value)
            if name.startswith("rest_"):
                fn = name[5:].replace("/","_")
                endpoint = name[5:]
                # Ansible goes out of it's way to make our life difficult. If
                # 'lookup' sees a file that it thinks contains json, then it'll
                # insist on parsing and return a json object. We just want
                # a string, so prepend a space and then strip the space off
                # later.
                file(os.path.join(o.files_dir, fn),"w").write(" " +value)
                o.rest_configs.append( {"endpoint": endpoint, "fn": fn} )
            if name.startswith("component_config"):
                components = json.loads(value,object_pairs_hook=OrderedDict)
                for component in components.keys():
                    config = components[component]
                    for key in config.keys():
                         config_val = config[key]
                         found = re.findall('<(.+?)>',config_val)
                         for x in found:
                            #Get value corresponding to that string
                            val = self.get_dynamic_parameter_value(o, x)
                            if val:
	                       config_val = re.sub('<'+x+'>', val, config_val)
                            #TODO: else raise an exception?
	                 o.component_configs.append( {"component": component, "config_params": "'{\""+key+"\":\""+config_val+"\"}'"} )

    def prepare_record(self, o):
        self.write_configs(o)

    def get_extra_attributes_common(self, o):
        fields = {}

        # These are attributes that are not dependent on Instance. For example,
        # REST API stuff.

        onos = self.get_onos_service(o)

        fields["files_dir"] = o.files_dir
        fields["appname"] = o.name
        fields["rest_configs"] = o.rest_configs
        fields["rest_hostname"] = onos.rest_hostname
        fields["rest_port"] = onos.rest_port

        if o.dependencies:
            fields["dependencies"] = [x.strip() for x in o.dependencies.split(",")]
        else:
            fields["dependencies"] = []

        return fields

    def get_extra_attributes_full(self, o):
        instance = self.get_instance(o)

        fields = self.get_extra_attributes_common(o)

        fields["config_fns"] = o.config_fns
        fields["early_rest_configs"] = o.early_rest_configs
        fields["component_configs"] = o.component_configs
        fields["node_key_fn"] = o.node_key_fn

        if o.install_dependencies:
            fields["install_dependencies"] = [x.strip() for x in o.install_dependencies.split(",")]
        else:
            fields["install_dependencies"] = []

        if (instance.isolation=="container"):
            fields["ONOS_container"] = "%s-%s" % (instance.slice.name, str(instance.id))
        else:
            fields["ONOS_container"] = "ONOS"
        return fields

    def get_extra_attributes(self, o):
        if self.is_no_container(o):
            return self.get_extra_attributes_common(o)
        else:
            return self.get_extra_attributes_full(o)

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run
        super(SyncONOSApp, self).sync_fields(o, fields)

    def run_playbook(self, o, fields):
        if self.is_no_container(o):
            # There is no machine to SSH to, so use the synchronizer's
            # run_template method directly.
            run_template("sync_onosapp_nocontainer.yaml", fields)
        else:
            super(SyncONOSApp, self).run_playbook(o, fields)

    def delete_record(self, m):
        pass
