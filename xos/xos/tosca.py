import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
django.setup()
from core.models import Slice,Sliver,User,Flavor,Node,Image

class XOSNodeSelector(object):
    def __init__(self, user):
        self.user = user

    def get_allowed_nodes(self):
        # TODO: logic to get nodes that the user can use
        nodes = Node.objects.all()
        return nodes

    def get_nodes(self, quantity):
        nodes = self.get_allowed_nodes()
        # TODO: sort the nodes by some useful metric to pick the best one
        return nodes[:quantity]

class XOSTosca(object):
    def __init__(self, tosca_yaml):
        try:
            (tmp_handle, tmp_pathname) = tempfile.mkstemp()
            os.write(tmp_handle, tosca_yaml)
            os.close(tmp_handle)

            self.template = ToscaTemplate(tmp_pathname)
        finally:
            os.remove(tmp_pathname)

        #pdb.set_trace()

    def execute(self, user):
        for nodetemplate in self.template.nodetemplates:
            self.execute_nodetemplate(user, nodetemplate)

    def select_compute_node(self, user, v):
        mem_size = v.get_property_value("mem_size")
        num_cpus = v.get_property_value("num_cpus")
        disk_size = v.get_property_value("disk_size")

        # TODO: pick flavor based on parameters
        flavor = Flavor.objects.get(name="m1.small")

        compute_node = XOSNodeSelector(user).get_nodes(1)[0]

        return (compute_node, flavor)

    def select_image(self, user, v):
        distribution = v.get_property_value("distribution")
        version = v.get_property_value("version")
        type = v.get_property_value("type")
        architecture = v.get_property_value("architecture")

        # TODO: pick image based on parameters

        imgs=Image.objects.filter(name="Ubuntu 14.04 LTS")   # portal
        if imgs:
            return imgs[0]
        return Image.objects.get(name="Ubuntu-14.04-LTS")    # demo

    def execute_nodetemplate(self, user, nodetemplate):
        if (nodetemplate.type != "tosca.nodes.Compute"):
             raise Exception("I Don't know how to deal with %s" % type)

        host=None
        flavor=None
        image=None

        sliceName = None
        artifacts = nodetemplate.entity_tpl.get("artifacts",[])
        for artifact in artifacts:
            if artifact.get("xos_slice", None):
                 sliceName = artifact["xos_slice"]

        if not sliceName:
             raise Exception("No xos_slice artifact for node %s" % nodetemplate.name)

        slice = Slice.objects.filter(name=sliceName)
        if not slice:
             raise Exception("Could not find slice %s" % sliceName)
        slice = slice[0]

        capabilities = nodetemplate.get_capabilities()
        for (k,v) in capabilities.items():
            if (k=="host"):
                (compute_node, flavor) = self.select_compute_node(user, v)
            elif (k=="os"):
                image = self.select_image(user, v)

        if not compute_node:
            raise Exception("Failed to pick a host")
        if not image:
            raise Exception("Failed to pick an image")
        if not flavor:
            raise Exception("Failed to pick a flavor")

        sliver = Sliver(deployment = compute_node.site_deployment.deployment,
                        node = compute_node,
                        flavor = flavor,
                        slice = slice,
                        image = image)
        sliver.caller = user
        sliver.save()


def main():
    sample = """tosca_definitions_version: tosca_simple_yaml_1_0

description: Template for deploying a single server with predefined properties.

topology_template:
  node_templates:
    my_server:
      type: tosca.nodes.Compute
      capabilities:
        # Host container properties
        host:
         properties:
           num_cpus: 1
           disk_size: 10 GB
           mem_size: 4 MB
        # Guest Operating System properties
        os:
          properties:
            # host Operating System image properties
            architecture: x86_64
            type: linux
            distribution: rhel
            version: 6.5
      artifacts:
          - xos_slice: mysite_tosca
            type: tosca.artifacts.Deployment

"""
    u = User.objects.get(email="scott@onlab.us")

    xt = XOSTosca(sample)
    xt.execute(u)

if __name__=="__main__":
    main()


