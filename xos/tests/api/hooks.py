import dredd_hooks as hooks
import sys

# HELPERS
from helpers import subscriber

restoreSubscriber = "sudo docker exec teststandalone_xos_1_db psql -U postgres -d xos -c \"UPDATE core_tenantroot SET deleted=false WHERE id=1;\""

@hooks.before_each
def my_before_each_hook(transaction):
    # print('before each restore', transaction['name'])
    # commands.getstatusoutput(restoreSubscriber)
    Subs.createTestSubscriber()
    sys.stdout.flush()


@hooks.before("Truckroll > Truckroll Collection > Create a Truckroll")
def skip_test1(transaction):
    transaction['skip'] = True


@hooks.before("Truckroll > Truckroll Detail > View a Truckroll Detail")
def skip_test2(transaction):
    transaction['skip'] = True


@hooks.before("Truckroll > Truckroll Detail > Delete a Truckroll Detail")
def skip_test3(transaction):
    transaction['skip'] = True


@hooks.before("vOLT > vOLT Collection > Create a vOLT")
def skip_test4(transaction):
    transaction['skip'] = True
