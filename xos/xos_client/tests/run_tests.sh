#! /bin/bash

# Run the tests from the head-node against an xos-client VM

PW=`cat /opt/cord/build/platform-install/credentials/xosadmin@opencord.org`

docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/orm_user_crud.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/orm_listall.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/vtr_crud.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/vsg_introspect.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/csr_introspect.py -u xosadmin@opencord.org -p $PW -qq