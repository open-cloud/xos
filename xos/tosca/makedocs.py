import jinja2
import os
import sys
import yaml
import pdb

# add the parent directory to sys.path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

"""
{'derived_from': 'tosca.nodes.Root', 'capabilities': {'scalable': {'type': 'tosca.capabilities.Scalable'},
'service': {'type': 'tosca.capabilities.xos.Service'}}, 'properties': {'icon_url': {'required': False,
'type': 'string'}, 'public_key': {'required': False, 'type': 'string'}, 'kind': {'default': 'generic',
'type': 'string'}, 'published': {'default': True, 'type': 'boolean'}, 'view_url': {'required': False, 'type': 'string'}, 'enabled': {'default': True, 'type': 'boolean'}, 'versionNumber': {'required': False, 'type': 'string'}}}
"""

class ToscaDocumenter(object):
    def __init__(self, fn="./custom_types/xos.yaml", templatedir="./doctemplates/html", templatename="toscadoctemplate.html", destfn="tosca_reference.html"):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(templatedir))

        self.node_types = {}
        self.root_types = yaml.load(file("definitions/TOSCA_definition_1_0.yaml").read())
        for x in self.root_types.keys():
            if x in ["tosca.nodes.Compute", "tosca.nodes.network.Network"]:
                self.node_types[x] = self.root_types[x]

        self.custom_types = yaml.load(file(fn).read())
        self.node_types.update(self.custom_types.get("node_types"))

        self.destfn = destfn
        self.templatename = templatename

    def run(self):
        node_types=[]
        for k in sorted(self.node_types.keys()):
            nt = self.node_types[k]
            nt["node_type_name"] = k

            derived_from = nt.get("derived_from","")

            if derived_from.startswith("tosca.nodes"):
                nt["node_type_kind"] = "node"
            elif derived_from.startswith("tosca.capabilities"):
                nt["node_type_kind"] = "capability"
            elif derived_from.startswith("tosca.relationships"):
                nt["node_type_kind"] = "relationship"

            node_types.append(nt)

        template = self.env.get_template(self.templatename)

        self.destf = open(self.destfn,"w")
        self.destf.write(template.render(node_types=node_types))

def main():
    ToscaDocumenter().run()

if __name__=="__main__":
    main()
