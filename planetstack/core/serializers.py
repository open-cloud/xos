from django.forms import widgets
from rest_framework import serializers
from core.models import *


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Role
        fields = ('id', 
                  'role_id',
                  'role',
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
                  'kuser_id', 
                  'firstname', 
                  'lastname',
                  'email', 
                  'password',
                  'phone',
                  'public_key', 
                  'user_url',
                  'is_admin',
                  'site',
                  'slice_memberships',
                  'site_privileges')
                    
class SliceSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    slivers = serializers.HyperlinkedRelatedField(view_name='sliver-detail')
    class Meta:
        model = Slice
        fields = ('id',
                  'tenant_id',
                  'enabled',
                  'name',
                  'url',
                  'omf_friendly',
                  'description',
                  'slice_url',
                  'network_id',
                  'router_id',
                  'subnet_id',
                  'site',
                  'slivers',
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

class DeploymentSerializer(serializers.HyperlinkedModelSerializer):

    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    sites = serializers.HyperlinkedRelatedField(view_name='deploymentnetwork-detail')
    class Meta:
        model = Deployment
        fields = ('id',
                  'name',
                  'sites'
                 )

class SliverSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
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
                  'instance_name',
                  'ip',
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

serializerLookUp = { 
                 Role: RoleSerializer,
                 User: UserSerializer,
                 Site: SiteSerializer,
                 SitePrivilege: SitePrivilegeSerializer,
                 Slice: SliceSerializer,
                 SliceMembership: SliceMembershipSerializer,
                 Node: NodeSerializer,
                 Sliver: SliverSerializer,
                 Deployment: DeploymentSerializer,
                 Image: ImageSerializer,
                 None: None,
                }

