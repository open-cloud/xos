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
		'networkdeploymentses': reverse('networkdeployments-list', request=request, format=format),
		'slices': reverse('slice-list', request=request, format=format),
		'networks': reverse('network-list', request=request, format=format),
		'services': reverse('service-list', request=request, format=format),
		'serviceclasses': reverse('serviceclass-list', request=request, format=format),
		'payments': reverse('payment-list', request=request, format=format),
		'charges': reverse('charge-list', request=request, format=format),
		'roles': reverse('role-list', request=request, format=format),
		'usableobjects': reverse('usableobject-list', request=request, format=format),
		'siteroles': reverse('siterole-list', request=request, format=format),
		'slivers': reverse('sliver-list', request=request, format=format),
		'nodes': reverse('node-list', request=request, format=format),
		'dashboardviews': reverse('dashboardview-list', request=request, format=format),
		'imagedeploymentses': reverse('imagedeployments-list', request=request, format=format),
		'reservedresources': reverse('reservedresource-list', request=request, format=format),
		'networkslices': reverse('networkslice-list', request=request, format=format),
		'userdashboardviews': reverse('userdashboardview-list', request=request, format=format),
		'planetstackprivileges': reverse('planetstackprivilege-list', request=request, format=format),
		'users': reverse('user-list', request=request, format=format),
		'deployments': reverse('deployment-list', request=request, format=format),
		'reservations': reverse('reservation-list', request=request, format=format),
		'slicedeploymentses': reverse('slicedeployments-list', request=request, format=format),
		'siteprivileges': reverse('siteprivilege-list', request=request, format=format),
		'planetstacks': reverse('planetstack-list', request=request, format=format),
		'userdeploymentses': reverse('userdeployments-list', request=request, format=format),
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
	
	class Meta:
		model = ServiceAttribute
		fields = ('id','created','updated','enacted','name','value','service',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Image
		fields = ('id','created','updated','enacted','name','disk_format','container_format','path',)


class NetworkParameterSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkParameter
		fields = ('id','created','updated','enacted','parameter','value','content_type','object_id',)


class SiteSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Site
		fields = ('id','created','updated','enacted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)


class SliceRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SliceRole
		fields = ('id','created','updated','enacted','role',)


class TagSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
	
	
	
	slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
	
	
	
	nodes = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='node-detail')
	
	
	class Meta:
		model = Tag
		fields = ('id','created','updated','enacted','service','name','value','content_type','object_id','sites','slices','slivers','nodes',)


class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Invoice
		fields = ('id','created','updated','enacted','date','account',)


class PlanetStackRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = PlanetStackRole
		fields = ('id','created','updated','enacted','role',)


class SlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SlicePrivilege
		fields = ('id','created','updated','enacted','user','slice','role',)


class NetworkSliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkSliver
		fields = ('id','created','updated','enacted','network','sliver','ip','port_id',)


class NetworkDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkDeployments
		fields = ('id','created','updated','enacted','network','deployment','net_id','router_id','subnet_id','subnet',)


class SliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	availableNetworks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	class Meta:
		model = Slice
		fields = ('id','created','updated','enacted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','imagePreference','service','network','mountDataSets','serviceClass','creator','networks','availableNetworks','networks','networks',)


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	
	availableRouters = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	
	routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
	
	
	class Meta:
		model = Network
		fields = ('id','created','updated','enacted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','network_id','router_id','subnet_id','routers','availableRouters','routers','routers',)


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


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Payment
		fields = ('id','created','updated','enacted','account','amount','date',)


class ChargeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Charge
		fields = ('id','created','updated','enacted','account','slice','kind','state','date','object','amount','coreHours','invoice',)


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


class SiteRoleSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SiteRole
		fields = ('id','created','updated','enacted','role',)


class SliverSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
	networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
	
	
	
#	upgradeFrom_rel_+ = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='serviceclass-detail')
	
	
	class Meta:
		model = Sliver
		fields = ('id','created','updated','enacted','instance_id','name','instance_name','ip','image','creator','slice','node','deploymentNetwork','numberCores','userData','networks','networks','upgradeFrom_rel_+',)


class NodeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Node
		fields = ('id','created','updated','enacted','name','site','deployment',)


class DashboardViewSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = DashboardView
		fields = ('id','created','updated','enacted','name','url',)


class ImageDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = ImageDeployments
		fields = ('id','created','updated','enacted','image','deployment','glance_image_id',)


class ReservedResourceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = ReservedResource
		fields = ('id','created','updated','enacted','sliver','resource','quantity','reservationSet',)


class NetworkSliceSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkSlice
		fields = ('id','created','updated','enacted','network','slice',)


class UserDashboardViewSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = UserDashboardView
		fields = ('id','created','updated','enacted','user','dashboardView','order',)


class PlanetStackPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = PlanetStackPrivilege
		fields = ('id','created','updated','enacted','user','planetstack','role',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = User
		fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','timezone',)


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	
	sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
	
	
	class Meta:
		model = Deployment
		fields = ('id','created','updated','enacted','name','admin_user','admin_password','admin_tenant','auth_url','accessControl','sites','sites',)


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Reservation
		fields = ('id','created','updated','enacted','startTime','slice','duration',)


class SliceDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SliceDeployments
		fields = ('id','created','updated','enacted','slice','deployment','tenant_id','network_id','router_id','subnet_id',)


class SitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SitePrivilege
		fields = ('id','created','updated','enacted','user','site','role',)


class PlanetStackSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = PlanetStack
		fields = ('id','created','updated','enacted','description',)


class UserDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = UserDeployments
		fields = ('id','created','updated','enacted','user','deployment','kuser_id',)


class AccountSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = Account
		fields = ('id','created','updated','enacted','site',)


class NetworkParameterTypeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = NetworkParameterType
		fields = ('id','created','updated','enacted','name','description',)


class SiteDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = SiteDeployments
		fields = ('id','created','updated','enacted','site','deployment','tenant_id',)


class DeploymentPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
	id = serializers.Field()
	
	class Meta:
		model = DeploymentPrivilege
		fields = ('id','created','updated','enacted','user','deployment','role',)


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
	
	class Meta:
		model = SliceTag
		fields = ('id','created','updated','enacted','slice','name','value',)


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

                 NetworkDeployments: NetworkDeploymentsSerializer,

                 Slice: SliceSerializer,

                 Network: NetworkSerializer,

                 Service: ServiceSerializer,

                 ServiceClass: ServiceClassSerializer,

                 Payment: PaymentSerializer,

                 Charge: ChargeSerializer,

                 Role: RoleSerializer,

                 UsableObject: UsableObjectSerializer,

                 SiteRole: SiteRoleSerializer,

                 Sliver: SliverSerializer,

                 Node: NodeSerializer,

                 DashboardView: DashboardViewSerializer,

                 ImageDeployments: ImageDeploymentsSerializer,

                 ReservedResource: ReservedResourceSerializer,

                 NetworkSlice: NetworkSliceSerializer,

                 UserDashboardView: UserDashboardViewSerializer,

                 PlanetStackPrivilege: PlanetStackPrivilegeSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 Reservation: ReservationSerializer,

                 SliceDeployments: SliceDeploymentsSerializer,

                 SitePrivilege: SitePrivilegeSerializer,

                 PlanetStack: PlanetStackSerializer,

                 UserDeployments: UserDeploymentsSerializer,

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
    
    def get_queryset(self):
        return ServiceAttribute.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = ServiceAttribute().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceAttributeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ServiceAttributeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer
    
    def get_queryset(self):
        return ServiceAttribute.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceAttributeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceAttributeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    
    def get_queryset(self):
        return Image.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Image().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ImageList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    
    def get_queryset(self):
        return Image.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ImageDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ImageDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkParameterList(generics.ListCreateAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    
    def get_queryset(self):
        return NetworkParameter.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkParameter().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkParameterList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkParameterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    
    def get_queryset(self):
        return NetworkParameter.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkParameterDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkParameterDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SiteList(generics.ListCreateAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    
    def get_queryset(self):
        return Site.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Site().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SiteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    
    def get_queryset(self):
        return Site.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SliceRoleList(generics.ListCreateAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    
    def get_queryset(self):
        return SliceRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SliceRole().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceRoleList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SliceRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    
    def get_queryset(self):
        return SliceRole.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceRoleDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceRoleDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    
    def get_queryset(self):
        return Tag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Tag().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(TagList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    
    def get_queryset(self):
        return Tag.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(TagDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(TagDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class InvoiceList(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Invoice().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(InvoiceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class InvoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(InvoiceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(InvoiceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class PlanetStackRoleList(generics.ListCreateAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer
    
    def get_queryset(self):
        return PlanetStackRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = PlanetStackRole().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackRoleList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PlanetStackRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer
    
    def get_queryset(self):
        return PlanetStackRole.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackRoleDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackRoleDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SlicePrivilegeList(generics.ListCreateAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    
    def get_queryset(self):
        return SlicePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SlicePrivilege().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SlicePrivilegeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SlicePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    
    def get_queryset(self):
        return SlicePrivilege.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SlicePrivilegeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SlicePrivilegeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkSliverList(generics.ListCreateAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer
    
    def get_queryset(self):
        return NetworkSliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkSliver().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkSliverList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkSliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer
    
    def get_queryset(self):
        return NetworkSliver.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkSliverDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkSliverDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkDeploymentsList(generics.ListCreateAPIView):
    queryset = NetworkDeployments.objects.select_related().all()
    serializer_class = NetworkDeploymentsSerializer
    
    def get_queryset(self):
        return NetworkDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkDeployments().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkDeploymentsList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkDeployments.objects.select_related().all()
    serializer_class = NetworkDeploymentsSerializer
    
    def get_queryset(self):
        return NetworkDeployments.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkDeploymentsDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkDeploymentsDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    
    def get_queryset(self):
        return Slice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Slice().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    
    def get_queryset(self):
        return Slice.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkList(generics.ListCreateAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    
    def get_queryset(self):
        return Network.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Network().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    
    def get_queryset(self):
        return Network.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        return Service.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Service().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        return Service.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ServiceClassList(generics.ListCreateAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer
    
    def get_queryset(self):
        return ServiceClass.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = ServiceClass().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceClassList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ServiceClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer
    
    def get_queryset(self):
        return ServiceClass.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceClassDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceClassDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Payment().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PaymentList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PaymentDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PaymentDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ChargeList(generics.ListCreateAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer
    
    def get_queryset(self):
        return Charge.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Charge().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ChargeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ChargeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer
    
    def get_queryset(self):
        return Charge.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ChargeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ChargeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    
    def get_queryset(self):
        return Role.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Role().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(RoleList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    
    def get_queryset(self):
        return Role.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(RoleDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(RoleDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class UsableObjectList(generics.ListCreateAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer
    
    def get_queryset(self):
        return UsableObject.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = UsableObject().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UsableObjectList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UsableObjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer
    
    def get_queryset(self):
        return UsableObject.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UsableObjectDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UsableObjectDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SiteRoleList(generics.ListCreateAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    
    def get_queryset(self):
        return SiteRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SiteRole().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteRoleList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SiteRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    
    def get_queryset(self):
        return SiteRole.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteRoleDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteRoleDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer
    
    def get_queryset(self):
        return Sliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Sliver().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliverList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer
    
    def get_queryset(self):
        return Sliver.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliverDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliverDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    
    def get_queryset(self):
        return Node.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Node().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NodeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    
    def get_queryset(self):
        return Node.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NodeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NodeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class DashboardViewList(generics.ListCreateAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    
    def get_queryset(self):
        return DashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = DashboardView().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DashboardViewList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DashboardViewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    
    def get_queryset(self):
        return DashboardView.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DashboardViewDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DashboardViewDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ImageDeploymentsList(generics.ListCreateAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    
    def get_queryset(self):
        return ImageDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = ImageDeployments().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ImageDeploymentsList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ImageDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    
    def get_queryset(self):
        return ImageDeployments.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ImageDeploymentsDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ImageDeploymentsDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ReservedResourceList(generics.ListCreateAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer
    
    def get_queryset(self):
        return ReservedResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = ReservedResource().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ReservedResourceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ReservedResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer
    
    def get_queryset(self):
        return ReservedResource.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ReservedResourceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ReservedResourceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkSliceList(generics.ListCreateAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    
    def get_queryset(self):
        return NetworkSlice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkSlice().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkSliceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkSliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    
    def get_queryset(self):
        return NetworkSlice.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkSliceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkSliceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class UserDashboardViewList(generics.ListCreateAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    
    def get_queryset(self):
        return UserDashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = UserDashboardView().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserDashboardViewList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserDashboardViewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    
    def get_queryset(self):
        return UserDashboardView.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDashboardViewDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDashboardViewDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class PlanetStackPrivilegeList(generics.ListCreateAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer
    
    def get_queryset(self):
        return PlanetStackPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = PlanetStackPrivilege().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackPrivilegeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PlanetStackPrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer
    
    def get_queryset(self):
        return PlanetStackPrivilege.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackPrivilegeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackPrivilegeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = User().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    
    def get_queryset(self):
        return Deployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Deployment().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DeploymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    
    def get_queryset(self):
        return Deployment.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        return Reservation.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Reservation().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ReservationList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        return Reservation.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ReservationDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ReservationDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SliceDeploymentsList(generics.ListCreateAPIView):
    queryset = SliceDeployments.objects.select_related().all()
    serializer_class = SliceDeploymentsSerializer
    
    def get_queryset(self):
        return SliceDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SliceDeployments().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceDeploymentsList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SliceDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceDeployments.objects.select_related().all()
    serializer_class = SliceDeploymentsSerializer
    
    def get_queryset(self):
        return SliceDeployments.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceDeploymentsDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceDeploymentsDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SitePrivilegeList(generics.ListCreateAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    
    def get_queryset(self):
        return SitePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SitePrivilege().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SitePrivilegeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SitePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    
    def get_queryset(self):
        return SitePrivilege.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SitePrivilegeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SitePrivilegeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class PlanetStackList(generics.ListCreateAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer
    
    def get_queryset(self):
        return PlanetStack.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = PlanetStack().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PlanetStackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer
    
    def get_queryset(self):
        return PlanetStack.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class UserDeploymentsList(generics.ListCreateAPIView):
    queryset = UserDeployments.objects.select_related().all()
    serializer_class = UserDeploymentsSerializer
    
    def get_queryset(self):
        return UserDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = UserDeployments().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserDeploymentsList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserDeployments.objects.select_related().all()
    serializer_class = UserDeploymentsSerializer
    
    def get_queryset(self):
        return UserDeployments.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDeploymentsDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(UserDeploymentsDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer
    
    def get_queryset(self):
        return Account.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Account().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(AccountList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer
    
    def get_queryset(self):
        return Account.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(AccountDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(AccountDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkParameterTypeList(generics.ListCreateAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    
    def get_queryset(self):
        return NetworkParameterType.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkParameterType().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkParameterTypeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkParameterTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    
    def get_queryset(self):
        return NetworkParameterType.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkParameterTypeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkParameterTypeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SiteDeploymentsList(generics.ListCreateAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer
    
    def get_queryset(self):
        return SiteDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SiteDeployments().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteDeploymentsList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SiteDeploymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer
    
    def get_queryset(self):
        return SiteDeployments.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteDeploymentsDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SiteDeploymentsDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class DeploymentPrivilegeList(generics.ListCreateAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    
    def get_queryset(self):
        return DeploymentPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = DeploymentPrivilege().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentPrivilegeList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DeploymentPrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    
    def get_queryset(self):
        return DeploymentPrivilege.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentPrivilegeDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentPrivilegeDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class DeploymentRoleList(generics.ListCreateAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    
    def get_queryset(self):
        return DeploymentRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = DeploymentRole().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentRoleList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DeploymentRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    
    def get_queryset(self):
        return DeploymentRole.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentRoleDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(DeploymentRoleDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        return Project.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Project().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ProjectList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        return Project.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ProjectDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ProjectDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class SliceTagList(generics.ListCreateAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer
    
    def get_queryset(self):
        return SliceTag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = SliceTag().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceTagList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SliceTagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer
    
    def get_queryset(self):
        return SliceTag.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceTagDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SliceTagDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class NetworkTemplateList(generics.ListCreateAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    
    def get_queryset(self):
        return NetworkTemplate.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = NetworkTemplate().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkTemplateList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class NetworkTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    
    def get_queryset(self):
        return NetworkTemplate.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkTemplateDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(NetworkTemplateDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class RouterList(generics.ListCreateAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer
    
    def get_queryset(self):
        return Router.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = Router().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(RouterList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RouterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer
    
    def get_queryset(self):
        return Router.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(RouterDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(RouterDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



class ServiceResourceList(generics.ListCreateAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer
    
    def get_queryset(self):
        return ServiceResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = ServiceResource().update(request.DATA)
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceResourceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ServiceResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer
    
    def get_queryset(self):
        return ServiceResource.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceResourceDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(ServiceResourceDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     



