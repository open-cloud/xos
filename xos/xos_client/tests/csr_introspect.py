import sys
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: csr_introspect"

    c = xos_grpc_client.coreclient

    for csr in c.xos_orm.CordSubscriberRoot.objects.all():
        print "  csr", csr.id
        for field_name in ["firewall_enable", "firewall_rules", "url_filter_enable", "url_filter_rules", "cdn_enable", "uplink_speed", "downlink_speed", "enable_uverse", "status"]:
            print "    %s: %s" % (field_name, getattr(csr, field_name))

    print "    okay"

xos_grpc_client.start_api_parseargs(test_callback)

