from django.forms import widgets
from rest_framework import serializers
from core.models import *


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):

    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    sites = serializers.HyperlinkedRelatedField(view_name='site-detail')
    class Meta:
        model = Deployment
        fields = ('id',
                  'url',
                  'name',
                  'sites'
                 )

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Image
        fields = ('id',
                  'url',
                  'image_id',
                  'name',
                  'disk_format',
                  'container_format')

class NodeSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Node
        fields = ('id',
                 'url',
                 'name')

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Project
        fields = ('id',
                 'url',
                 'name')

class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Reservation
        fields = ('id',
                 'url',
                 'startTime',
                 'slice',
                 'duration',
                 'endTime',
                 )

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = Role
        fields = ('id', 
                 'url',
                 'role',
                 'role_type')


class ServiceClassSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    class Meta:
        model = ServiceClass
        fields = ('id',
                 'url',
                 'name',
                 'description',
                 'commitment',
                 'membershipFee',
                 'membershipFeeMonths',
                 'upgradeRequiresApproval',
                 'upgradeFrom',
                 )

class ServiceResourceSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    serviceClass = serializers.HyperlinkedRelatedField(view_name='serviceclass-detail')
    class Meta:
        model = ServiceResource
        fields = ('id',
                 'url',
                 'name',
                 'serviceClass',
                 'maxUnitsDeployment',
                 'maxUnitsNode',
                 'maxDuration',
                 'bucketInRate',
                 'bucketMaxSize',
                 'cost',
                 'calendarReservable',
                 )

class SliceSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    instances = serializers.HyperlinkedRelatedField(view_name='instance-detail')
    class Meta:
        model = Slice
        fields = ('id',
                  'url',
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
                  'imagePreference',
		  'network',
		  'mountDataSets',
                  'site',
                  'instances',
                  'updated',
                  'created')

class SlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    slice = serializers.HyperlinkedRelatedField(view_name='slice-detail')
    user = serializers.HyperlinkedRelatedField(view_name='user-detail')
    role = serializers.HyperlinkedRelatedField(view_name='role-detail')
    class Meta:
        model = SlicePrivilege
        fields = ('id',
                  'url',
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
                  'url',
                  'user',
                  'site',
                  'role')

class InstanceSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    image = serializers.HyperlinkedRelatedField(view_name='image-detail')
    slice = serializers.HyperlinkedRelatedField(view_name='slice-detail')
    deploymentNetwork = serializers.HyperlinkedRelatedField(view_name='deployment-detail')
    node = serializers.HyperlinkedRelatedField(view_name='node-detail')
    
    #slice = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Instance
        fields = ('id',
                  'url',
                  'instance_id',
                  'name',
                  'instance_name',
                  'ip',
                  'image',
                  'slice',
                  'deploymentNetwork',
                  'node')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    site = serializers.HyperlinkedRelatedField(view_name='site-detail')
    slice_privileges = serializers.HyperlinkedRelatedField(view_name='sliceprivilege-detail')
    site_privileges = serializers.HyperlinkedRelatedField(view_name='siteprivilege-detail')
    class Meta:
        model = User
        fields = ('id',
                  'url',
                  'kuser_id', 
                  'firstname', 
                  'lastname',
                  'email', 
                  'password',
                  'phone',
                  'public_key', 
                  'user_url',
                  'is_admin',
                  'slice_privileges',
                  'site_privileges')
                    
class TagSerializer(serializers.HyperlinkedModelSerializer):
    # HyperlinkedModelSerializer doesn't include the id by default
    id = serializers.Field()
    project = serializers.HyperlinkedRelatedField(view_name='project-detail')
    #content_type = serializers.PrimaryKeyRelatedField(read_only=True)
    content_type = serializers.RelatedField(source = "content_type")
    content_object = serializers.RelatedField(source='content_object')
    class Meta:
        model = Tag
        fields = ('id', 
                  'url',
                  'project',
                  'value',
                  'content_type',
                  'object_id',
                  'content_object',
                  'name')

serializerLookUp = { 
                 Deployment: DeploymentSerializer,
                 Image: ImageSerializer,
                 Node: NodeSerializer,
                 Project: ProjectSerializer,
                 Reservation: ReservationSerializer,
                 Role: RoleSerializer,
                 ServiceClass: ServiceClassSerializer,
                 ServiceResource: ServiceResourceSerializer,
                 Site: SiteSerializer,
                 SitePrivilege: SitePrivilegeSerializer,
                 Slice: SliceSerializer,
                 SlicePrivilege: SlicePrivilegeSerializer,
                 Instance: InstanceSerializer,
                 Tag: TagSerializer,
                 User: UserSerializer,
                 None: None,
                }

