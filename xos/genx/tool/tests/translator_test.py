from xproto_test_base import *
import yaml

# Generate other formats from xproto
class XProtoTranslatorTest(XProtoTest):
    def test_proto_generator(self):
        xproto = \
"""
message VRouterPort (XOSBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
	target = \
"""
{% for m in proto.messages %}
message {{ m.name }} {
  option bases = "{{ m.bases | map(attribute='name') | join(",") }}";
  {%- for f in m.fields %}
  {{ f.modifier }} {{f.type}} {{f.name}} = {{ f.id }}{% if f.options %} [{% for k,v in f.options.iteritems() %} {{ k }} = "{{ xproto_unquote(v)}}"{% if not loop.last %},{% endif %} {% endfor %}]{% endif %};
  {%- endfor %}
}
{% endfor %}
"""

        self.generate(xproto = xproto, target = target)
        self.generate(xproto = self.get_output(), target = "{{ proto }}")
	output = self.get_output()
        self.assertIn("VRouterService", output)
    
    def test_yaml_generator(self):
        xproto = \
"""
option app_name = "test";

message Port (PlCoreBase,ParameterMixin){
     required manytoone network->Network:links = 1 [db_index = True, null = False, blank = False];
     optional manytoone instance->Instance:ports = 2 [db_index = True, null = True, blank = True];
     optional string ip = 3 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False];
     optional string port_id = 4 [help_text = "Neutron port id", max_length = 256, null = True, db_index = False, blank = True];
     optional string mac = 5 [help_text = "MAC address associated with this port", max_length = 256, null = True, db_index = False, blank = True];
     required bool xos_created = 6 [default = False, null = False, db_index = False, blank = True];
}

message Instance (PlCoreBase){
     optional string instance_id = 1 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance id", null = True, db_index = False];
     optional string instance_uuid = 2 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance uuid", null = True, db_index = False];
     required string name = 3 [max_length = 200, content_type = "stripped", blank = False, help_text = "Instance name", null = False, db_index = False];
     optional string instance_name = 4 [max_length = 200, content_type = "stripped", blank = True, help_text = "OpenStack generated name", null = True, db_index = False];
     optional string ip = 5 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False];
     required manytoone image->Image:instances = 6 [db_index = True, null = False, blank = False];
     optional manytoone creator->User:instances = 7 [db_index = True, null = True, blank = True];
     required manytoone slice->Slice:instances = 8 [db_index = True, null = False, blank = False];
     required manytoone deployment->Deployment:instance_deployment = 9 [db_index = True, null = False, blank = False];
     required manytoone node->Node:instances = 10 [db_index = True, null = False, blank = False];
     required int32 numberCores = 11 [help_text = "Number of cores for instance", default = 0, null = False, db_index = False, blank = False];
     required manytoone flavor->Flavor:instance = 12 [help_text = "Flavor of this instance", default = "get_default_flavor()", null = False, db_index = True, blank = False];
     optional string userData = 13 [help_text = "user_data passed to instance during creation", null = True, db_index = False, blank = True];
     required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
     optional string volumes = 15 [help_text = "Comma-separated list of directories to expose to parent context", null = True, db_index = False, blank = True];
     optional manytoone parent->Instance:instance = 16 [help_text = "Parent Instance for containers nested inside of VMs", null = True, db_index = True, blank = True];
     required manytomany tags->Tag = 17 [db_index = False, null = False, blank = True];
}

message Network (PlCoreBase,ParameterMixin) {
     required string name = 1 [db_index = False, max_length = 32, null = False, blank = False];
     required manytoone template->NetworkTemplate:network = 2 [db_index = True, null = False, blank = False];
     required string subnet = 3 [db_index = False, max_length = 32, null = False, blank = True];
     required string start_ip = 4 [db_index = False, max_length = 32, null = False, blank = True];
     required string end_ip = 5 [db_index = False, max_length = 32, null = False, blank = True];
     optional string ports = 6 [db_index = False, max_length = 1024, null = True, blank = True];
     optional string labels = 7 [db_index = False, max_length = 1024, null = True, blank = True];
     required manytoone owner->Slice:ownedNetworks = 8 [help_text = "Slice that owns control of this Network", null = False, db_index = True, blank = False];
     required int32 guaranteed_bandwidth = 9 [default = 0, null = False, db_index = False, blank = False];
     required bool permit_all_slices = 10 [default = False, null = False, db_index = False, blank = True];
     optional string topology_parameters = 11 [db_index = False, null = True, blank = True];
     optional string controller_url = 12 [db_index = False, max_length = 1024, null = True, blank = True];
     optional string controller_parameters = 13 [db_index = False, null = True, blank = True];
     optional string network_id = 14 [help_text = "Quantum network", max_length = 256, null = True, db_index = False, blank = True];
     optional string router_id = 15 [help_text = "Quantum router id", max_length = 256, null = True, db_index = False, blank = True];
     optional string subnet_id = 16 [help_text = "Quantum subnet id", max_length = 256, null = True, db_index = False, blank = True];
     required bool autoconnect = 17 [help_text = "This network can be autoconnected to the slice that owns it", default = True, null = False, db_index = False, blank = True];
     required manytomany permitted_slices->Slice/Network_permitted_slices:availableNetworks = 18 [db_index = False, null = False, blank = True];
     required manytomany slices->Slice/NetworkSlice:networks = 19 [db_index = False, null = False, blank = True];
     required manytomany instances->Instance/Port:networks = 20 [db_index = False, null = False, blank = True];
}

