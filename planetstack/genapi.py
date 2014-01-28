from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
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
		'sliceprivileges': reverse('sliceprivilege-list', request=request, format=format),
		'planetstackroles': reverse('planetstackrole-list', request=request, format=format),
		'networkslivers': reverse('networksliver-list', request=request, format=format),
		'projects': reverse('project-list', request=request, format=format),
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
		'singletonmodels': reverse('singletonmodel-list', request=request, format=format),
		'planetstacks': reverse('planetstack-list', request=request, format=format),
		'accounts': reverse('account-list', request=request, format=format),
		'networkparametertypes': reverse('networkparametertype-list', request=request, format=format),
		'sitedeploymentses': reverse('sitedeployments-list', request=request, format=format),
		'deploymentprivileges': reverse('deploymentprivilege-list', request=request, format=format),
		'deploymentroles': reverse('deploymentrole-list', request=request, format=format),
		'plcorebases': reverse('plcorebase-list', request=request, format=format),
		'slicetags': reverse('slicetag-list', request=request, format=format),
		'networktemplates': reverse('networktemplate-list', request=request, format=format),
		'routers': reverse('router-list', request=request, format=format),
		'serviceresources': reverse('serviceresource-list', request=request, format=format),
		
    })

# Based on serializers.py



class ServiceattributeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	service = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='service-detail')
	
	
	class Meta:
		model = serviceattribute
		fields = ('id','created','updated','enacted','name','value',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = image
		fields = ('id','created','updated','enacted','image_id','name','disk_format','container_format',)


class NetworkparameterSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = networkparameter
		fields = ('id','created','updated','enacted','parameter','value','content_type','object_id',)


class SiteSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = site
		fields = ('id','created','updated','enacted','tenant_id','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)


class SliceroleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = slicerole
		fields = ('id','created','updated','enacted','role',)


class TagSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	service = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='service-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
	
	
	
	nodes = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='node-detail')
	
	
	class Meta:
		model = tag
		fields = ('id','created','updated','enacted','name','value','content_type','object_id',)


class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='account-detail')
	
	
	class Meta:
		model = invoice
		fields = ('id','created','updated','enacted','date',)


class SliceprivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='user-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = sliceprivilege
		fields = ('id','created','updated','enacted',)


class PlanetstackroleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = planetstackrole
		fields = ('id','created','updated','enacted','role',)


class NetworksliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
	
	
	class Meta:
		model = networksliver
		fields = ('id','created','updated','enacted','ip','port_id',)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = project
		fields = ('id','created','updated','enacted','name',)


class SliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	service = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='service-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	class Meta:
		model = slice
		fields = ('id','created','updated','enacted','tenant_id','name','enabled','omf_friendly','description','slice_url','network_id','router_id','subnet_id','serviceClass','creator',)


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	class Meta:
		model = network
		fields = ('id','created','updated','enacted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','network_id','router_id','subnet_id',)


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = service
		fields = ('id','created','updated','enacted','description','enabled','name','versionNumber','published',)


class ServiceclassSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = serviceclass
		fields = ('id','created','updated','enacted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)


class SiteroleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = siterole
		fields = ('id','created','updated','enacted','role',)


class ChargeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='account-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	invoice = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='invoice-detail')
	
	
	class Meta:
		model = charge
		fields = ('id','created','updated','enacted','kind','state','date','object','amount','coreHours',)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = role
		fields = ('id','created','updated','enacted','role_type','role','description','content_type',)


class UsableobjectSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = usableobject
		fields = ('id','created','updated','enacted','name',)


class SliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	image = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='image-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	nodes = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='node-detail')
	
	
	class Meta:
		model = sliver
		fields = ('id','created','updated','enacted','instance_id','name','instance_name','ip','creator','deploymentNetwork','numberCores',)


class NodeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
	
	
	class Meta:
		model = node
		fields = ('id','created','updated','enacted','name',)


class ReservedresourceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
	
	
	class Meta:
		model = reservedresource
		fields = ('id','created','updated','enacted','resource','quantity','reservationSet',)


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	account = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='account-detail')
	
	
	class Meta:
		model = payment
		fields = ('id','created','updated','enacted','amount','date',)


class NetworksliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = networkslice
		fields = ('id','created','updated','enacted',)


class PlanetstackprivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='user-detail')
	
	
	
	planetstack = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='planetstack-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = planetstackprivilege
		fields = ('id','created','updated','enacted',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = user
		fields = ('id','password','last_login','email','username','kuser_id','firstname','lastname','phone','user_url','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','timezone',)


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = deployment
		fields = ('id','created','updated','enacted','name',)


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = reservation
		fields = ('id','created','updated','enacted','startTime','duration',)


class SiteprivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='user-detail')
	
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = siteprivilege
		fields = ('id','created','updated','enacted',)


class SingletonmodelSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = singletonmodel
		fields = ()


class PlanetstackSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = planetstack
		fields = ('id','created','updated','enacted','description',)


class AccountSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = account
		fields = ('id','created','updated','enacted',)


class NetworkparametertypeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = networkparametertype
		fields = ('id','created','updated','enacted','name','description',)


class SitedeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
	
	
	class Meta:
		model = sitedeployments
		fields = ('id','created','updated','enacted',)


class DeploymentprivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	user = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='user-detail')
	
	
	
	deployment = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
	
	
	
	role = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')
	
	
	class Meta:
		model = deploymentprivilege
		fields = ('id','created','updated','enacted',)


class DeploymentroleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = deploymentrole
		fields = ('id','created','updated','enacted','role',)


class PlcorebaseSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = plcorebase
		fields = ('created','updated','enacted',)


class SlicetagSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	class Meta:
		model = slicetag
		fields = ('id','created','updated','enacted','name','value',)


class NetworktemplateSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = networktemplate
		fields = ('id','created','updated','enacted','name','description','guaranteedBandwidth','visibility','translation','sharedNetworkName','sharedNetworkId',)


class RouterSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = router
		fields = ('id','created','updated','enacted','name','owner',)


class ServiceresourceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = serviceresource
		fields = ('id','created','updated','enacted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)


serializerLookUp = { 

                 Serviceattribute: ServiceattributeSerializer,

                 Image: ImageSerializer,

                 Networkparameter: NetworkparameterSerializer,

                 Site: SiteSerializer,

                 Slicerole: SliceroleSerializer,

                 Tag: TagSerializer,

                 Invoice: InvoiceSerializer,

                 Sliceprivilege: SliceprivilegeSerializer,

                 Planetstackrole: PlanetstackroleSerializer,

                 Networksliver: NetworksliverSerializer,

                 Project: ProjectSerializer,

                 Slice: SliceSerializer,

                 Network: NetworkSerializer,

                 Service: ServiceSerializer,

                 Serviceclass: ServiceclassSerializer,

                 Siterole: SiteroleSerializer,

                 Charge: ChargeSerializer,

                 Role: RoleSerializer,

                 Usableobject: UsableobjectSerializer,

                 Sliver: SliverSerializer,

                 Node: NodeSerializer,

                 Reservedresource: ReservedresourceSerializer,

                 Payment: PaymentSerializer,

                 Networkslice: NetworksliceSerializer,

                 Planetstackprivilege: PlanetstackprivilegeSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 Reservation: ReservationSerializer,

                 Siteprivilege: SiteprivilegeSerializer,

                 Singletonmodel: SingletonmodelSerializer,

                 Planetstack: PlanetstackSerializer,

                 Account: AccountSerializer,

                 Networkparametertype: NetworkparametertypeSerializer,

                 Sitedeployments: SitedeploymentsSerializer,

                 Deploymentprivilege: DeploymentprivilegeSerializer,

                 Deploymentrole: DeploymentroleSerializer,

                 Plcorebase: PlcorebaseSerializer,

                 Slicetag: SlicetagSerializer,

                 Networktemplate: NetworktemplateSerializer,

                 Router: RouterSerializer,

                 Serviceresource: ServiceresourceSerializer,

                 None: None,
                }

# Based on core/views/*.py


class ServiceattributeList(generics.ListCreateAPIView):
    queryset = Serviceattribute.objects.select_related.all()
    serializer_class = ServiceattributeSerializer

class ServiceattributeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Serviceattribute.objects.select_related.all()
    serializer_class = ServiceattributeSerializer



class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.select_related.all()
    serializer_class = ImageSerializer

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.select_related.all()
    serializer_class = ImageSerializer



class NetworkparameterList(generics.ListCreateAPIView):
    queryset = Networkparameter.objects.select_related.all()
    serializer_class = NetworkparameterSerializer

class NetworkparameterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Networkparameter.objects.select_related.all()
    serializer_class = NetworkparameterSerializer



class SiteList(generics.ListCreateAPIView):
    queryset = Site.objects.select_related.all()
    serializer_class = SiteSerializer

class SiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Site.objects.select_related.all()
    serializer_class = SiteSerializer



class SliceroleList(generics.ListCreateAPIView):
    queryset = Slicerole.objects.select_related.all()
    serializer_class = SliceroleSerializer

class SliceroleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slicerole.objects.select_related.all()
    serializer_class = SliceroleSerializer



class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.select_related.all()
    serializer_class = TagSerializer

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.select_related.all()
    serializer_class = TagSerializer



class InvoiceList(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related.all()
    serializer_class = InvoiceSerializer

class InvoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.select_related.all()
    serializer_class = InvoiceSerializer



class SliceprivilegeList(generics.ListCreateAPIView):
    queryset = Sliceprivilege.objects.select_related.all()
    serializer_class = SliceprivilegeSerializer

class SliceprivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sliceprivilege.objects.select_related.all()
    serializer_class = SliceprivilegeSerializer



class PlanetstackroleList(generics.ListCreateAPIView):
    queryset = Planetstackrole.objects.select_related.all()
    serializer_class = PlanetstackroleSerializer

class PlanetstackroleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Planetstackrole.objects.select_related.all()
    serializer_class = PlanetstackroleSerializer



class NetworksliverList(generics.ListCreateAPIView):
    queryset = Networksliver.objects.select_related.all()
    serializer_class = NetworksliverSerializer

class NetworksliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Networksliver.objects.select_related.all()
    serializer_class = NetworksliverSerializer



class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.select_related.all()
    serializer_class = ProjectSerializer

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.select_related.all()
    serializer_class = ProjectSerializer



class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.select_related.all()
    serializer_class = SliceSerializer

class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.select_related.all()
    serializer_class = SliceSerializer



class NetworkList(generics.ListCreateAPIView):
    queryset = Network.objects.select_related.all()
    serializer_class = NetworkSerializer

class NetworkDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Network.objects.select_related.all()
    serializer_class = NetworkSerializer



class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.select_related.all()
    serializer_class = ServiceSerializer

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related.all()
    serializer_class = ServiceSerializer



class ServiceclassList(generics.ListCreateAPIView):
    queryset = Serviceclass.objects.select_related.all()
    serializer_class = ServiceclassSerializer

class ServiceclassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Serviceclass.objects.select_related.all()
    serializer_class = ServiceclassSerializer



class SiteroleList(generics.ListCreateAPIView):
    queryset = Siterole.objects.select_related.all()
    serializer_class = SiteroleSerializer

class SiteroleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Siterole.objects.select_related.all()
    serializer_class = SiteroleSerializer



class ChargeList(generics.ListCreateAPIView):
    queryset = Charge.objects.select_related.all()
    serializer_class = ChargeSerializer

class ChargeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Charge.objects.select_related.all()
    serializer_class = ChargeSerializer



class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.select_related.all()
    serializer_class = RoleSerializer

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.select_related.all()
    serializer_class = RoleSerializer



class UsableobjectList(generics.ListCreateAPIView):
    queryset = Usableobject.objects.select_related.all()
    serializer_class = UsableobjectSerializer

class UsableobjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usableobject.objects.select_related.all()
    serializer_class = UsableobjectSerializer



class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.select_related.all()
    serializer_class = SliverSerializer

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sliver.objects.select_related.all()
    serializer_class = SliverSerializer



class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.select_related.all()
    serializer_class = NodeSerializer

class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.select_related.all()
    serializer_class = NodeSerializer



class ReservedresourceList(generics.ListCreateAPIView):
    queryset = Reservedresource.objects.select_related.all()
    serializer_class = ReservedresourceSerializer

class ReservedresourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservedresource.objects.select_related.all()
    serializer_class = ReservedresourceSerializer



class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related.all()
    serializer_class = PaymentSerializer

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related.all()
    serializer_class = PaymentSerializer



class NetworksliceList(generics.ListCreateAPIView):
    queryset = Networkslice.objects.select_related.all()
    serializer_class = NetworksliceSerializer

class NetworksliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Networkslice.objects.select_related.all()
    serializer_class = NetworksliceSerializer



class PlanetstackprivilegeList(generics.ListCreateAPIView):
    queryset = Planetstackprivilege.objects.select_related.all()
    serializer_class = PlanetstackprivilegeSerializer

class PlanetstackprivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Planetstackprivilege.objects.select_related.all()
    serializer_class = PlanetstackprivilegeSerializer



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.select_related.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related.all()
    serializer_class = UserSerializer



class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.select_related.all()
    serializer_class = DeploymentSerializer

class DeploymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.select_related.all()
    serializer_class = DeploymentSerializer



class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related.all()
    serializer_class = ReservationSerializer

class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.select_related.all()
    serializer_class = ReservationSerializer



class SiteprivilegeList(generics.ListCreateAPIView):
    queryset = Siteprivilege.objects.select_related.all()
    serializer_class = SiteprivilegeSerializer

class SiteprivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Siteprivilege.objects.select_related.all()
    serializer_class = SiteprivilegeSerializer



class SingletonmodelList(generics.ListCreateAPIView):
    queryset = Singletonmodel.objects.select_related.all()
    serializer_class = SingletonmodelSerializer

class SingletonmodelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Singletonmodel.objects.select_related.all()
    serializer_class = SingletonmodelSerializer



class PlanetstackList(generics.ListCreateAPIView):
    queryset = Planetstack.objects.select_related.all()
    serializer_class = PlanetstackSerializer

class PlanetstackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Planetstack.objects.select_related.all()
    serializer_class = PlanetstackSerializer



class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.select_related.all()
    serializer_class = AccountSerializer

class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.select_related.all()
    serializer_class = AccountSerializer



class NetworkparametertypeList(generics.ListCreateAPIView):
    queryset = Networkparametertype.objects.select_related.all()
    serializer_class = NetworkparametertypeSerializer

class NetworkparametertypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Networkparametertype.objects.select_related.all()
    serializer_class = NetworkparametertypeSerializer



class SitedeploymentsList(generics.ListCreateAPIView):
    queryset = Sitedeployments.objects.select_related.all()
    serializer_class = SitedeploymentsSerializer

class SitedeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sitedeployments.objects.select_related.all()
    serializer_class = SitedeploymentsSerializer



class DeploymentprivilegeList(generics.ListCreateAPIView):
    queryset = Deploymentprivilege.objects.select_related.all()
    serializer_class = DeploymentprivilegeSerializer

class DeploymentprivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deploymentprivilege.objects.select_related.all()
    serializer_class = DeploymentprivilegeSerializer



class DeploymentroleList(generics.ListCreateAPIView):
    queryset = Deploymentrole.objects.select_related.all()
    serializer_class = DeploymentroleSerializer

class DeploymentroleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deploymentrole.objects.select_related.all()
    serializer_class = DeploymentroleSerializer



class PlcorebaseList(generics.ListCreateAPIView):
    queryset = Plcorebase.objects.select_related.all()
    serializer_class = PlcorebaseSerializer

class PlcorebaseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plcorebase.objects.select_related.all()
    serializer_class = PlcorebaseSerializer



class SlicetagList(generics.ListCreateAPIView):
    queryset = Slicetag.objects.select_related.all()
    serializer_class = SlicetagSerializer

class SlicetagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slicetag.objects.select_related.all()
    serializer_class = SlicetagSerializer



class NetworktemplateList(generics.ListCreateAPIView):
    queryset = Networktemplate.objects.select_related.all()
    serializer_class = NetworktemplateSerializer

class NetworktemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Networktemplate.objects.select_related.all()
    serializer_class = NetworktemplateSerializer



class RouterList(generics.ListCreateAPIView):
    queryset = Router.objects.select_related.all()
    serializer_class = RouterSerializer

class RouterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Router.objects.select_related.all()
    serializer_class = RouterSerializer



class ServiceresourceList(generics.ListCreateAPIView):
    queryset = Serviceresource.objects.select_related.all()
    serializer_class = ServiceresourceSerializer

class ServiceresourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Serviceresource.objects.select_related.all()
    serializer_class = ServiceresourceSerializer



