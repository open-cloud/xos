from django.forms import widgets
from rest_framework import serializers
from plstackapi.planetstack.models import *


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Role
        fields = ('id', 
                  'role_id',
                  'role_type')

class SliceSerializer(serializers.HyperlinkedModelSerializer):

    site = serializers.HyperlinkedRelatedField(view_name='site-detail')

    class Meta:
        model = Slice
        fields = ('id',
                  'url',
                  'name',
                  'instantiation',
                  'omf_friendly',
                  'description',
                  'slice_url',
                  'site',
                  'updated',
                  'created')

class SiteSerializer(serializers.HyperlinkedModelSerializer):

    #Experimenting with whether to use ids, hyperlinks, or nested includes
    #slices = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #slices = serializers.RelatedField(many=True, read_only=True)
    #slices = SliceSerializer(many=True)
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='slice-detail')
    deployment_networks = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='sitedeploymentnetwork-detail')

    class Meta:
        model = Site
        fields = ('id',
                  'url',
                  'name',
                  'deployment_networks',
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

class DeploymentNetworkSerializer(serializers.HyperlinkedModelSerializer):

    sites = serializers.HyperlinkedRelatedField(view_name='sitedeploymentnetwork-detail')
    class Meta:
        model = DeploymentNetwork
        fields = ('id',
                  'name',
                  'sites'
                 )

class SiteDeploymentNetworkSerializer(serializers.HyperlinkedModelSerializer):

    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    deploymentNetwork = serializers.HyperlinkedRelatedField(view_name='deploymentnetwork-detail')

    class Meta:
        model = SiteDeploymentNetwork
        fields = ('url',
                 'site',
                 'deploymentNetwork')

class SliverSerializer(serializers.ModelSerializer):
    slice = serializers.RelatedField(read_only=True)
    #slice = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Sliver
        fields = ('id',
                  'slice',
                  'name')

class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = ('id',
                 'name')

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id',
                  'image_id',
                  'name',
                  'disk_format',
                  'container_format')

class FlavorSerializer(serializers.ModelSerializer):

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
                 Site: SiteSerializer,
                 Slice: SliceSerializer,
                 Node: NodeSerializer,
                 Sliver: SliverSerializer,
                 DeploymentNetwork: DeploymentNetworkSerializer,
                 SiteDeploymentNetwork: SiteDeploymentNetworkSerializer,
                 Image: ImageSerializer,
                 Flavor: FlavorSerializer, 
                 None: None,
                }

