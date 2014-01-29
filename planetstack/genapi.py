from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets

"""
	Schema of the generator object:
		all: Set of all Model objects
		all_if(regex): Set of Model objects that match regex
	
	Model object:
		plural: English plural of object name
		camel: CamelCase version of object name
		refs: list of references to other Model objects
		props: list of properties minus refs

	TODO: Deal with subnets
"""

# Based on api_root.py

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
		'serviceattributes': reverse('serviceattribute-list', request=request, format=format),
		'images': reverse('image-list', request=request, format=format),
		'networkparameters': reverse('networkparameter-list', request=request, format=format),
		'sites': reverse('site-list', request=request, format=format),
		'sliceroles': reverse('slicerole-list', request=request, format=format),
		'tags': reverse('tag-list', request=request, format=format),
		'invoices': reverse('invoice-list', request=request, format=format),
		'planetstackroles': reverse('planetstackrole-list', request=request, format=format),
		'sliceprivileges': reverse('sliceprivilege-list', request=request, format=format),
		'networkslivers': reverse('networksliver-list', request=request, format=format),
		'slices': reverse('slice-list', request=request, format=format),
		'networks': reverse('network-list', request=request, format=format),
		'services': reverse('service-list', request=request, format=format),
		'serviceclasses': reverse('serviceclass-list', request=request, format=format),
		'siteroles': reverse('siterole-list', request=request, format=format),
		'charges': reverse('charge-list', request=request, format=format),
		'roles': reverse('role-list', request=request, format=format),
		'usableobjects': reverse('usableobject-list', request=request, format=format),
		'slivers': reverse('sliver-list', request=request, format=format),
		'nodes': reverse('node-list', request=request, format=format),
		'reservedresources': reverse('reservedresource-list', request=request, format=format),
		'payments': reverse('payment-list', request=request, format=format),
		'networkslices': reverse('networkslice-list', request=request, format=format),
		'planetstackprivileges': reverse('planetstackprivilege-list', request=request, format=format),
		'users': reverse('user-list', request=request, format=format),
		'deployments': reverse('deployment-list', request=request, format=format),
		'reservations': reverse('reservation-list', request=request, format=format),
		'siteprivileges': reverse('siteprivilege-list', request=request, format=format),
		'planetstacks': reverse('planetstack-list', request=request, format=format),
		'accounts': reverse('account-list', request=request, format=format),
		'networkparametertypes': reverse('networkparametertype-list', request=request, format=format),
		'sitedeploymentses': reverse('sitedeployments-list', request=request, format=format),
		'deploymentprivileges': reverse('deploymentprivilege-list', request=request, format=format),
		'deploymentroles': reverse('deploymentrole-list', request=request, format=format),
		'projects': reverse('project-list', request=request, format=format),
		'slicetags': reverse('slicetag-list', request=request, format=format),
		'networktemplates': reverse('networktemplate-list', request=request, format=format),
		'routers': reverse('router-list', request=request, format=format),
		'serviceresources': reverse('serviceresource-list', request=request, format=format),
		
    })

# Based on serializers.py



class ServiceAttributeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	service = serializers.HyperlinkedRelatedField(read_only=True, view_name='service-detail')
	
	
	class Meta:
		model = ServiceAttribute
		fields = ('id','created','updated','enacted','name','value',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Image
		fields = ('id','created','updated','enacted','image_id','name','disk_format','container_format',)


class NetworkParameterSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkParameter
		fields = ('id','created','updated','enacted','parameter','value','content_type','object_id',)


class SiteSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Site
		fields = ('id','created','updated','enacted','tenant_id','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)


class SliceRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SliceRole
		fields = ('id','created','updated','enacted','role',)


class TagSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	service = serializers.HyperlinkedRelatedField(read_only=True, view_name='service-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
	
	
	
	nodes = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='node-detail')
	
	
	class Meta:
		model = Tag
		fields = ('id','created','updated','enacted','name','value','content_type','object_id',)


class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(read_only=True, view_name='account-detail')
	
	
	class Meta:
		model = Invoice
		fields = ('id','created','updated','enacted','date',)


class PlanetStackRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = PlanetStackRole
		fields = ('id','created','updated','enacted','role',)


class SlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
	
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = SlicePrivilege
		fields = ('id','created','updated','enacted',)


class NetworkSliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	network = serializers.HyperlinkedRelatedField(read_only=True, view_name='network-detail')
	
	
	
	sliver = serializers.HyperlinkedRelatedField(read_only=True, view_name='sliver-detail')
	
	
	class Meta:
		model = NetworkSliver
		fields = ('id','created','updated','enacted','ip','port_id',)


class SliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	
	service = serializers.HyperlinkedRelatedField(read_only=True, view_name='service-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	class Meta:
		model = Slice
		fields = ('id','created','updated','enacted','tenant_id','name','enabled','omf_friendly','description','slice_url','network_id','router_id','subnet_id','serviceClass','creator',)


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	class Meta:
		model = Network
		fields = ('id','created','updated','enacted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','network_id','router_id','subnet_id',)


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Service
		fields = ('id','created','updated','enacted','description','enabled','name','versionNumber','published',)


class ServiceClassSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = ServiceClass
		fields = ('id','created','updated','enacted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)


class SiteRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SiteRole
		fields = ('id','created','updated','enacted','role',)


class ChargeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(read_only=True, view_name='account-detail')
	
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	
	invoice = serializers.HyperlinkedRelatedField(read_only=True, view_name='invoice-detail')
	
	
	class Meta:
		model = Charge
		fields = ('id','created','updated','enacted','kind','state','date','object','amount','coreHours',)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Role
		fields = ('id','created','updated','enacted','role_type','role','description','content_type',)


class UsableObjectSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = UsableObject
		fields = ('id','created','updated','enacted','name',)


class SliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	image = serializers.HyperlinkedRelatedField(read_only=True, view_name='image-detail')
	
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	
	node = serializers.HyperlinkedRelatedField(read_only=True, view_name='node-detail')
	
	
	class Meta:
		model = Sliver
		fields = ('id','created','updated','enacted','instance_id','name','instance_name','ip','creator','deploymentNetwork','numberCores',)


class NodeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(read_only=True, view_name='deployment-detail')
	
	
	class Meta:
		model = Node
		fields = ('id','created','updated','enacted','name',)


class ReservedResourceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sliver = serializers.HyperlinkedRelatedField(read_only=True, view_name='sliver-detail')
	
	
	class Meta:
		model = ReservedResource
		fields = ('id','created','updated','enacted','resource','quantity','reservationSet',)


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(read_only=True, view_name='account-detail')
	
	
	class Meta:
		model = Payment
		fields = ('id','created','updated','enacted','amount','date',)


class NetworkSliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	network = serializers.HyperlinkedRelatedField(read_only=True, view_name='network-detail')
	
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = NetworkSlice
		fields = ('id','created','updated','enacted',)


class PlanetStackPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
	
	
	
	planetstack = serializers.HyperlinkedRelatedField(read_only=True, view_name='planetstack-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = PlanetStackPrivilege
		fields = ('id','created','updated','enacted',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = User
		fields = ('id','password','last_login','email','username','kuser_id','firstname','lastname','phone','user_url','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','timezone',)


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = Deployment
		fields = ('id','created','updated','enacted','name',)


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = Reservation
		fields = ('id','created','updated','enacted','startTime','duration',)


class SitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
	
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = SitePrivilege
		fields = ('id','created','updated','enacted',)


class PlanetStackSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = PlanetStack
		fields = ('id','created','updated','enacted','description',)


class AccountSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = Account
		fields = ('id','created','updated','enacted',)


class NetworkParameterTypeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkParameterType
		fields = ('id','created','updated','enacted','name','description',)


class SiteDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	site = serializers.HyperlinkedRelatedField(read_only=True, view_name='site-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(read_only=True, view_name='deployment-detail')
	
	
	class Meta:
		model = SiteDeployments
		fields = ('id','created','updated','enacted',)


class DeploymentPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(read_only=True, view_name='deployment-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = DeploymentPrivilege
		fields = ('id','created','updated','enacted',)


class DeploymentRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = DeploymentRole
		fields = ('id','created','updated','enacted','role',)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Project
		fields = ('id','created','updated','enacted','name',)


class SliceTagSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	slice = serializers.HyperlinkedRelatedField(read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = SliceTag
		fields = ('id','created','updated','enacted','name','value',)


class NetworkTemplateSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkTemplate
		fields = ('id','created','updated','enacted','name','description','guaranteedBandwidth','visibility','translation','sharedNetworkName','sharedNetworkId',)


class RouterSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Router
		fields = ('id','created','updated','enacted','name','owner',)


class ServiceResourceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = ServiceResource
		fields = ('id','created','updated','enacted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)


serializerLookUp = { 

                 ServiceAttribute: ServiceAttributeSerializer,

                 Image: ImageSerializer,

                 NetworkParameter: NetworkParameterSerializer,

                 Site: SiteSerializer,

                 SliceRole: SliceRoleSerializer,

                 Tag: TagSerializer,

                 Invoice: InvoiceSerializer,

                 PlanetStackRole: PlanetStackRoleSerializer,

                 SlicePrivilege: SlicePrivilegeSerializer,

                 NetworkSliver: NetworkSliverSerializer,

                 Slice: SliceSerializer,

                 Network: NetworkSerializer,

                 Service: ServiceSerializer,

                 ServiceClass: ServiceClassSerializer,

                 SiteRole: SiteRoleSerializer,

                 Charge: ChargeSerializer,

                 Role: RoleSerializer,

                 UsableObject: UsableObjectSerializer,

                 Sliver: SliverSerializer,

                 Node: NodeSerializer,

                 ReservedResource: ReservedResourceSerializer,

                 Payment: PaymentSerializer,

                 NetworkSlice: NetworkSliceSerializer,

                 PlanetStackPrivilege: PlanetStackPrivilegeSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 Reservation: ReservationSerializer,

                 SitePrivilege: SitePrivilegeSerializer,

                 PlanetStack: PlanetStackSerializer,

                 Account: AccountSerializer,

                 NetworkParameterType: NetworkParameterTypeSerializer,

                 SiteDeployments: SiteDeploymentsSerializer,

                 DeploymentPrivilege: DeploymentPrivilegeSerializer,

                 DeploymentRole: DeploymentRoleSerializer,

                 Project: ProjectSerializer,

                 SliceTag: SliceTagSerializer,

                 NetworkTemplate: NetworkTemplateSerializer,

                 Router: RouterSerializer,

                 ServiceResource: ServiceResourceSerializer,

                 None: None,
                }

# Based on core/views/*.py


class ServiceAttributeList(generics.ListCreateAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer

class ServiceAttributeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer



class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer



class NetworkParameterList(generics.ListCreateAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer

class NetworkParameterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer



class SiteList(generics.ListCreateAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer

class SiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer



class SliceRoleList(generics.ListCreateAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer

class SliceRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer



class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer



class InvoiceList(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer

class InvoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer



class PlanetStackRoleList(generics.ListCreateAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer

class PlanetStackRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer



class SlicePrivilegeList(generics.ListCreateAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer

class SlicePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer



class NetworkSliverList(generics.ListCreateAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer

class NetworkSliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer



class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer

class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer



class NetworkList(generics.ListCreateAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer

class NetworkDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer



class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer



class ServiceClassList(generics.ListCreateAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer

class ServiceClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer



class SiteRoleList(generics.ListCreateAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer

class SiteRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer



class ChargeList(generics.ListCreateAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer

class ChargeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer



class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer



class UsableObjectList(generics.ListCreateAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer

class UsableObjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer



class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer



class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer

class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer



class ReservedResourceList(generics.ListCreateAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer

class ReservedResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer



class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer



class NetworkSliceList(generics.ListCreateAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer

class NetworkSliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer



class PlanetStackPrivilegeList(generics.ListCreateAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer

class PlanetStackPrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer



class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer

class DeploymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer



class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer

class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer



class SitePrivilegeList(generics.ListCreateAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer

class SitePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer



class PlanetStackList(generics.ListCreateAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer

class PlanetStackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer



class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer

class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer



class NetworkParameterTypeList(generics.ListCreateAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer

class NetworkParameterTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer



class SiteDeploymentsList(generics.ListCreateAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer

class SiteDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer



class DeploymentPrivilegeList(generics.ListCreateAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer

class DeploymentPrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer



class DeploymentRoleList(generics.ListCreateAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer

class DeploymentRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer



class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer



class SliceTagList(generics.ListCreateAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer

class SliceTagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer



class NetworkTemplateList(generics.ListCreateAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer

class NetworkTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer



class RouterList(generics.ListCreateAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer

class RouterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer



class ServiceResourceList(generics.ListCreateAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer

class ServiceResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer



