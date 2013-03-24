from PLC.Nodes import Nodes

class SliverImporter:

    def __init__(self, importer):
        self.importer = importer
        self.slivers = {}

    def run(self):
        nodes = Nodes(self.importer.api)
        for node in nodes:
            slice_id in node['slice_ids']:
                self.slivers[(slice['slice_id'], node['node_id'])] = slice          

