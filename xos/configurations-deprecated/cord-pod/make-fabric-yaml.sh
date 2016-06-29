FN=$SETUPDIR/fabric.yaml

rm -f $FN

cat >> $FN <<EOF
tosca_definitions_version: tosca_simple_yaml_1_0

imports:
   - custom_types/xos.yaml

description: generate fabric configuration

topology_template:
  node_templates:

    service#ONOS_Fabric:
      type: tosca.nodes.ONOSService
      requirements:
      properties:
          kind: onos
          view_url: /admin/onos/onosservice/\$id$/
          no_container: true
          rest_hostname: onos-fabric
          replaces: service_ONOS_Fabric
          rest_onos/v1/network/configuration/: { get_artifact: [ SELF, fabric_network_cfg_json, LOCAL_FILE ] }
      artifacts:
          fabric_network_cfg_json: /root/setup/cord-fabric-vr.json

    service#fabric:
      type: tosca.nodes.FabricService
      properties:
          view_url: /admin/fabric/fabricservice/\$id\$/
          replaces: service_fabric


EOF

NODES=$( bash -c "source $SETUPDIR/admin-openrc.sh ; nova host-list" |grep compute|awk '{print $2}' )
I=0
for NODE in $NODES; do
    echo $NODE
    cat >> $FN <<EOF
    $NODE:
      type: tosca.nodes.Node

    # Fabric location field for node $NODE
    ${NODE}_location_tag:
      type: tosca.nodes.Tag
      properties:
          name: location
          value: of:0000000000000001/1
      requirements:
          - target:
              node: $NODE
              relationship: tosca.relationships.TagsObject
          - service:
              node: service#ONOS_Fabric
              relationship: tosca.relationships.MemberOfService
EOF
done

cat >> $FN <<EOF
    Fabric_ONOS_app:
      type: tosca.nodes.ONOSApp
      requirements:
          - onos_tenant:
              node: service#ONOS_Fabric
              relationship: tosca.relationships.TenantOfService
          - fabric_service:
              node: service#fabric
              relationship: tosca.relationships.UsedByService
      properties:
          dependencies: org.onosproject.drivers, org.onosproject.openflow-base, org.onosproject.netcfghostprovider, org.onosproject.netcfglinksprovider, org.onosproject.segmentrouting, org.onosproject.vrouter, org.onosproject.hostprovider
EOF
