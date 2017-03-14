import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVRouterApp(ORMWrapper):
    @property
    def interfaces(self):
        app_interfaces = []
        devices = self.stub.VRouterDevice.objects.filter(vrouter_service_id=self.id)
        for device in devices:
            ports = self.stub.VRouterPort.objects.filter(vrouter_device_id=device.id)
            for port in ports:
                interfaces = self.stub.VRouterInterface.objects.filter(vrouter_port_id=port.id)
                for iface in interfaces:
                    app_interfaces.append(iface.name)
        return app_interfaces

register_convenience_wrapper("VRouterApp", ORMWrapperVRouterApp)
