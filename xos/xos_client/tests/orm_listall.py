import sys
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: orm_listall_crud"

    c = xos_grpc_client.coreclient

    for model_name in c.xos_orm.all_model_names:
        model_class = getattr(c.xos_orm, model_name)

        try:
            print "   list all %s ..." % model_name,

            objs = model_class.objects.all()

            print "[%d] okay" % len(objs)
        except:
            print "   fail!"
            traceback.print_exc()

    print "    done"

xos_grpc_client.start_api_parseargs(test_callback)

