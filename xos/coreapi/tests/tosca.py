import random
import string
import sys
sys.path.append("..")

import grpc_client
from testconfig import *

SLICE_NAME="mysite_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

TOSCA_RECIPE="""tosca_definitions_version: tosca_simple_yaml_1_0

description: Just some test...

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    mysite:
      type: tosca.nodes.Site

    %s:
      type: tosca.nodes.Slice
      requirements:
          - slice:
                node: mysite
                relationship: tosca.relationships.MemberOfSite
""" % SLICE_NAME

print "tosca_test"

c=grpc_client.SecureClient("xos-core.cord.lab", username=USERNAME, password=PASSWORD)
request=grpc_client.ToscaRequest()
request.recipe = TOSCA_RECIPE

print "Execute"

response=c.utility.RunTosca(request)

if response.status == response.SUCCESS:
    print "  success"
else:
    print "  failure"

for line in response.messages.split("\n"):
    print "    %s" % line

print "Destroy"

response = c.utility.DestroyTosca(request)

if response.status == response.SUCCESS:
    print "  success"
else:
    print "  failure"

for line in response.messages.split("\n"):
    print "    %s" % line

print "Done"
