import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,Sliver,User,Flavor,Node,Image
from nodeselect import XOSNodeSelector
from imageselect import XOSImageSelector

class XOSTosca(object):
    def __init__(self, tosca_yaml, parent_dir=None):
        # TOSCA will look for imports using a relative path from where the
        # template file is located, so we have to put the template file
        # in a specific place.
        if not parent_dir:
            parent_dir = os.getcwd()

        try:
            (tmp_handle, tmp_pathname) = tempfile.mkstemp(dir=parent_dir)
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

        compute_node = XOSNodeSelector(user, mem_size=mem_size, num_cpus=num_cpus, disk_size=disk_size).get_nodes(1)[0]

        return (compute_node, flavor)

    def select_image(self, user, v):
        distribution = v.get_property_value("distribution")
        version = v.get_property_value("version")
        type = v.get_property_value("type")
        architecture = v.get_property_value("architecture")

        return XOSImageSelector(user, distribution=distribution, version=version, type=type, architecture=architecture).get_image()

    def execute_nodetemplate(self, user, nodetemplate):
        if (nodetemplate.type == "tosca.nodes.Slice"):
            return

        if (nodetemplate.type == "tosca.nodes.Service"):
            return

        if (nodetemplate.type != "tosca.nodes.Compute"):
            raise Exception("I Don't know how to deal with %s" % nodetemplate.type)

        host=None
        flavor=None
        image=None

        sliceName  = None
        for reqs in nodetemplate.requirements:
            for (k,v) in reqs.items():
                print v
                if (v["relationship"] == "tosca.relationships.MemberOfSlice"):
                    sliceName = v["node"]
        if not sliceName:
             raise Exception("No slice requirement for node %s" % nodetemplate.name)

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
        print "XXX save sliver" #sliver.save()