message Slice (PlCoreBase){
     required string name = 1 [max_length = 80, content_type = "stripped", blank = False, help_text = "The Name of the Slice", null = False, db_index = False];
     required bool enabled = 2 [help_text = "Status for this Slice", default = True, null = False, db_index = False, blank = True];
     required bool omf_friendly = 3 [default = False, null = False, db_index = False, blank = True];
     required string description = 4 [help_text = "High level description of the slice and expected activities", max_length = 1024, null = False, db_index = False, blank = True];
     required string slice_url = 5 [db_index = False, max_length = 512, null = False, content_type = "url", blank = True];
     required manytoone site->Site:slices = 6 [help_text = "The Site this Slice belongs to", null = False, db_index = True, blank = False];
     required int32 max_instances = 7 [default = 10, null = False, db_index = False, blank = False];
     optional manytoone service->Service:slices = 8 [db_index = True, null = True, blank = True];
     optional string network = 9 [blank = True, max_length = 256, null = True, db_index = False, choices = "((None, 'Default'), ('host', 'Host'), ('bridged', 'Bridged'), ('noauto', 'No Automatic Networks'))"];
     optional string exposed_ports = 10 [db_index = False, max_length = 256, null = True, blank = True];
     optional manytoone serviceClass->ServiceClass:slices = 11 [db_index = True, null = True, blank = True];
     optional manytoone creator->User:slices = 12 [db_index = True, null = True, blank = True];
     optional manytoone default_flavor->Flavor:slices = 13 [db_index = True, null = True, blank = True];
     optional manytoone default_image->Image:slices = 14 [db_index = True, null = True, blank = True];
     optional manytoone default_node->Node:slices = 15 [db_index = True, null = True, blank = True];
     optional string mount_data_sets = 16 [default = "GenBank", max_length = 256, content_type = "stripped", blank = True, null = True, db_index = False];
     required string default_isolation = 17 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
     required manytomany tags->Tag = 18 [db_index = False, null = False, blank = True];
}
"""

        # Update this to the contents of modeldefs.xtarget
        target = \
"""
items:
{%- for m in proto.messages | sort(attribute='name') %}
{%- if m.name != 'XOSBase' %}
- app: {{ xproto_unquote(xproto_first_non_empty([m.options.app_name, context.app_name, options.app_name])) }}
  fields: 
  {%- set id_field = {'type':'int32', 'name':'id', 'options':{}} %}
  {% for f in (xproto_base_fields(m, proto.message_table) + m.fields + [id_field]) | sort(attribute='name') -%}
  {% if not f.link or f.options.link_type != 'manytomany' -%}
  - hint: {% if f.options.help_text %}{{ xproto_unquote(f.options.help_text) }}{% else %}''{% endif %}
    {% if not f.link -%}
    name: {{ f.name }}
    {%- else -%}
    name: {{ f.name }}_id
    relation: {model: {{ f.options.model }}, type: {{ f.options.link_type }}}
    {% endif %}
    type: {{ xproto_type_to_ui_type(f) }}
    {% set validators = xproto_validators(f) -%}
    {% if validators -%}
    validators:
    {% for v in validators | sort(attribute='name',reverse=True) -%}
    - {{ v | yaml }}
    {% endfor %}
    {% else -%}
    validators: []
    {% endif %}
  {% endif -%}
  {% endfor %}
  name: {{ m.name }}  
  {%- set goodlinks = xproto_links_to_modeldef_relations( xproto_base_links(m, proto.message_table) + m.links ) %}
  {% if goodlinks %}
  relations:
  {{ goodlinks | join('\n') | indent(width=2)}}
  {%- else %}
  relations: []
  {%- endif %}
{%- endif %}
{% endfor -%} 
"""

        self.generate(xproto = xproto, target = target)
	output = self.get_output()
        yaml_ir = yaml.load(output)
        self.assertEqual(len(yaml_ir['items']), 4)

if __name__ == '__main__':
    unittest.main()


