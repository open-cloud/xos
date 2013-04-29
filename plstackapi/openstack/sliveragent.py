import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plstackapi.planetstack.settings")
import time
from plstackapi.core.models.sliver import Sliver
from plstackapi.openstack.client import OpenStackClient    

class SliverAgent:

    def run(self):
        client = OpenStackClient()
        while True:
            # fill in null ip addresses 
            slivers = Sliver.objects.filter(ip=None)
            for sliver in slivers:
                # update connection
                client.connect(username=client.keystone.username,
                               password=client.keystone.password,
                               tenant=sliver.slice.name)  
                servers = client.nova.servers.findall(id=sliver.instance_id)
                if not servers:
                    continue
                server = servers[0]
                ips = server.addresses.get(sliver.slice.name, [])
                if not ips:
                    continue
                sliver.ip = ips[0]['addr']
                sliver.save()
            time.sleep(7)
                
                                        
if __name__ == '__main__':
    SliverAgent().run()
                 
