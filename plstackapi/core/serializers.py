from django.forms import widgets
from rest_framework import serializers
from plstackapi.core.models import *


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
 
    class Meta:
        model = Role
        fields = ('id', 
                  'role_id',
                  'role_type')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    slice_memberships = serializers.HyperlinkedRelatedField(view_name='slice-membership-detail')
    site_privileges = serializers.HyperlinkedRelatedField(view_name='site-privilege-detail')
    class Meta:
        model = User
        fields = ('id',
                  'user_id', 
                  'firstname', 
                  'lastname',
                  'email', 
                  'phone', 
                  'user_url',
                  'is_admin',
                  'site',
                  'slice_memberships',
                  'site_privileges')
                    
class KeySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    user = serializers.HyperlinkedRelatedField(view_name='user-detail') 
    class Meta:
        model = Key
        fields = ('id',
                  'name',
                  'key',
                  'type',
                  'blacklisted', 
                  'user')


class SliceSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    slivers = serializers.HyperlinkedRelatedField(view_name='sliver-detail')
    subnet= serializers.HyperlinkedRelatedField(view_name='subnet-detail')
    class Meta:
        model = Slice
        fields = ('id',
                  'tenant_id',
                  'enabled',
                  'name',
                  'url',
                  'instantiation',
                  'omf_friendly',
                  'description',
                  'slice_url',
                  'network_id',
                  'router_id',
                  'site',
                  'slivers',
                  'subnet',
                  'updated',
                  'created')

class SliceMembershipSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    slice = serializers.HyperlinkedRelatedField(view_name='slice-detail')
    user = serializers.HyperlinkedRelatedField(view_name='user-detail')
    role = serializers.HyperlinkedRelatedField(view_name='role-detail')
    class Meta:
        model = SitePrivilege
        fields = ('id',
                  'user',
                  'slice',
                  'role')

class SubnetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    slice = serializers.HyperlinkedRelatedField(view_name='slice-detail')
    class Meta:
        model = Subnet
        fields = ('id',
                  'subnet_id',
                  'cidr',
                  'ip_version',
                  'start',
                  'end',
                  'slice')  

class SiteSerializer(serializers.HyperlinkedModelSerializer):

    #Experimenting with whether to use ids, hyperlinks, or nested includes
    #slices = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #slices = serializers.RelatedField(many=True, read_only=True)
    #slices = SliceSerializer(many=True)
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='slice-detail')

    class Meta:
        model = Site
        fields = ('id',
                  'url',
                  'name',
                  'slices',
                  'site_url',
                  'enabled',
                  'longitude',
                  'latitude',
                  'login_base',
                  'tenant_id',
                  'is_public',
                  'abbreviated_name',
                  'updated',
                  'created')

class SitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    user = serializers.HyperlinkedRelatedField(view_name='user-detail')
    role = serializers.HyperlinkedRelatedField(view_name='role-detail')
    class Meta:
        model = SitePrivilege
        fields = ('id',
                  'user',
                  'site',
                  'role')

class DeploymentNetworkSerializer(serializers.HyperlinkedModelSerializer):

    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    sites = serializers.HyperlinkedRelatedField(view_name='deploymentnetwork-detail')
    class Meta:
        model = DeploymentNetwork
        fields = ('id',
                  'name',
                  'sites'
                 )

class SliverSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    flavor = serializers.HyperlinkedRelatedField(view_name='flavor-detail')
    image = serializers.HyperlinkedRelatedField(view_name='image-detail')
    key = serializers.HyperlinkedRelatedField(view_name='key-detail')
    slice = serializers.HyperlinkedRelatedField(view_name='slice-detail')
    deployment_network = serializers.HyperlinkedRelatedField(view_name='deployment_network-detail')
    node = serializers.HyperlinkedRelatedField(view_name='node-detail')
    
    
    #slice = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Sliver
        fields = ('id',
                  'instance_id',
                  'name',
                  'flavor',
                  'image',
                  'key',
                  'slice',
                  'deploymentNetwork',
                  'node')

class NodeSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Node
        fields = ('id',
                 'name')

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Image
        fields = ('id',
                  'image_id',
                  'name',
                  'disk_format',
                  'container_format')

class FlavorSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Flavor
        fields = ('id',
                  'flavor_id',
                  'name',
                  'memory_mb',
                  'disk_gb',
                  'vcpus')

serializerLookUp = { 
                 Role: RoleSerializer,
                 User: UserSerializer,
                 Key: KeySerializer,
                 Site: SiteSerializer,
                 SitePrivilege: SitePrivilegeSerializer,
                 Slice: SliceSerializer,
                 SliceMembership: SliceMembershipSerializer,
                 Subnet: SubnetSerializer,
                 Node: NodeSerializer,
                 Sliver: SliverSerializer,
                 DeploymentNetwork: DeploymentNetworkSerializer,
                 Image: ImageSerializer,
                 Flavor: FlavorSerializer, 
                 None: None,
                }

