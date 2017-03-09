import sys
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: vsg_introspect"

    c = xos_grpc_client.coreclient

    for vsg in c.xos_orm.VSGTenant.objects.all():
        print "  vsg", vsg.id
        for field_name in ["wan_container_ip", "wan_container_mac", "wan_container_netbits", "wan_container_gateway_ip", "wan_container_gateway_mac", "wan_vm_ip", "wan_vm_mac"]:
            print "    %s: %s" % (field_name, getattr(vsg, field_name))

    print "    okay"

xos_grpc_client.start_api_parseargs(test_callback)

