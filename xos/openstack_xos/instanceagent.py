import os
import sys
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import time
from core.models.instance import Instance
from openstack.manager import OpenStackManager

class InstanceAgent:

    def run(self):
        manager = OpenStackManager()
        # exit if openstack is disable or unavailable
        if not manager.enabled or not manager.has_openstack:
            sys.exit()

        while True :
            # fill in null ip addresses 
            instances = Instance.objects.filter(ip=None)
            for instance in instances:
                # update connection
                manager.client.connect(username=manager.client.keystone.username,
                               password=manager.client.keystone.password,
                               tenant=instance.slice.name)  
                instance.os_manager = manager
                servers = manager.client.nova.servers.findall(id=instance.instance_id)
                if not servers:
                    continue
                server = servers[0]
                ips = server.addresses.get(instance.slice.name, [])
                if not ips:
                    continue
                instance.ip = ips[0]['addr']
                instance.save()
            time.sleep(7)
                
                                        
if __name__ == '__main__':
    InstanceAgent().run()
                 
