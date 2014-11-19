from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import GenericAPIView
from core.models import *
from django.forms import widgets
from rest_framework import filters
from django.conf.urls import patterns, url

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

def get_REST_patterns():
    return patterns('',
        url(r'^plstackapi/$', api_root),
    
        url(r'plstackapi/serviceattributes/$', ServiceAttributeList.as_view(), name='serviceattribute-list'),
        url(r'plstackapi/serviceattributes/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceAttributeDetail.as_view(), name ='serviceattribute-detail'),
#        url(r'plstackapi/serviceattributes/!new/$', ServiceAttributeNew.as_view(), name ='serviceattribute-new'),
    
        url(r'plstackapi/images/$', ImageList.as_view(), name='image-list'),
        url(r'plstackapi/images/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDetail.as_view(), name ='image-detail'),
#        url(r'plstackapi/images/!new/$', ImageNew.as_view(), name ='image-new'),
    
        url(r'plstackapi/networkparameters/$', NetworkParameterList.as_view(), name='networkparameter-list'),
        url(r'plstackapi/networkparameters/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterDetail.as_view(), name ='networkparameter-detail'),
#        url(r'plstackapi/networkparameters/!new/$', NetworkParameterNew.as_view(), name ='networkparameter-new'),
    
        url(r'plstackapi/sites/$', SiteList.as_view(), name='site-list'),
        url(r'plstackapi/sites/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDetail.as_view(), name ='site-detail'),
#        url(r'plstackapi/sites/!new/$', SiteNew.as_view(), name ='site-new'),
    
        url(r'plstackapi/slice_roles/$', SliceRoleList.as_view(), name='slicerole-list'),
        url(r'plstackapi/slice_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceRoleDetail.as_view(), name ='slicerole-detail'),
#        url(r'plstackapi/slice_roles/!new/$', SliceRoleNew.as_view(), name ='slicerole-new'),
    
        url(r'plstackapi/tags/$', TagList.as_view(), name='tag-list'),
        url(r'plstackapi/tags/(?P<pk>[a-zA-Z0-9\-]+)/$', TagDetail.as_view(), name ='tag-detail'),
#        url(r'plstackapi/tags/!new/$', TagNew.as_view(), name ='tag-new'),
    
        url(r'plstackapi/invoices/$', InvoiceList.as_view(), name='invoice-list'),
        url(r'plstackapi/invoices/(?P<pk>[a-zA-Z0-9\-]+)/$', InvoiceDetail.as_view(), name ='invoice-detail'),
#        url(r'plstackapi/invoices/!new/$', InvoiceNew.as_view(), name ='invoice-new'),
    
        url(r'plstackapi/slice_privileges/$', SlicePrivilegeList.as_view(), name='sliceprivilege-list'),
        url(r'plstackapi/slice_privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SlicePrivilegeDetail.as_view(), name ='sliceprivilege-detail'),
#        url(r'plstackapi/slice_privileges/!new/$', SlicePrivilegeNew.as_view(), name ='sliceprivilege-new'),
    
        url(r'plstackapi/planetstackroles/$', PlanetStackRoleList.as_view(), name='planetstackrole-list'),
        url(r'plstackapi/planetstackroles/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackRoleDetail.as_view(), name ='planetstackrole-detail'),
#        url(r'plstackapi/planetstackroles/!new/$', PlanetStackRoleNew.as_view(), name ='planetstackrole-new'),
    
        url(r'plstackapi/networkslivers/$', NetworkSliverList.as_view(), name='networksliver-list'),
        url(r'plstackapi/networkslivers/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliverDetail.as_view(), name ='networksliver-detail'),
#        url(r'plstackapi/networkslivers/!new/$', NetworkSliverNew.as_view(), name ='networksliver-new'),
    
        url(r'plstackapi/networkdeployments/$', NetworkDeploymentsList.as_view(), name='networkdeployments-list'),
        url(r'plstackapi/networkdeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkDeploymentsDetail.as_view(), name ='networkdeployments-detail'),
#        url(r'plstackapi/networkdeployments/!new/$', NetworkDeploymentsNew.as_view(), name ='networkdeployments-new'),
    
        url(r'plstackapi/flavors/$', FlavorList.as_view(), name='flavor-list'),
        url(r'plstackapi/flavors/(?P<pk>[a-zA-Z0-9\-]+)/$', FlavorDetail.as_view(), name ='flavor-detail'),
#        url(r'plstackapi/flavors/!new/$', FlavorNew.as_view(), name ='flavor-new'),
    
        url(r'plstackapi/projects/$', ProjectList.as_view(), name='project-list'),
        url(r'plstackapi/projects/(?P<pk>[a-zA-Z0-9\-]+)/$', ProjectDetail.as_view(), name ='project-detail'),
#        url(r'plstackapi/projects/!new/$', ProjectNew.as_view(), name ='project-new'),
    
        url(r'plstackapi/slices/$', SliceList.as_view(), name='slice-list'),
        url(r'plstackapi/slices/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceDetail.as_view(), name ='slice-detail'),
#        url(r'plstackapi/slices/!new/$', SliceNew.as_view(), name ='slice-new'),
    
        url(r'plstackapi/networks/$', NetworkList.as_view(), name='network-list'),
        url(r'plstackapi/networks/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkDetail.as_view(), name ='network-detail'),
#        url(r'plstackapi/networks/!new/$', NetworkNew.as_view(), name ='network-new'),
    
        url(r'plstackapi/services/$', ServiceList.as_view(), name='service-list'),
        url(r'plstackapi/services/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDetail.as_view(), name ='service-detail'),
#        url(r'plstackapi/services/!new/$', ServiceNew.as_view(), name ='service-new'),
    
        url(r'plstackapi/serviceclasses/$', ServiceClassList.as_view(), name='serviceclass-list'),
        url(r'plstackapi/serviceclasses/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceClassDetail.as_view(), name ='serviceclass-detail'),
#        url(r'plstackapi/serviceclasses/!new/$', ServiceClassNew.as_view(), name ='serviceclass-new'),
    
        url(r'plstackapi/planetstacks/$', PlanetStackList.as_view(), name='planetstack-list'),
        url(r'plstackapi/planetstacks/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackDetail.as_view(), name ='planetstack-detail'),
#        url(r'plstackapi/planetstacks/!new/$', PlanetStackNew.as_view(), name ='planetstack-new'),
    
        url(r'plstackapi/charges/$', ChargeList.as_view(), name='charge-list'),
        url(r'plstackapi/charges/(?P<pk>[a-zA-Z0-9\-]+)/$', ChargeDetail.as_view(), name ='charge-detail'),
#        url(r'plstackapi/charges/!new/$', ChargeNew.as_view(), name ='charge-new'),
    
        url(r'plstackapi/roles/$', RoleList.as_view(), name='role-list'),
        url(r'plstackapi/roles/(?P<pk>[a-zA-Z0-9\-]+)/$', RoleDetail.as_view(), name ='role-detail'),
#        url(r'plstackapi/roles/!new/$', RoleNew.as_view(), name ='role-new'),
    
        url(r'plstackapi/usableobjects/$', UsableObjectList.as_view(), name='usableobject-list'),
        url(r'plstackapi/usableobjects/(?P<pk>[a-zA-Z0-9\-]+)/$', UsableObjectDetail.as_view(), name ='usableobject-detail'),
#        url(r'plstackapi/usableobjects/!new/$', UsableObjectNew.as_view(), name ='usableobject-new'),
    
        url(r'plstackapi/site_roles/$', SiteRoleList.as_view(), name='siterole-list'),
        url(r'plstackapi/site_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteRoleDetail.as_view(), name ='siterole-detail'),
#        url(r'plstackapi/site_roles/!new/$', SiteRoleNew.as_view(), name ='siterole-new'),
    
        url(r'plstackapi/slicecredentials/$', SliceCredentialList.as_view(), name='slicecredential-list'),
        url(r'plstackapi/slicecredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceCredentialDetail.as_view(), name ='slicecredential-detail'),
#        url(r'plstackapi/slicecredentials/!new/$', SliceCredentialNew.as_view(), name ='slicecredential-new'),
    
        url(r'plstackapi/slivers/$', SliverList.as_view(), name='sliver-list'),
        url(r'plstackapi/slivers/(?P<pk>[a-zA-Z0-9\-]+)/$', SliverDetail.as_view(), name ='sliver-detail'),
#        url(r'plstackapi/slivers/!new/$', SliverNew.as_view(), name ='sliver-new'),
    
        url(r'plstackapi/nodes/$', NodeList.as_view(), name='node-list'),
        url(r'plstackapi/nodes/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeDetail.as_view(), name ='node-detail'),
#        url(r'plstackapi/nodes/!new/$', NodeNew.as_view(), name ='node-new'),
    
        url(r'plstackapi/dashboardviews/$', DashboardViewList.as_view(), name='dashboardview-list'),
        url(r'plstackapi/dashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', DashboardViewDetail.as_view(), name ='dashboardview-detail'),
#        url(r'plstackapi/dashboardviews/!new/$', DashboardViewNew.as_view(), name ='dashboardview-new'),
    
        url(r'plstackapi/reservedresources/$', ReservedResourceList.as_view(), name='reservedresource-list'),
        url(r'plstackapi/reservedresources/(?P<pk>[a-zA-Z0-9\-]+)/$', ReservedResourceDetail.as_view(), name ='reservedresource-detail'),
#        url(r'plstackapi/reservedresources/!new/$', ReservedResourceNew.as_view(), name ='reservedresource-new'),
    
        url(r'plstackapi/payments/$', PaymentList.as_view(), name='payment-list'),
        url(r'plstackapi/payments/(?P<pk>[a-zA-Z0-9\-]+)/$', PaymentDetail.as_view(), name ='payment-detail'),
#        url(r'plstackapi/payments/!new/$', PaymentNew.as_view(), name ='payment-new'),
    
        url(r'plstackapi/networkslices/$', NetworkSliceList.as_view(), name='networkslice-list'),
        url(r'plstackapi/networkslices/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliceDetail.as_view(), name ='networkslice-detail'),
#        url(r'plstackapi/networkslices/!new/$', NetworkSliceNew.as_view(), name ='networkslice-new'),
    
        url(r'plstackapi/userdashboardviews/$', UserDashboardViewList.as_view(), name='userdashboardview-list'),
        url(r'plstackapi/userdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDashboardViewDetail.as_view(), name ='userdashboardview-detail'),
#        url(r'plstackapi/userdashboardviews/!new/$', UserDashboardViewNew.as_view(), name ='userdashboardview-new'),
    
        url(r'plstackapi/sitedeployments/$', SiteDeploymentsList.as_view(), name='sitedeployment-list'),
        url(r'plstackapi/sitedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDeploymentsDetail.as_view(), name ='sitedeployment-detail'),
#        url(r'plstackapi/sitedeployments/!new/$', SiteDeploymentsNew.as_view(), name ='sitedeployment-new'),
    
        url(r'plstackapi/planetstackprivileges/$', PlanetStackPrivilegeList.as_view(), name='planetstackprivilege-list'),
        url(r'plstackapi/planetstackprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackPrivilegeDetail.as_view(), name ='planetstackprivilege-detail'),
#        url(r'plstackapi/planetstackprivileges/!new/$', PlanetStackPrivilegeNew.as_view(), name ='planetstackprivilege-new'),
    
        url(r'plstackapi/users/$', UserList.as_view(), name='user-list'),
        url(r'plstackapi/users/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDetail.as_view(), name ='user-detail'),
#        url(r'plstackapi/users/!new/$', UserNew.as_view(), name ='user-new'),
    
        url(r'plstackapi/deployments/$', DeploymentList.as_view(), name='deployment-list'),
        url(r'plstackapi/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name ='deployment-detail'),
#        url(r'plstackapi/deployments/!new/$', DeploymentNew.as_view(), name ='deployment-new'),
    
        url(r'plstackapi/reservations/$', ReservationList.as_view(), name='reservation-list'),
        url(r'plstackapi/reservations/(?P<pk>[a-zA-Z0-9\-]+)/$', ReservationDetail.as_view(), name ='reservation-detail'),
#        url(r'plstackapi/reservations/!new/$', ReservationNew.as_view(), name ='reservation-new'),
    
        url(r'plstackapi/siteprivileges/$', SitePrivilegeList.as_view(), name='siteprivilege-list'),
        url(r'plstackapi/siteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SitePrivilegeDetail.as_view(), name ='siteprivilege-detail'),
#        url(r'plstackapi/siteprivileges/!new/$', SitePrivilegeNew.as_view(), name ='siteprivilege-new'),
    
        url(r'plstackapi/slicedeployments/$', SliceDeploymentsList.as_view(), name='slicedeployment-list'),
        url(r'plstackapi/slicedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceDeploymentsDetail.as_view(), name ='slicedeployment-detail'),
#        url(r'plstackapi/slicedeployments/!new/$', SliceDeploymentsNew.as_view(), name ='slicedeployment-new'),
    
        url(r'plstackapi/userdeployments/$', UserDeploymentList.as_view(), name='userdeployment-list'),
        url(r'plstackapi/userdeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDeploymentDetail.as_view(), name ='userdeployment-detail'),
#        url(r'plstackapi/userdeployments/!new/$', UserDeploymentNew.as_view(), name ='userdeployment-new'),
    
        url(r'plstackapi/accounts/$', AccountList.as_view(), name='account-list'),
        url(r'plstackapi/accounts/(?P<pk>[a-zA-Z0-9\-]+)/$', AccountDetail.as_view(), name ='account-detail'),
#        url(r'plstackapi/accounts/!new/$', AccountNew.as_view(), name ='account-new'),
    
        url(r'plstackapi/networkparametertypes/$', NetworkParameterTypeList.as_view(), name='networkparametertype-list'),
        url(r'plstackapi/networkparametertypes/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterTypeDetail.as_view(), name ='networkparametertype-detail'),
#        url(r'plstackapi/networkparametertypes/!new/$', NetworkParameterTypeNew.as_view(), name ='networkparametertype-new'),
    
        url(r'plstackapi/sitecredentials/$', SiteCredentialList.as_view(), name='sitecredential-list'),
        url(r'plstackapi/sitecredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteCredentialDetail.as_view(), name ='sitecredential-detail'),
#        url(r'plstackapi/sitecredentials/!new/$', SiteCredentialNew.as_view(), name ='sitecredential-new'),
    
        url(r'plstackapi/deploymentprivileges/$', DeploymentPrivilegeList.as_view(), name='deploymentprivilege-list'),
        url(r'plstackapi/deploymentprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentPrivilegeDetail.as_view(), name ='deploymentprivilege-detail'),
#        url(r'plstackapi/deploymentprivileges/!new/$', DeploymentPrivilegeNew.as_view(), name ='deploymentprivilege-new'),
    
        url(r'plstackapi/imagedeployments/$', ImageDeploymentList.as_view(), name='imagedeployment-list'),
        url(r'plstackapi/imagedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDeploymentDetail.as_view(), name ='imagedeployment-detail'),
#        url(r'plstackapi/imagedeployments/!new/$', ImageDeploymentNew.as_view(), name ='imagedeployment-new'),
    
        url(r'plstackapi/deploymentroles/$', DeploymentRoleList.as_view(), name='deploymentrole-list'),
        url(r'plstackapi/deploymentroles/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentRoleDetail.as_view(), name ='deploymentrole-detail'),
#        url(r'plstackapi/deploymentroles/!new/$', DeploymentRoleNew.as_view(), name ='deploymentrole-new'),
    
        url(r'plstackapi/usercredentials/$', UserCredentialList.as_view(), name='usercredential-list'),
        url(r'plstackapi/usercredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', UserCredentialDetail.as_view(), name ='usercredential-detail'),
#        url(r'plstackapi/usercredentials/!new/$', UserCredentialNew.as_view(), name ='usercredential-new'),
    
        url(r'plstackapi/slicetags/$', SliceTagList.as_view(), name='slicetag-list'),
        url(r'plstackapi/slicetags/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceTagDetail.as_view(), name ='slicetag-detail'),
#        url(r'plstackapi/slicetags/!new/$', SliceTagNew.as_view(), name ='slicetag-new'),
    
        url(r'plstackapi/networktemplates/$', NetworkTemplateList.as_view(), name='networktemplate-list'),
        url(r'plstackapi/networktemplates/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkTemplateDetail.as_view(), name ='networktemplate-detail'),
#        url(r'plstackapi/networktemplates/!new/$', NetworkTemplateNew.as_view(), name ='networktemplate-new'),
    
        url(r'plstackapi/routers/$', RouterList.as_view(), name='router-list'),
        url(r'plstackapi/routers/(?P<pk>[a-zA-Z0-9\-]+)/$', RouterDetail.as_view(), name ='router-detail'),
#        url(r'plstackapi/routers/!new/$', RouterNew.as_view(), name ='router-new'),
    
        url(r'plstackapi/serviceresources/$', ServiceResourceList.as_view(), name='serviceresource-list'),
        url(r'plstackapi/serviceresources/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceResourceDetail.as_view(), name ='serviceresource-detail'),
#        url(r'plstackapi/serviceresources/!new/$', ServiceResourceNew.as_view(), name ='serviceresource-new'),
    
    )

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
        'networkdeploymentses': reverse('networkdeployments-list', request=request, format=format),
        'flavors': reverse('flavor-list', request=request, format=format),
        'projects': reverse('project-list', request=request, format=format),
        'slices': reverse('slice-list', request=request, format=format),
        'networks': reverse('network-list', request=request, format=format),
        'services': reverse('service-list', request=request, format=format),
        'serviceclasses': reverse('serviceclass-list', request=request, format=format),
        'planetstacks': reverse('planetstack-list', request=request, format=format),
        'charges': reverse('charge-list', request=request, format=format),
        'roles': reverse('role-list', request=request, format=format),
        'usableobjects': reverse('usableobject-list', request=request, format=format),
        'siteroles': reverse('siterole-list', request=request, format=format),
        'slicecredentials': reverse('slicecredential-list', request=request, format=format),
        'slivers': reverse('sliver-list', request=request, format=format),
        'nodes': reverse('node-list', request=request, format=format),
        'dashboardviews': reverse('dashboardview-list', request=request, format=format),
        'reservedresources': reverse('reservedresource-list', request=request, format=format),
        'payments': reverse('payment-list', request=request, format=format),
        'networkslices': reverse('networkslice-list', request=request, format=format),
        'userdashboardviews': reverse('userdashboardview-list', request=request, format=format),
        'sitedeployments': reverse('sitedeployment-list', request=request, format=format),
        'planetstackprivileges': reverse('planetstackprivilege-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'deployments': reverse('deployment-list', request=request, format=format),
        'reservations': reverse('reservation-list', request=request, format=format),
        'siteprivileges': reverse('siteprivilege-list', request=request, format=format),
        'slicedeployments': reverse('slicedeployment-list', request=request, format=format),
        'userdeployments': reverse('userdeployment-list', request=request, format=format),
        'accounts': reverse('account-list', request=request, format=format),
        'networkparametertypes': reverse('networkparametertype-list', request=request, format=format),
        'sitecredentials': reverse('sitecredential-list', request=request, format=format),
        'deploymentprivileges': reverse('deploymentprivilege-list', request=request, format=format),
        'imagedeployments': reverse('imagedeployment-list', request=request, format=format),
        'deploymentroles': reverse('deploymentrole-list', request=request, format=format),
        'usercredentials': reverse('usercredential-list', request=request, format=format),
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
        fields = ('id','created','updated','enacted','backend_status','deleted','name','value','service',)

class ServiceAttributeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ServiceAttribute
        fields = ('id','created','updated','enacted','backend_status','deleted','name','value','service',)




class ImageSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Image
        fields = ('id','created','updated','enacted','backend_status','deleted','name','disk_format','container_format','path',)

class ImageIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Image
        fields = ('id','created','updated','enacted','backend_status','deleted','name','disk_format','container_format','path',)




class NetworkParameterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkParameter
        fields = ('id','created','updated','enacted','backend_status','deleted','parameter','value','content_type','object_id',)

class NetworkParameterIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkParameter
        fields = ('id','created','updated','enacted','backend_status','deleted','parameter','value','content_type','object_id',)




class SiteSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Site
        fields = ('id','created','updated','enacted','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)

class SiteIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Site
        fields = ('id','created','updated','enacted','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)




class SliceRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)

class SliceRoleIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)




class TagSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Tag
        fields = ('id','created','updated','enacted','backend_status','deleted','service','name','value','content_type','object_id',)

class TagIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Tag
        fields = ('id','created','updated','enacted','backend_status','deleted','service','name','value','content_type','object_id',)




class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Invoice
        fields = ('id','created','updated','enacted','backend_status','deleted','date','account',)

class InvoiceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Invoice
        fields = ('id','created','updated','enacted','backend_status','deleted','date','account',)




class SlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SlicePrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','slice','role',)

class SlicePrivilegeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SlicePrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','slice','role',)




class PlanetStackRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStackRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)

class PlanetStackRoleIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStackRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)




class NetworkSliverSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkSliver
        fields = ('id','created','updated','enacted','backend_status','deleted','network','sliver','ip','port_id',)

class NetworkSliverIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkSliver
        fields = ('id','created','updated','enacted','backend_status','deleted','network','sliver','ip','port_id',)




class NetworkDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','network','deployment','net_id','router_id','subnet_id','subnet',)

class NetworkDeploymentsIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','network','deployment','net_id','router_id','subnet_id','subnet',)




class FlavorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Flavor
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','flavor','order','default',)

class FlavorIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Flavor
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','flavor','order','default',)




class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Project
        fields = ('id','created','updated','enacted','backend_status','deleted','name',)

class ProjectIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Project
        fields = ('id','created','updated','enacted','backend_status','deleted','name',)




class SliceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    availableNetworks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    class Meta:
        model = Slice
        fields = ('id','created','updated','enacted','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','imagePreference','service','network','mountDataSets','serviceClass','creator','networks','availableNetworks','networks','networks',)

class SliceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    availableNetworks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    class Meta:
        model = Slice
        fields = ('id','created','updated','enacted','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','imagePreference','service','network','mountDataSets','serviceClass','creator','networks','availableNetworks','networks','networks',)




class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    availableRouters = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    class Meta:
        model = Network
        fields = ('id','created','updated','enacted','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','topologyParameters','controllerUrl','controllerParameters','network_id','router_id','subnet_id','routers','availableRouters','routers','routers',)

class NetworkIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    availableRouters = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    class Meta:
        model = Network
        fields = ('id','created','updated','enacted','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','topologyParameters','controllerUrl','controllerParameters','network_id','router_id','subnet_id','routers','availableRouters','routers','routers',)




class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Service
        fields = ('id','created','updated','enacted','backend_status','deleted','description','enabled','name','versionNumber','published',)

class ServiceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Service
        fields = ('id','created','updated','enacted','backend_status','deleted','description','enabled','name','versionNumber','published',)




class ServiceClassSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ServiceClass
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)

class ServiceClassIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ServiceClass
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)




class PlanetStackSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStack
        fields = ('id','created','updated','enacted','backend_status','deleted','description',)

class PlanetStackIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStack
        fields = ('id','created','updated','enacted','backend_status','deleted','description',)




class ChargeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Charge
        fields = ('id','created','updated','enacted','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)

class ChargeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Charge
        fields = ('id','created','updated','enacted','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)




class RoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Role
        fields = ('id','created','updated','enacted','backend_status','deleted','role_type','role','description','content_type',)

class RoleIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Role
        fields = ('id','created','updated','enacted','backend_status','deleted','role_type','role','description','content_type',)




class UsableObjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UsableObject
        fields = ('id','created','updated','enacted','backend_status','deleted','name',)

class UsableObjectIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UsableObject
        fields = ('id','created','updated','enacted','backend_status','deleted','name',)




class SiteRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)

class SiteRoleIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)




class SliceCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','key_id','enc_value',)

class SliceCredentialIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','key_id','enc_value',)




class SliverSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    class Meta:
        model = Sliver
        fields = ('id','created','updated','enacted','backend_status','deleted','instance_id','name','instance_name','ip','image','creator','slice','node','deploymentNetwork','numberCores','flavor','userData','networks','networks',)

class SliverIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    class Meta:
        model = Sliver
        fields = ('id','created','updated','enacted','backend_status','deleted','instance_id','name','instance_name','ip','image','creator','slice','node','deploymentNetwork','numberCores','flavor','userData','networks','networks',)




class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Node
        fields = ('id','created','updated','enacted','backend_status','deleted','name','site','deployment',)

class NodeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Node
        fields = ('id','created','updated','enacted','backend_status','deleted','name','site','deployment',)




class DashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DashboardView
        fields = ('id','created','updated','enacted','backend_status','deleted','name','url',)

class DashboardViewIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DashboardView
        fields = ('id','created','updated','enacted','backend_status','deleted','name','url',)




class ReservedResourceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ReservedResource
        fields = ('id','created','updated','enacted','backend_status','deleted','sliver','resource','quantity','reservationSet',)

class ReservedResourceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ReservedResource
        fields = ('id','created','updated','enacted','backend_status','deleted','sliver','resource','quantity','reservationSet',)




class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Payment
        fields = ('id','created','updated','enacted','backend_status','deleted','account','amount','date',)

class PaymentIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Payment
        fields = ('id','created','updated','enacted','backend_status','deleted','account','amount','date',)




class NetworkSliceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkSlice
        fields = ('id','created','updated','enacted','backend_status','deleted','network','slice',)

class NetworkSliceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkSlice
        fields = ('id','created','updated','enacted','backend_status','deleted','network','slice',)




class UserDashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserDashboardView
        fields = ('id','created','updated','enacted','backend_status','deleted','user','dashboardView','order',)

class UserDashboardViewIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserDashboardView
        fields = ('id','created','updated','enacted','backend_status','deleted','user','dashboardView','order',)




class SiteDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','site','deployment','tenant_id',)

class SiteDeploymentsIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','site','deployment','tenant_id',)




class PlanetStackPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStackPrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','planetstack','role',)

class PlanetStackPrivilegeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = PlanetStackPrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','planetstack','role',)




class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = User
        fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','backend_status','deleted','timezone',)

class UserIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = User
        fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','backend_status','deleted','timezone',)




class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
    flavors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='flavor-detail')
    
    
    
    flavors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='flavor-detail')
    
    
    class Meta:
        model = Deployment
        fields = ('id','created','updated','enacted','backend_status','deleted','name','admin_user','admin_password','admin_tenant','auth_url','backend_type','availability_zone','accessControl','sites','sites','flavors','flavors',)

class DeploymentIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
    flavors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='flavor-detail')
    
    
    
    flavors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='flavor-detail')
    
    
    class Meta:
        model = Deployment
        fields = ('id','created','updated','enacted','backend_status','deleted','name','admin_user','admin_password','admin_tenant','auth_url','backend_type','availability_zone','accessControl','sites','sites','flavors','flavors',)




class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Reservation
        fields = ('id','created','updated','enacted','backend_status','deleted','startTime','slice','duration',)

class ReservationIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Reservation
        fields = ('id','created','updated','enacted','backend_status','deleted','startTime','slice','duration',)




class SitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SitePrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','site','role',)

class SitePrivilegeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SitePrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','site','role',)




class SliceDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','deployment','tenant_id','network_id','router_id','subnet_id',)

class SliceDeploymentsIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceDeployments
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','deployment','tenant_id','network_id','router_id','subnet_id',)




class UserDeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserDeployment
        fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','kuser_id',)

class UserDeploymentIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserDeployment
        fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','kuser_id',)




class AccountSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Account
        fields = ('id','created','updated','enacted','backend_status','deleted','site',)

class AccountIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Account
        fields = ('id','created','updated','enacted','backend_status','deleted','site',)




class NetworkParameterTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkParameterType
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description',)

class NetworkParameterTypeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkParameterType
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description',)




class SiteCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','site','name','key_id','enc_value',)

class SiteCredentialIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SiteCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','site','name','key_id','enc_value',)




class DeploymentPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DeploymentPrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','role',)

class DeploymentPrivilegeIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DeploymentPrivilege
        fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','role',)




class ImageDeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ImageDeployment
        fields = ('id','created','updated','enacted','backend_status','deleted','image','deployment','glance_image_id',)

class ImageDeploymentIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ImageDeployment
        fields = ('id','created','updated','enacted','backend_status','deleted','image','deployment','glance_image_id',)




class DeploymentRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DeploymentRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)

class DeploymentRoleIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = DeploymentRole
        fields = ('id','created','updated','enacted','backend_status','deleted','role',)




class UserCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','user','name','key_id','enc_value',)

class UserCredentialIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = UserCredential
        fields = ('id','created','updated','enacted','backend_status','deleted','user','name','key_id','enc_value',)




class SliceTagSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceTag
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','value',)

class SliceTagIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = SliceTag
        fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','value',)




class NetworkTemplateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkTemplate
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','guaranteedBandwidth','visibility','translation','sharedNetworkName','sharedNetworkId','topologyKind','controllerKind',)

class NetworkTemplateIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = NetworkTemplate
        fields = ('id','created','updated','enacted','backend_status','deleted','name','description','guaranteedBandwidth','visibility','translation','sharedNetworkName','sharedNetworkId','topologyKind','controllerKind',)




class RouterSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Router
        fields = ('id','created','updated','enacted','backend_status','deleted','name','owner',)

class RouterIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Router
        fields = ('id','created','updated','enacted','backend_status','deleted','name','owner',)




class ServiceResourceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ServiceResource
        fields = ('id','created','updated','enacted','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)

class ServiceResourceIdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = ServiceResource
        fields = ('id','created','updated','enacted','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)




serializerLookUp = { 

                 ServiceAttribute: ServiceAttributeSerializer,

                 Image: ImageSerializer,

                 NetworkParameter: NetworkParameterSerializer,

                 Site: SiteSerializer,

                 SliceRole: SliceRoleSerializer,

                 Tag: TagSerializer,

                 Invoice: InvoiceSerializer,

                 SlicePrivilege: SlicePrivilegeSerializer,

                 PlanetStackRole: PlanetStackRoleSerializer,

                 NetworkSliver: NetworkSliverSerializer,

                 NetworkDeployments: NetworkDeploymentsSerializer,

                 Flavor: FlavorSerializer,

                 Project: ProjectSerializer,

                 Slice: SliceSerializer,

                 Network: NetworkSerializer,

                 Service: ServiceSerializer,

                 ServiceClass: ServiceClassSerializer,

                 PlanetStack: PlanetStackSerializer,

                 Charge: ChargeSerializer,

                 Role: RoleSerializer,

                 UsableObject: UsableObjectSerializer,

                 SiteRole: SiteRoleSerializer,

                 SliceCredential: SliceCredentialSerializer,

                 Sliver: SliverSerializer,

                 Node: NodeSerializer,

                 DashboardView: DashboardViewSerializer,

                 ReservedResource: ReservedResourceSerializer,

                 Payment: PaymentSerializer,

                 NetworkSlice: NetworkSliceSerializer,

                 UserDashboardView: UserDashboardViewSerializer,

                 SiteDeployments: SiteDeploymentsSerializer,

                 PlanetStackPrivilege: PlanetStackPrivilegeSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 Reservation: ReservationSerializer,

                 SitePrivilege: SitePrivilegeSerializer,

                 SliceDeployments: SliceDeploymentsSerializer,

                 UserDeployment: UserDeploymentSerializer,

                 Account: AccountSerializer,

                 NetworkParameterType: NetworkParameterTypeSerializer,

                 SiteCredential: SiteCredentialSerializer,

                 DeploymentPrivilege: DeploymentPrivilegeSerializer,

                 ImageDeployment: ImageDeploymentSerializer,

                 DeploymentRole: DeploymentRoleSerializer,

                 UserCredential: UserCredentialSerializer,

                 SliceTag: SliceTagSerializer,

                 NetworkTemplate: NetworkTemplateSerializer,

                 Router: RouterSerializer,

                 ServiceResource: ServiceResourceSerializer,

                 None: None,
                }

class PlanetStackRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

    # To handle fine-grained field permissions, we have to check can_update
    # the object has been updated but before it has been saved.

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        self.object = self.get_object_or_none()

        serializer = self.get_serializer(self.object, data=request.DATA,
                                         files=request.FILES, partial=partial)

        if not serializer.is_valid():
            print "UpdateModelMixin: not serializer.is_valid"
            print serializer.errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.pre_save(serializer.object)
        except ValidationError as err:
            # full_clean on model instance may be called in pre_save,
            # so we have to handle eventual errors.
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)

        if serializer.object is not None:
            if not serializer.object.can_update(request.user):
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if self.object is None:
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        self.object = serializer.save(force_update=True)
        self.post_save(self.object, created=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(generics.RetrieveUpdateDestroyAPIView, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Based on core/views/*.py


class ServiceAttributeList(generics.ListCreateAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer
    id_serializer_class = ServiceAttributeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','value','service',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return ServiceAttribute.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceAttributeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ServiceAttributeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ServiceAttributeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer
    id_serializer_class = ServiceAttributeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return ServiceAttribute.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ServiceAttributeNew(GenericAPIView):
    serializer_class = ServiceAttributeSerializer
    id_serializer_class = ServiceAttributeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = ServiceAttribute()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','disk_format','container_format','path',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Image.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ImageList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ImageList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ImageDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Image.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ImageNew(GenericAPIView):
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Image()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkParameterList(generics.ListCreateAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','parameter','value','content_type','object_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkParameter.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkParameterList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkParameterList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkParameterDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkParameter.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkParameterNew(GenericAPIView):
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkParameter()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SiteList(generics.ListCreateAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Site.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SiteList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SiteDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Site.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SiteNew(GenericAPIView):
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Site()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliceRoleList(generics.ListCreateAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SliceRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceRoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliceRoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliceRoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SliceRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliceRoleNew(GenericAPIView):
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SliceRole()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','service','name','value','content_type','object_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Tag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(TagList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(TagList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class TagDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Tag.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class TagNew(GenericAPIView):
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Tag()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class InvoiceList(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer
    id_serializer_class = InvoiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','date','account',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Invoice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(InvoiceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(InvoiceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class InvoiceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer
    id_serializer_class = InvoiceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Invoice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class InvoiceNew(GenericAPIView):
    serializer_class = InvoiceSerializer
    id_serializer_class = InvoiceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Invoice()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SlicePrivilegeList(generics.ListCreateAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','slice','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SlicePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SlicePrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SlicePrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SlicePrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SlicePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SlicePrivilegeNew(GenericAPIView):
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SlicePrivilege()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class PlanetStackRoleList(generics.ListCreateAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer
    id_serializer_class = PlanetStackRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return PlanetStackRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackRoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(PlanetStackRoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class PlanetStackRoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer
    id_serializer_class = PlanetStackRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return PlanetStackRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class PlanetStackRoleNew(GenericAPIView):
    serializer_class = PlanetStackRoleSerializer
    id_serializer_class = PlanetStackRoleIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = PlanetStackRole()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkSliverList(generics.ListCreateAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer
    id_serializer_class = NetworkSliverIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','network','sliver','ip','port_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkSliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkSliverList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkSliverList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkSliverDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer
    id_serializer_class = NetworkSliverIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkSliver.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkSliverNew(GenericAPIView):
    serializer_class = NetworkSliverSerializer
    id_serializer_class = NetworkSliverIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkSliver()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkDeploymentsList(generics.ListCreateAPIView):
    queryset = NetworkDeployments.objects.select_related().all()
    serializer_class = NetworkDeploymentsSerializer
    id_serializer_class = NetworkDeploymentsIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','network','deployment','net_id','router_id','subnet_id','subnet',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkDeploymentsList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkDeploymentsList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkDeploymentsDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkDeployments.objects.select_related().all()
    serializer_class = NetworkDeploymentsSerializer
    id_serializer_class = NetworkDeploymentsIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkDeployments.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkDeploymentsNew(GenericAPIView):
    serializer_class = NetworkDeploymentsSerializer
    id_serializer_class = NetworkDeploymentsIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkDeployments()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class FlavorList(generics.ListCreateAPIView):
    queryset = Flavor.objects.select_related().all()
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','description','flavor','order','default',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Flavor.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(FlavorList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(FlavorList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class FlavorDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Flavor.objects.select_related().all()
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Flavor.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class FlavorNew(GenericAPIView):
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Flavor()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer
    id_serializer_class = ProjectIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Project.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ProjectList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ProjectList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ProjectDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer
    id_serializer_class = ProjectIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Project.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ProjectNew(GenericAPIView):
    serializer_class = ProjectSerializer
    id_serializer_class = ProjectIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Project()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','imagePreference','service','network','mountDataSets','serviceClass','creator','networks','availableNetworks','networks','networks',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Slice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Slice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliceNew(GenericAPIView):
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Slice()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkList(generics.ListCreateAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteedBandwidth','permitAllSlices','topologyParameters','controllerUrl','controllerParameters','network_id','router_id','subnet_id','routers','availableRouters','routers','routers',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Network.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Network.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkNew(GenericAPIView):
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Network()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','description','enabled','name','versionNumber','published',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Service.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ServiceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ServiceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Service.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ServiceNew(GenericAPIView):
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Service()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ServiceClassList(generics.ListCreateAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer
    id_serializer_class = ServiceClassIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return ServiceClass.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceClassList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ServiceClassList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ServiceClassDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer
    id_serializer_class = ServiceClassIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return ServiceClass.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ServiceClassNew(GenericAPIView):
    serializer_class = ServiceClassSerializer
    id_serializer_class = ServiceClassIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = ServiceClass()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class PlanetStackList(generics.ListCreateAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer
    id_serializer_class = PlanetStackIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','description',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return PlanetStack.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(PlanetStackList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class PlanetStackDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer
    id_serializer_class = PlanetStackIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return PlanetStack.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class PlanetStackNew(GenericAPIView):
    serializer_class = PlanetStackSerializer
    id_serializer_class = PlanetStackIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = PlanetStack()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ChargeList(generics.ListCreateAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer
    id_serializer_class = ChargeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Charge.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ChargeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ChargeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ChargeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer
    id_serializer_class = ChargeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Charge.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ChargeNew(GenericAPIView):
    serializer_class = ChargeSerializer
    id_serializer_class = ChargeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Charge()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','role_type','role','description','content_type',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Role.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(RoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(RoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class RoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Role.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class RoleNew(GenericAPIView):
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Role()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class UsableObjectList(generics.ListCreateAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer
    id_serializer_class = UsableObjectIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return UsableObject.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UsableObjectList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(UsableObjectList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class UsableObjectDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer
    id_serializer_class = UsableObjectIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return UsableObject.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class UsableObjectNew(GenericAPIView):
    serializer_class = UsableObjectSerializer
    id_serializer_class = UsableObjectIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = UsableObject()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SiteRoleList(generics.ListCreateAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SiteRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteRoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SiteRoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SiteRoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SiteRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SiteRoleNew(GenericAPIView):
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SiteRole()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliceCredentialList(generics.ListCreateAPIView):
    queryset = SliceCredential.objects.select_related().all()
    serializer_class = SliceCredentialSerializer
    id_serializer_class = SliceCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SliceCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceCredentialList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliceCredentialList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliceCredentialDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SliceCredential.objects.select_related().all()
    serializer_class = SliceCredentialSerializer
    id_serializer_class = SliceCredentialIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SliceCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliceCredentialNew(GenericAPIView):
    serializer_class = SliceCredentialSerializer
    id_serializer_class = SliceCredentialIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SliceCredential()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer
    id_serializer_class = SliverIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','instance_id','name','instance_name','ip','image','creator','slice','node','deploymentNetwork','numberCores','flavor','userData','networks','networks',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Sliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliverList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliverList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliverDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer
    id_serializer_class = SliverIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Sliver.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliverNew(GenericAPIView):
    serializer_class = SliverSerializer
    id_serializer_class = SliverIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Sliver()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','site','deployment',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Node.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NodeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NodeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NodeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Node.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NodeNew(GenericAPIView):
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Node()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class DashboardViewList(generics.ListCreateAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','url',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return DashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DashboardViewList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(DashboardViewList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class DashboardViewDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return DashboardView.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class DashboardViewNew(GenericAPIView):
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = DashboardView()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ReservedResourceList(generics.ListCreateAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer
    id_serializer_class = ReservedResourceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','sliver','resource','quantity','reservationSet',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return ReservedResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ReservedResourceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ReservedResourceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ReservedResourceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer
    id_serializer_class = ReservedResourceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return ReservedResource.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ReservedResourceNew(GenericAPIView):
    serializer_class = ReservedResourceSerializer
    id_serializer_class = ReservedResourceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = ReservedResource()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer
    id_serializer_class = PaymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','account','amount','date',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Payment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PaymentList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(PaymentList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class PaymentDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer
    id_serializer_class = PaymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Payment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class PaymentNew(GenericAPIView):
    serializer_class = PaymentSerializer
    id_serializer_class = PaymentIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Payment()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkSliceList(generics.ListCreateAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','network','slice',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkSlice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkSliceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkSliceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkSliceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkSlice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkSliceNew(GenericAPIView):
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkSlice()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class UserDashboardViewList(generics.ListCreateAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','dashboardView','order',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return UserDashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserDashboardViewList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(UserDashboardViewList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class UserDashboardViewDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return UserDashboardView.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class UserDashboardViewNew(GenericAPIView):
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = UserDashboardView()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SiteDeploymentsList(generics.ListCreateAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer
    id_serializer_class = SiteDeploymentsIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','site','deployment','tenant_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SiteDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteDeploymentsList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SiteDeploymentsList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SiteDeploymentsDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SiteDeployments.objects.select_related().all()
    serializer_class = SiteDeploymentsSerializer
    id_serializer_class = SiteDeploymentsIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SiteDeployments.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SiteDeploymentsNew(GenericAPIView):
    serializer_class = SiteDeploymentsSerializer
    id_serializer_class = SiteDeploymentsIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SiteDeployments()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class PlanetStackPrivilegeList(generics.ListCreateAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer
    id_serializer_class = PlanetStackPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','planetstack','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return PlanetStackPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(PlanetStackPrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(PlanetStackPrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class PlanetStackPrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer
    id_serializer_class = PlanetStackPrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return PlanetStackPrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class PlanetStackPrivilegeNew(GenericAPIView):
    serializer_class = PlanetStackPrivilegeSerializer
    id_serializer_class = PlanetStackPrivilegeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = PlanetStackPrivilege()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','created','updated','enacted','backend_status','deleted','timezone',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return User.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(UserList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class UserDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return User.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class UserNew(GenericAPIView):
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = User()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','admin_user','admin_password','admin_tenant','auth_url','backend_type','availability_zone','accessControl','sites','sites','flavors','flavors',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Deployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(DeploymentList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class DeploymentDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Deployment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class DeploymentNew(GenericAPIView):
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Deployment()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer
    id_serializer_class = ReservationIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','startTime','slice','duration',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Reservation.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ReservationList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ReservationList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ReservationDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer
    id_serializer_class = ReservationIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Reservation.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ReservationNew(GenericAPIView):
    serializer_class = ReservationSerializer
    id_serializer_class = ReservationIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Reservation()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SitePrivilegeList(generics.ListCreateAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','site','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SitePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SitePrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SitePrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SitePrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SitePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SitePrivilegeNew(GenericAPIView):
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SitePrivilege()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliceDeploymentsList(generics.ListCreateAPIView):
    queryset = SliceDeployments.objects.select_related().all()
    serializer_class = SliceDeploymentsSerializer
    id_serializer_class = SliceDeploymentsIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','slice','deployment','tenant_id','network_id','router_id','subnet_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SliceDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceDeploymentsList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliceDeploymentsList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliceDeploymentsDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SliceDeployments.objects.select_related().all()
    serializer_class = SliceDeploymentsSerializer
    id_serializer_class = SliceDeploymentsIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SliceDeployments.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliceDeploymentsNew(GenericAPIView):
    serializer_class = SliceDeploymentsSerializer
    id_serializer_class = SliceDeploymentsIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SliceDeployments()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class UserDeploymentList(generics.ListCreateAPIView):
    queryset = UserDeployment.objects.select_related().all()
    serializer_class = UserDeploymentSerializer
    id_serializer_class = UserDeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','kuser_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return UserDeployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserDeploymentList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(UserDeploymentList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class UserDeploymentDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = UserDeployment.objects.select_related().all()
    serializer_class = UserDeploymentSerializer
    id_serializer_class = UserDeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return UserDeployment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class UserDeploymentNew(GenericAPIView):
    serializer_class = UserDeploymentSerializer
    id_serializer_class = UserDeploymentIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = UserDeployment()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer
    id_serializer_class = AccountIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','site',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Account.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(AccountList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(AccountList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class AccountDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer
    id_serializer_class = AccountIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Account.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class AccountNew(GenericAPIView):
    serializer_class = AccountSerializer
    id_serializer_class = AccountIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Account()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkParameterTypeList(generics.ListCreateAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','description',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkParameterType.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkParameterTypeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkParameterTypeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkParameterTypeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkParameterType.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkParameterTypeNew(GenericAPIView):
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkParameterType()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SiteCredentialList(generics.ListCreateAPIView):
    queryset = SiteCredential.objects.select_related().all()
    serializer_class = SiteCredentialSerializer
    id_serializer_class = SiteCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','site','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SiteCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteCredentialList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SiteCredentialList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SiteCredentialDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SiteCredential.objects.select_related().all()
    serializer_class = SiteCredentialSerializer
    id_serializer_class = SiteCredentialIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SiteCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SiteCredentialNew(GenericAPIView):
    serializer_class = SiteCredentialSerializer
    id_serializer_class = SiteCredentialIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SiteCredential()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class DeploymentPrivilegeList(generics.ListCreateAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','deployment','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return DeploymentPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentPrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(DeploymentPrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class DeploymentPrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return DeploymentPrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class DeploymentPrivilegeNew(GenericAPIView):
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = DeploymentPrivilege()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ImageDeploymentList(generics.ListCreateAPIView):
    queryset = ImageDeployment.objects.select_related().all()
    serializer_class = ImageDeploymentSerializer
    id_serializer_class = ImageDeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','image','deployment','glance_image_id',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return ImageDeployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ImageDeploymentList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ImageDeploymentList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ImageDeploymentDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ImageDeployment.objects.select_related().all()
    serializer_class = ImageDeploymentSerializer
    id_serializer_class = ImageDeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return ImageDeployment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ImageDeploymentNew(GenericAPIView):
    serializer_class = ImageDeploymentSerializer
    id_serializer_class = ImageDeploymentIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = ImageDeployment()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class DeploymentRoleList(generics.ListCreateAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return DeploymentRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(DeploymentRoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(DeploymentRoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class DeploymentRoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return DeploymentRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class DeploymentRoleNew(GenericAPIView):
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = DeploymentRole()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class UserCredentialList(generics.ListCreateAPIView):
    queryset = UserCredential.objects.select_related().all()
    serializer_class = UserCredentialSerializer
    id_serializer_class = UserCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','user','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return UserCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(UserCredentialList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(UserCredentialList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class UserCredentialDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = UserCredential.objects.select_related().all()
    serializer_class = UserCredentialSerializer
    id_serializer_class = UserCredentialIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return UserCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class UserCredentialNew(GenericAPIView):
    serializer_class = UserCredentialSerializer
    id_serializer_class = UserCredentialIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = UserCredential()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class SliceTagList(generics.ListCreateAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer
    id_serializer_class = SliceTagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','slice','name','value',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return SliceTag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceTagList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SliceTagList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SliceTagDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer
    id_serializer_class = SliceTagIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return SliceTag.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class SliceTagNew(GenericAPIView):
    serializer_class = SliceTagSerializer
    id_serializer_class = SliceTagIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = SliceTag()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class NetworkTemplateList(generics.ListCreateAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','description','guaranteedBandwidth','visibility','translation','sharedNetworkName','sharedNetworkId','topologyKind','controllerKind',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return NetworkTemplate.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(NetworkTemplateList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(NetworkTemplateList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class NetworkTemplateDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return NetworkTemplate.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class NetworkTemplateNew(GenericAPIView):
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = NetworkTemplate()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class RouterList(generics.ListCreateAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer
    id_serializer_class = RouterIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','name','owner',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return Router.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(RouterList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(RouterList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class RouterDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer
    id_serializer_class = RouterIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return Router.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class RouterNew(GenericAPIView):
    serializer_class = RouterSerializer
    id_serializer_class = RouterIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = Router()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



class ServiceResourceList(generics.ListCreateAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer
    id_serializer_class = ServiceResourceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return ServiceResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            raise Exception("failed serializer.is_valid: " + str(serializer.errors))
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ServiceResourceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ServiceResourceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ServiceResourceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer
    id_serializer_class = ServiceResourceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return ServiceResource.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

"""
    XXX smbaker: my intent was to create a view that would return 'new' objects
    filled with defaults. I solved it another way, so this code may soon be
    abandoned.

class ServiceResourceNew(GenericAPIView):
    serializer_class = ServiceResourceSerializer
    id_serializer_class = ServiceResourceIdSerializer

    def get(self, request, *args, **kwargs):
        return self.makenew(request, *args, **kwargs)

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def makenew(self, request, *args, **kwargs):
        obj = ServiceResource()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
"""



