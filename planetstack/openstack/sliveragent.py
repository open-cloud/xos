import os
import sys
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
import time
from core.models.sliver import Sliver
from openstack.manager import OpenStackManager

class SliverAgent:

    def run(self):
        manager = OpenStackManager()
        # exit if openstack is disable or unavailable
        if not manager.enabled or not manager.has_openstack:
            sys.exit()

        while True :
            # fill in null ip addresses 
            slivers = Sliver.objects.filter(ip=None)
            for sliver in slivers:
                # update connection
                manager.client.connect(username=manager.client.keystone.username,
                               password=manager.client.keystone.password,
                               tenant=sliver.slice.name)  
                sliver.os_manager = manager
                servers = manager.client.nova.servers.findall(id=sliver.instance_id)
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
                 
