import sys
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: vtr_crud"

    c = xos_grpc_client.coreclient

    sr = c.xos_orm.CordSubscriberRoot.objects.first()
    if not sr:
        print "No subscriber roots!"
        return

    vt = c.xos_orm.VTRTenant.objects.new()
    vt.target = sr
    vt.test="ping"
    vt.scope="vm"
    vt.argument="8.8.8.8"
    vt.save()

    assert(vt.id is not None)
    assert(vt.id>0)

    # Check and make sure we can read it back, pay particular attention to
    # the generic foreign key.
    vt2 = c.xos_orm.VTRTenant.objects.get(id=vt.id)
    assert(vt2.target_id == sr.id)
    assert(vt2.target_type_id == sr.self_content_type_id)
    assert("TenantRoot" in vt2.target.class_names)

    vt2.delete()

    # now, make sure it has been deleted
    vt3 = c.xos_orm.VTRTenant.objects.filter(id=vt.id)
    assert(not vt3)

    print "    okay"

xos_grpc_client.start_api_parseargs(test_callback)

