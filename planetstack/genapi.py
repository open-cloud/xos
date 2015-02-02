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
from rest_framework.exceptions import PermissionDenied as RestFrameworkPermissionDenied

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    IdField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    IdField = serializers.Field

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
    
        url(r'plstackapi/controllerimages/$', ControllerImagesList.as_view(), name='controllerimages-list'),
        url(r'plstackapi/controllerimages/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerImagesDetail.as_view(), name ='controllerimages-detail'),
    
        url(r'plstackapi/controllersiteprivileges/$', ControllerSitePrivilegeList.as_view(), name='controllersiteprivilege-list'),
        url(r'plstackapi/controllersiteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSitePrivilegeDetail.as_view(), name ='controllersiteprivilege-detail'),
    
        url(r'plstackapi/images/$', ImageList.as_view(), name='image-list'),
        url(r'plstackapi/images/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDetail.as_view(), name ='image-detail'),
    
        url(r'plstackapi/networkparameters/$', NetworkParameterList.as_view(), name='networkparameter-list'),
        url(r'plstackapi/networkparameters/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterDetail.as_view(), name ='networkparameter-detail'),
    
        url(r'plstackapi/sites/$', SiteList.as_view(), name='site-list'),
        url(r'plstackapi/sites/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDetail.as_view(), name ='site-detail'),
    
        url(r'plstackapi/slice_roles/$', SliceRoleList.as_view(), name='slicerole-list'),
        url(r'plstackapi/slice_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceRoleDetail.as_view(), name ='slicerole-detail'),
    
        url(r'plstackapi/tags/$', TagList.as_view(), name='tag-list'),
        url(r'plstackapi/tags/(?P<pk>[a-zA-Z0-9\-]+)/$', TagDetail.as_view(), name ='tag-detail'),
    
        url(r'plstackapi/invoices/$', InvoiceList.as_view(), name='invoice-list'),
        url(r'plstackapi/invoices/(?P<pk>[a-zA-Z0-9\-]+)/$', InvoiceDetail.as_view(), name ='invoice-detail'),
    
        url(r'plstackapi/slice_privileges/$', SlicePrivilegeList.as_view(), name='sliceprivilege-list'),
        url(r'plstackapi/slice_privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SlicePrivilegeDetail.as_view(), name ='sliceprivilege-detail'),
    
        url(r'plstackapi/planetstackroles/$', PlanetStackRoleList.as_view(), name='planetstackrole-list'),
        url(r'plstackapi/planetstackroles/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackRoleDetail.as_view(), name ='planetstackrole-detail'),
    
        url(r'plstackapi/networkslivers/$', NetworkSliverList.as_view(), name='networksliver-list'),
        url(r'plstackapi/networkslivers/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliverDetail.as_view(), name ='networksliver-detail'),
    
        url(r'plstackapi/flavors/$', FlavorList.as_view(), name='flavor-list'),
        url(r'plstackapi/flavors/(?P<pk>[a-zA-Z0-9\-]+)/$', FlavorDetail.as_view(), name ='flavor-detail'),
    
        url(r'plstackapi/controllersites/$', ControllerSiteList.as_view(), name='controllersite-list'),
        url(r'plstackapi/controllersites/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSiteDetail.as_view(), name ='controllersite-detail'),
    
        url(r'plstackapi/projects/$', ProjectList.as_view(), name='project-list'),
        url(r'plstackapi/projects/(?P<pk>[a-zA-Z0-9\-]+)/$', ProjectDetail.as_view(), name ='project-detail'),
    
        url(r'plstackapi/slices/$', SliceList.as_view(), name='slice-list'),
        url(r'plstackapi/slices/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceDetail.as_view(), name ='slice-detail'),
    
        url(r'plstackapi/networks/$', NetworkList.as_view(), name='network-list'),
        url(r'plstackapi/networks/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkDetail.as_view(), name ='network-detail'),
    
        url(r'plstackapi/services/$', ServiceList.as_view(), name='service-list'),
        url(r'plstackapi/services/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDetail.as_view(), name ='service-detail'),
    
        url(r'plstackapi/serviceclasses/$', ServiceClassList.as_view(), name='serviceclass-list'),
        url(r'plstackapi/serviceclasses/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceClassDetail.as_view(), name ='serviceclass-detail'),
    
        url(r'plstackapi/planetstacks/$', PlanetStackList.as_view(), name='planetstack-list'),
        url(r'plstackapi/planetstacks/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackDetail.as_view(), name ='planetstack-detail'),
    
        url(r'plstackapi/charges/$', ChargeList.as_view(), name='charge-list'),
        url(r'plstackapi/charges/(?P<pk>[a-zA-Z0-9\-]+)/$', ChargeDetail.as_view(), name ='charge-detail'),
    
        url(r'plstackapi/roles/$', RoleList.as_view(), name='role-list'),
        url(r'plstackapi/roles/(?P<pk>[a-zA-Z0-9\-]+)/$', RoleDetail.as_view(), name ='role-detail'),
    
        url(r'plstackapi/usableobjects/$', UsableObjectList.as_view(), name='usableobject-list'),
        url(r'plstackapi/usableobjects/(?P<pk>[a-zA-Z0-9\-]+)/$', UsableObjectDetail.as_view(), name ='usableobject-detail'),
    
        url(r'plstackapi/site_roles/$', SiteRoleList.as_view(), name='siterole-list'),
        url(r'plstackapi/site_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteRoleDetail.as_view(), name ='siterole-detail'),
    
        url(r'plstackapi/slicecredentials/$', SliceCredentialList.as_view(), name='slicecredential-list'),
        url(r'plstackapi/slicecredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceCredentialDetail.as_view(), name ='slicecredential-detail'),
    
        url(r'plstackapi/slivers/$', SliverList.as_view(), name='sliver-list'),
        url(r'plstackapi/slivers/(?P<pk>[a-zA-Z0-9\-]+)/$', SliverDetail.as_view(), name ='sliver-detail'),
    
        url(r'plstackapi/nodes/$', NodeList.as_view(), name='node-list'),
        url(r'plstackapi/nodes/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeDetail.as_view(), name ='node-detail'),
    
        url(r'plstackapi/dashboardviews/$', DashboardViewList.as_view(), name='dashboardview-list'),
        url(r'plstackapi/dashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', DashboardViewDetail.as_view(), name ='dashboardview-detail'),
    
        url(r'plstackapi/controllernetworks/$', ControllerNetworkList.as_view(), name='controllernetwork-list'),
        url(r'plstackapi/controllernetworks/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerNetworkDetail.as_view(), name ='controllernetwork-detail'),
    
        url(r'plstackapi/imagedeploymentses/$', ImageDeploymentsList.as_view(), name='imagedeployments-list'),
        url(r'plstackapi/imagedeploymentses/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDeploymentsDetail.as_view(), name ='imagedeployments-detail'),
    
        url(r'plstackapi/controllerusers/$', ControllerUserList.as_view(), name='controlleruser-list'),
        url(r'plstackapi/controllerusers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerUserDetail.as_view(), name ='controlleruser-detail'),
    
        url(r'plstackapi/reservedresources/$', ReservedResourceList.as_view(), name='reservedresource-list'),
        url(r'plstackapi/reservedresources/(?P<pk>[a-zA-Z0-9\-]+)/$', ReservedResourceDetail.as_view(), name ='reservedresource-detail'),
    
        url(r'plstackapi/payments/$', PaymentList.as_view(), name='payment-list'),
        url(r'plstackapi/payments/(?P<pk>[a-zA-Z0-9\-]+)/$', PaymentDetail.as_view(), name ='payment-detail'),
    
        url(r'plstackapi/networkslices/$', NetworkSliceList.as_view(), name='networkslice-list'),
        url(r'plstackapi/networkslices/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliceDetail.as_view(), name ='networkslice-detail'),
    
        url(r'plstackapi/userdashboardviews/$', UserDashboardViewList.as_view(), name='userdashboardview-list'),
        url(r'plstackapi/userdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDashboardViewDetail.as_view(), name ='userdashboardview-detail'),
    
        url(r'plstackapi/controllers/$', ControllerList.as_view(), name='controller-list'),
        url(r'plstackapi/controllers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDetail.as_view(), name ='controller-detail'),
    
        url(r'plstackapi/planetstackprivileges/$', PlanetStackPrivilegeList.as_view(), name='planetstackprivilege-list'),
        url(r'plstackapi/planetstackprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', PlanetStackPrivilegeDetail.as_view(), name ='planetstackprivilege-detail'),
    
        url(r'plstackapi/users/$', UserList.as_view(), name='user-list'),
        url(r'plstackapi/users/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDetail.as_view(), name ='user-detail'),
    
        url(r'plstackapi/deployments/$', DeploymentList.as_view(), name='deployment-list'),
        url(r'plstackapi/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name ='deployment-detail'),
    
        url(r'plstackapi/reservations/$', ReservationList.as_view(), name='reservation-list'),
        url(r'plstackapi/reservations/(?P<pk>[a-zA-Z0-9\-]+)/$', ReservationDetail.as_view(), name ='reservation-detail'),
    
        url(r'plstackapi/siteprivileges/$', SitePrivilegeList.as_view(), name='siteprivilege-list'),
        url(r'plstackapi/siteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SitePrivilegeDetail.as_view(), name ='siteprivilege-detail'),
    
        url(r'plstackapi/controllerslices/$', ControllerSliceList.as_view(), name='controllerslice-list'),
        url(r'plstackapi/controllerslices/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSliceDetail.as_view(), name ='controllerslice-detail'),
    
        url(r'plstackapi/controllerdashboardviews/$', ControllerDashboardViewList.as_view(), name='controllerdashboardview-list'),
        url(r'plstackapi/controllerdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDashboardViewDetail.as_view(), name ='controllerdashboardview-detail'),
    
        url(r'plstackapi/accounts/$', AccountList.as_view(), name='account-list'),
        url(r'plstackapi/accounts/(?P<pk>[a-zA-Z0-9\-]+)/$', AccountDetail.as_view(), name ='account-detail'),
    
        url(r'plstackapi/controllerroles/$', ControllerRoleList.as_view(), name='controllerrole-list'),
        url(r'plstackapi/controllerroles/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerRoleDetail.as_view(), name ='controllerrole-detail'),
    
        url(r'plstackapi/networkparametertypes/$', NetworkParameterTypeList.as_view(), name='networkparametertype-list'),
        url(r'plstackapi/networkparametertypes/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterTypeDetail.as_view(), name ='networkparametertype-detail'),
    
        url(r'plstackapi/sitecredentials/$', SiteCredentialList.as_view(), name='sitecredential-list'),
        url(r'plstackapi/sitecredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteCredentialDetail.as_view(), name ='sitecredential-detail'),
    
        url(r'plstackapi/deploymentprivileges/$', DeploymentPrivilegeList.as_view(), name='deploymentprivilege-list'),
        url(r'plstackapi/deploymentprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentPrivilegeDetail.as_view(), name ='deploymentprivilege-detail'),
    
        url(r'plstackapi/controllersliceprivileges/$', ControllerSlicePrivilegeList.as_view(), name='controllersliceprivilege-list'),
        url(r'plstackapi/controllersliceprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSlicePrivilegeDetail.as_view(), name ='controllersliceprivilege-detail'),
    
        url(r'plstackapi/sitedeployments/$', SiteDeploymentList.as_view(), name='sitedeployment-list'),
        url(r'plstackapi/sitedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDeploymentDetail.as_view(), name ='sitedeployment-detail'),
    
        url(r'plstackapi/deploymentroles/$', DeploymentRoleList.as_view(), name='deploymentrole-list'),
        url(r'plstackapi/deploymentroles/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentRoleDetail.as_view(), name ='deploymentrole-detail'),
    
        url(r'plstackapi/usercredentials/$', UserCredentialList.as_view(), name='usercredential-list'),
        url(r'plstackapi/usercredentials/(?P<pk>[a-zA-Z0-9\-]+)/$', UserCredentialDetail.as_view(), name ='usercredential-detail'),
    
        url(r'plstackapi/slicetags/$', SliceTagList.as_view(), name='slicetag-list'),
        url(r'plstackapi/slicetags/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceTagDetail.as_view(), name ='slicetag-detail'),
    
        url(r'plstackapi/networktemplates/$', NetworkTemplateList.as_view(), name='networktemplate-list'),
        url(r'plstackapi/networktemplates/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkTemplateDetail.as_view(), name ='networktemplate-detail'),
    
        url(r'plstackapi/routers/$', RouterList.as_view(), name='router-list'),
        url(r'plstackapi/routers/(?P<pk>[a-zA-Z0-9\-]+)/$', RouterDetail.as_view(), name ='router-detail'),
    
        url(r'plstackapi/serviceresources/$', ServiceResourceList.as_view(), name='serviceresource-list'),
        url(r'plstackapi/serviceresources/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceResourceDetail.as_view(), name ='serviceresource-detail'),
    
    )

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'serviceattributes': reverse('serviceattribute-list', request=request, format=format),
        'controllerimageses': reverse('controllerimages-list', request=request, format=format),
        'controllersiteprivileges': reverse('controllersiteprivilege-list', request=request, format=format),
        'images': reverse('image-list', request=request, format=format),
        'networkparameters': reverse('networkparameter-list', request=request, format=format),
        'sites': reverse('site-list', request=request, format=format),
        'sliceroles': reverse('slicerole-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
        'invoices': reverse('invoice-list', request=request, format=format),
        'sliceprivileges': reverse('sliceprivilege-list', request=request, format=format),
        'planetstackroles': reverse('planetstackrole-list', request=request, format=format),
        'networkslivers': reverse('networksliver-list', request=request, format=format),
        'flavors': reverse('flavor-list', request=request, format=format),
        'controllersites': reverse('controllersite-list', request=request, format=format),
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
        'controllernetworks': reverse('controllernetwork-list', request=request, format=format),
        'imagedeploymentses': reverse('imagedeployments-list', request=request, format=format),
        'controllerusers': reverse('controlleruser-list', request=request, format=format),
        'reservedresources': reverse('reservedresource-list', request=request, format=format),
        'payments': reverse('payment-list', request=request, format=format),
        'networkslices': reverse('networkslice-list', request=request, format=format),
        'userdashboardviews': reverse('userdashboardview-list', request=request, format=format),
        'controllers': reverse('controller-list', request=request, format=format),
        'planetstackprivileges': reverse('planetstackprivilege-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'deployments': reverse('deployment-list', request=request, format=format),
        'reservations': reverse('reservation-list', request=request, format=format),
        'siteprivileges': reverse('siteprivilege-list', request=request, format=format),
        'controllerslices': reverse('controllerslice-list', request=request, format=format),
        'controllerdashboardviews': reverse('controllerdashboardview-list', request=request, format=format),
        'accounts': reverse('account-list', request=request, format=format),
        'controllerroles': reverse('controllerrole-list', request=request, format=format),
        'networkparametertypes': reverse('networkparametertype-list', request=request, format=format),
        'sitecredentials': reverse('sitecredential-list', request=request, format=format),
        'deploymentprivileges': reverse('deploymentprivilege-list', request=request, format=format),
        'controllersliceprivileges': reverse('controllersliceprivilege-list', request=request, format=format),
        'sitedeployments': reverse('sitedeployment-list', request=request, format=format),
        'deploymentroles': reverse('deploymentrole-list', request=request, format=format),
        'usercredentials': reverse('usercredential-list', request=request, format=format),
        'slicetags': reverse('slicetag-list', request=request, format=format),
        'networktemplates': reverse('networktemplate-list', request=request, format=format),
        'routers': reverse('router-list', request=request, format=format),
        'serviceresources': reverse('serviceresource-list', request=request, format=format),
        
    })

# Based on serializers.py

class XOSModelSerializer(serializers.ModelSerializer):
    def save_object(self, obj, **kwargs):

        """ rest_framework can't deal with ManyToMany relations that have a
            through table. In plstackapi, most of the through tables we have
            use defaults or blank fields, so there's no reason why we shouldn't
            be able to save these objects.

            So, let's strip out these m2m relations, and deal with them ourself.
        """
        obj._complex_m2m_data={};
        if getattr(obj, '_m2m_data', None):
            for relatedObject in obj._meta.get_all_related_many_to_many_objects():
                if (relatedObject.field.rel.through._meta.auto_created):
                    # These are non-trough ManyToMany relations and
                    # can be updated just fine
                    continue
                fieldName = relatedObject.get_accessor_name()
                if fieldName in obj._m2m_data.keys():
                    obj._complex_m2m_data[fieldName] = (relatedObject, obj._m2m_data[fieldName])
                    del obj._m2m_data[fieldName]

        serializers.ModelSerializer.save_object(self, obj, **kwargs);

        for (accessor, stuff) in obj._complex_m2m_data.items():
            (relatedObject, data) = stuff
            through = relatedObject.field.rel.through
            local_fieldName = relatedObject.field.m2m_reverse_field_name()
            remote_fieldName = relatedObject.field.m2m_field_name()

            # get the current set of existing relations
            existing = through.objects.filter(**{local_fieldName: obj});

            data_ids = [item.id for item in data]
            existing_ids = [getattr(item,remote_fieldName).id for item in existing]

            #print "data_ids", data_ids
            #print "existing_ids", existing_ids

            # remove relations that are in 'existing' but not in 'data'
            for item in list(existing):
               if (getattr(item,remote_fieldName).id not in data_ids):
                   print "delete", getattr(item,remote_fieldName)
                   item.delete() #(purge=True)

            # add relations that are in 'data' but not in 'existing'
            for item in data:
               if (item.id not in existing_ids):
                   #print "add", item
                   newModel = through(**{local_fieldName: obj, remote_fieldName: item})
                   newModel.save()



class ServiceAttributeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceAttribute
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','value','service',)

class ServiceAttributeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceAttribute
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','value','service',)




class ControllerImagesSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerImages
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','controller','glance_image_id',)

class ControllerImagesIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerImages
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','controller','glance_image_id',)




class ControllerSitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSitePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','site_privilege','role_id',)

class ControllerSitePrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSitePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','site_privilege','role_id',)




class ImageSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    deployments = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Image
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','disk_format','container_format','path','deployments',)

class ImageIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    deployments = serializers.PrimaryKeyRelatedField(many=True,  queryset = Deployment.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Image
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','disk_format','container_format','path','deployments',)




class NetworkParameterSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkParameter
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','parameter','value','content_type','object_id',)

class NetworkParameterIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkParameter
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','parameter','value','content_type','object_id',)




class SiteSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    deployments = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Site
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)

class SiteIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    deployments = serializers.PrimaryKeyRelatedField(many=True,  queryset = Deployment.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Site
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)




class SliceRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

class SliceRoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)




class TagSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Tag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','service','name','value','content_type','object_id',)

class TagIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Tag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','service','name','value','content_type','object_id',)




class InvoiceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Invoice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','date','account',)

class InvoiceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Invoice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','date','account',)




class SlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SlicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','slice','role',)

class SlicePrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SlicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','slice','role',)




class PlanetStackRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStackRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

class PlanetStackRoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStackRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)




class NetworkSliverSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkSliver
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','sliver','ip','port_id',)

class NetworkSliverIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkSliver
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','sliver','ip','port_id',)




class FlavorSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    deployments = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='deployment-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Flavor
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','flavor','order','default','deployments',)

class FlavorIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    deployments = serializers.PrimaryKeyRelatedField(many=True,  queryset = Deployment.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Flavor
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','flavor','order','default','deployments',)




class ControllerSiteSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSite
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','controller','tenant_id',)

class ControllerSiteIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSite
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','controller','tenant_id',)




class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Project
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)

class ProjectIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Project
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)




class SliceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Slice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','service','network','serviceClass','creator','default_flavor','default_image','mount_data_sets','networks','networks',)

class SliceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  queryset = Network.objects.all())
    
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  queryset = Network.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Slice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','service','network','serviceClass','creator','default_flavor','default_image','mount_data_sets','networks','networks',)




class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
    
    
    
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
    
    
    
    slivers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sliver-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    
    routers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='router-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Network
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteed_bandwidth','permit_all_slices','topology_parameters','controller_url','controller_parameters','network_id','router_id','subnet_id','slices','slices','slivers','routers','routers',)

class NetworkIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    slices = serializers.PrimaryKeyRelatedField(many=True,  queryset = Slice.objects.all())
    
    
    
    slices = serializers.PrimaryKeyRelatedField(many=True,  queryset = Slice.objects.all())
    
    
    
    slivers = serializers.PrimaryKeyRelatedField(many=True,  queryset = Sliver.objects.all())
    
    
    
    routers = serializers.PrimaryKeyRelatedField(many=True,  queryset = Router.objects.all())
    
    
    
    routers = serializers.PrimaryKeyRelatedField(many=True,  queryset = Router.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Network
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteed_bandwidth','permit_all_slices','topology_parameters','controller_url','controller_parameters','network_id','router_id','subnet_id','slices','slices','slivers','routers','routers',)




class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Service
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','description','enabled','name','versionNumber','published',)

class ServiceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Service
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','description','enabled','name','versionNumber','published',)




class ServiceClassSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceClass
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)

class ServiceClassIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceClass
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)




class PlanetStackSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStack
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','description',)

class PlanetStackIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStack
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','description',)




class ChargeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Charge
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)

class ChargeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Charge
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)




class RoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Role
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role_type','role','description','content_type',)

class RoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Role
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role_type','role','description','content_type',)




class UsableObjectSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UsableObject
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)

class UsableObjectIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UsableObject
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)




class SiteRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

class SiteRoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)




class SliceCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','key_id','enc_value',)

class SliceCredentialIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','key_id','enc_value',)




class SliverSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Sliver
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','instance_id','instance_uuid','name','instance_name','ip','image','creator','slice','deployment','node','numberCores','flavor','userData','networks',)

class SliverIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  queryset = Network.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Sliver
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','instance_id','instance_uuid','name','instance_name','ip','image','creator','slice','deployment','node','numberCores','flavor','userData','networks',)




class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Node
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_deployment','site',)

class NodeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Node
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_deployment','site',)




class DashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    controllers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='controller-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','url','enabled','controllers',)

class DashboardViewIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    controllers = serializers.PrimaryKeyRelatedField(many=True,  queryset = Controller.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','url','enabled','controllers',)




class ControllerNetworkSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerNetwork
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','controller','net_id','router_id','subnet_id','subnet',)

class ControllerNetworkIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerNetwork
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','controller','net_id','router_id','subnet_id','subnet',)




class ImageDeploymentsSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ImageDeployments
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','deployment',)

class ImageDeploymentsIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ImageDeployments
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','deployment',)




class ControllerUserSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerUser
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','controller','kuser_id',)

class ControllerUserIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerUser
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','controller','kuser_id',)




class ReservedResourceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ReservedResource
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','sliver','resource','quantity','reservationSet',)

class ReservedResourceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ReservedResource
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','sliver','resource','quantity','reservationSet',)




class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Payment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','amount','date',)

class PaymentIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Payment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','amount','date',)




class NetworkSliceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkSlice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','slice',)

class NetworkSliceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkSlice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','slice',)




class UserDashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UserDashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','dashboardView','order',)

class UserDashboardViewIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UserDashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','dashboardView','order',)




class ControllerSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    dashboardviews = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='dashboardview-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Controller
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','dashboardviews',)

class ControllerIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    dashboardviews = serializers.PrimaryKeyRelatedField(many=True,  queryset = DashboardView.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Controller
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','dashboardviews',)




class PlanetStackPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStackPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','planetstack','role',)

class PlanetStackPrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = PlanetStackPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','planetstack','role',)




class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = User
        fields = ('humanReadableName', 'validators', 'id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','created','updated','enacted','policed','backend_status','deleted','timezone',)

class UserIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = User
        fields = ('humanReadableName', 'validators', 'id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','created','updated','enacted','policed','backend_status','deleted','timezone',)




class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    images = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='image-detail')
    
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
    flavors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='flavor-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Deployment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','accessControl','images','sites','flavors',)

class DeploymentIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    images = serializers.PrimaryKeyRelatedField(many=True,  queryset = Image.objects.all())
    
    
    
    sites = serializers.PrimaryKeyRelatedField(many=True,  queryset = Site.objects.all())
    
    
    
    flavors = serializers.PrimaryKeyRelatedField(many=True,  queryset = Flavor.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Deployment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','accessControl','images','sites','flavors',)




class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Reservation
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','startTime','slice','duration',)

class ReservationIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Reservation
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','startTime','slice','duration',)




class SitePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SitePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','site','role',)

class SitePrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SitePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','site','role',)




class ControllerSliceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSlice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice','tenant_id',)

class ControllerSliceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSlice
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice','tenant_id',)




class ControllerDashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerDashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','dashboardView','enabled','url',)

class ControllerDashboardViewIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerDashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','dashboardView','enabled','url',)




class AccountSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Account
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site',)

class AccountIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Account
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site',)




class ControllerRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

class ControllerRoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)




class NetworkParameterTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkParameterType
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description',)

class NetworkParameterTypeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkParameterType
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description',)




class SiteCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','name','key_id','enc_value',)

class SiteCredentialIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','name','key_id','enc_value',)




class DeploymentPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DeploymentPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','deployment','role',)

class DeploymentPrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DeploymentPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','deployment','role',)




class ControllerSlicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSlicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice_privilege','role_id',)

class ControllerSlicePrivilegeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ControllerSlicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice_privilege','role_id',)




class SiteDeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteDeployment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','deployment','controller','availability_zone',)

class SiteDeploymentIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteDeployment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','deployment','controller','availability_zone',)




class DeploymentRoleSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DeploymentRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

class DeploymentRoleIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = DeploymentRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)




class UserCredentialSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UserCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','name','key_id','enc_value',)

class UserCredentialIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = UserCredential
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','name','key_id','enc_value',)




class SliceTagSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceTag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','value',)

class SliceTagIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SliceTag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','value',)




class NetworkTemplateSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkTemplate
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','guaranteed_bandwidth','visibility','translation','shared_network_name','shared_network_id','topology_kind','controller_kind',)

class NetworkTemplateIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = NetworkTemplate
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','guaranteed_bandwidth','visibility','translation','shared_network_name','shared_network_id','topology_kind','controller_kind',)




class RouterSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    
    networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Router
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','owner','networks','networks',)

class RouterIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  queryset = Network.objects.all())
    
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  queryset = Network.objects.all())
    
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = Router
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','owner','networks','networks',)




class ServiceResourceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceResource
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)

class ServiceResourceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceResource
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)




serializerLookUp = { 

                 ServiceAttribute: ServiceAttributeSerializer,

                 ControllerImages: ControllerImagesSerializer,

                 ControllerSitePrivilege: ControllerSitePrivilegeSerializer,

                 Image: ImageSerializer,

                 NetworkParameter: NetworkParameterSerializer,

                 Site: SiteSerializer,

                 SliceRole: SliceRoleSerializer,

                 Tag: TagSerializer,

                 Invoice: InvoiceSerializer,

                 SlicePrivilege: SlicePrivilegeSerializer,

                 PlanetStackRole: PlanetStackRoleSerializer,

                 NetworkSliver: NetworkSliverSerializer,

                 Flavor: FlavorSerializer,

                 ControllerSite: ControllerSiteSerializer,

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

                 ControllerNetwork: ControllerNetworkSerializer,

                 ImageDeployments: ImageDeploymentsSerializer,

                 ControllerUser: ControllerUserSerializer,

                 ReservedResource: ReservedResourceSerializer,

                 Payment: PaymentSerializer,

                 NetworkSlice: NetworkSliceSerializer,

                 UserDashboardView: UserDashboardViewSerializer,

                 Controller: ControllerSerializer,

                 PlanetStackPrivilege: PlanetStackPrivilegeSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 Reservation: ReservationSerializer,

                 SitePrivilege: SitePrivilegeSerializer,

                 ControllerSlice: ControllerSliceSerializer,

                 ControllerDashboardView: ControllerDashboardViewSerializer,

                 Account: AccountSerializer,

                 ControllerRole: ControllerRoleSerializer,

                 NetworkParameterType: NetworkParameterTypeSerializer,

                 SiteCredential: SiteCredentialSerializer,

                 DeploymentPrivilege: DeploymentPrivilegeSerializer,

                 ControllerSlicePrivilege: ControllerSlicePrivilegeSerializer,

                 SiteDeployment: SiteDeploymentSerializer,

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
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.pre_save(serializer.object)
        except ValidationError as err:
            # full_clean on model instance may be called in pre_save,
            # so we have to handle eventual errors.
            response = {"error": "validation",
                         "specific_error": "ValidationError in pre_save",
                         "reasons": err.message_dict}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','value','service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceAttribute.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceAttribute.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerImagesList(generics.ListCreateAPIView):
    queryset = ControllerImages.objects.select_related().all()
    serializer_class = ControllerImagesSerializer
    id_serializer_class = ControllerImagesIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','controller','glance_image_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerImages.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerImagesList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerImagesList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerImagesDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerImages.objects.select_related().all()
    serializer_class = ControllerImagesSerializer
    id_serializer_class = ControllerImagesIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerImages.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerSitePrivilegeList(generics.ListCreateAPIView):
    queryset = ControllerSitePrivilege.objects.select_related().all()
    serializer_class = ControllerSitePrivilegeSerializer
    id_serializer_class = ControllerSitePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','site_privilege','role_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSitePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerSitePrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerSitePrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerSitePrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerSitePrivilege.objects.select_related().all()
    serializer_class = ControllerSitePrivilegeSerializer
    id_serializer_class = ControllerSitePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSitePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','disk_format','container_format','path','deployments',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Image.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Image.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkParameterList(generics.ListCreateAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','parameter','value','content_type','object_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkParameter.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkParameter.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SiteList(generics.ListCreateAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_url','enabled','location','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Site.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Site.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SliceRoleList(generics.ListCreateAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','service','name','value','content_type','object_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Tag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Tag.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class InvoiceList(generics.ListCreateAPIView):
    queryset = Invoice.objects.select_related().all()
    serializer_class = InvoiceSerializer
    id_serializer_class = InvoiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','date','account',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Invoice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Invoice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SlicePrivilegeList(generics.ListCreateAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','slice','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SlicePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SlicePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class PlanetStackRoleList(generics.ListCreateAPIView):
    queryset = PlanetStackRole.objects.select_related().all()
    serializer_class = PlanetStackRoleSerializer
    id_serializer_class = PlanetStackRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStackRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStackRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkSliverList(generics.ListCreateAPIView):
    queryset = NetworkSliver.objects.select_related().all()
    serializer_class = NetworkSliverSerializer
    id_serializer_class = NetworkSliverIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','sliver','ip','port_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkSliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkSliver.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class FlavorList(generics.ListCreateAPIView):
    queryset = Flavor.objects.select_related().all()
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','flavor','order','default','deployments',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Flavor.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Flavor.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerSiteList(generics.ListCreateAPIView):
    queryset = ControllerSite.objects.select_related().all()
    serializer_class = ControllerSiteSerializer
    id_serializer_class = ControllerSiteIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','controller','tenant_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSite.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerSiteList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerSiteList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerSiteDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerSite.objects.select_related().all()
    serializer_class = ControllerSiteSerializer
    id_serializer_class = ControllerSiteIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSite.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.select_related().all()
    serializer_class = ProjectSerializer
    id_serializer_class = ProjectIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Project.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Project.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','service','network','serviceClass','creator','default_flavor','default_image','mount_data_sets','networks','networks',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Slice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Slice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkList(generics.ListCreateAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','template','subnet','ports','labels','owner','guaranteed_bandwidth','permit_all_slices','topology_parameters','controller_url','controller_parameters','network_id','router_id','subnet_id','slices','slices','slivers','routers','routers',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Network.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Network.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','description','enabled','name','versionNumber','published',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Service.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Service.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ServiceClassList(generics.ListCreateAPIView):
    queryset = ServiceClass.objects.select_related().all()
    serializer_class = ServiceClassSerializer
    id_serializer_class = ServiceClassIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','commitment','membershipFee','membershipFeeMonths','upgradeRequiresApproval',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceClass.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceClass.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class PlanetStackList(generics.ListCreateAPIView):
    queryset = PlanetStack.objects.select_related().all()
    serializer_class = PlanetStackSerializer
    id_serializer_class = PlanetStackIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','description',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStack.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStack.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ChargeList(generics.ListCreateAPIView):
    queryset = Charge.objects.select_related().all()
    serializer_class = ChargeSerializer
    id_serializer_class = ChargeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','slice','kind','state','date','object','amount','coreHours','invoice',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Charge.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Charge.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role_type','role','description','content_type',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Role.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Role.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class UsableObjectList(generics.ListCreateAPIView):
    queryset = UsableObject.objects.select_related().all()
    serializer_class = UsableObjectSerializer
    id_serializer_class = UsableObjectIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UsableObject.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UsableObject.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SiteRoleList(generics.ListCreateAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SliceCredentialList(generics.ListCreateAPIView):
    queryset = SliceCredential.objects.select_related().all()
    serializer_class = SliceCredentialSerializer
    id_serializer_class = SliceCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.select_related().all()
    serializer_class = SliverSerializer
    id_serializer_class = SliverIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','instance_id','instance_uuid','name','instance_name','ip','image','creator','slice','deployment','node','numberCores','flavor','userData','networks',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Sliver.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Sliver.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','site_deployment','site',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Node.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Node.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class DashboardViewList(generics.ListCreateAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','url','enabled','controllers',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DashboardView.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerNetworkList(generics.ListCreateAPIView):
    queryset = ControllerNetwork.objects.select_related().all()
    serializer_class = ControllerNetworkSerializer
    id_serializer_class = ControllerNetworkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','controller','net_id','router_id','subnet_id','subnet',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerNetwork.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerNetworkList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerNetworkList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerNetworkDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerNetwork.objects.select_related().all()
    serializer_class = ControllerNetworkSerializer
    id_serializer_class = ControllerNetworkIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerNetwork.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ImageDeploymentsList(generics.ListCreateAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    id_serializer_class = ImageDeploymentsIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','image','deployment',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ImageDeployments.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ImageDeploymentsList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ImageDeploymentsList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ImageDeploymentsDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    id_serializer_class = ImageDeploymentsIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ImageDeployments.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerUserList(generics.ListCreateAPIView):
    queryset = ControllerUser.objects.select_related().all()
    serializer_class = ControllerUserSerializer
    id_serializer_class = ControllerUserIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','controller','kuser_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerUser.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerUserList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerUserList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerUserDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerUser.objects.select_related().all()
    serializer_class = ControllerUserSerializer
    id_serializer_class = ControllerUserIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerUser.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ReservedResourceList(generics.ListCreateAPIView):
    queryset = ReservedResource.objects.select_related().all()
    serializer_class = ReservedResourceSerializer
    id_serializer_class = ReservedResourceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','sliver','resource','quantity','reservationSet',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ReservedResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ReservedResource.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related().all()
    serializer_class = PaymentSerializer
    id_serializer_class = PaymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','account','amount','date',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Payment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Payment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkSliceList(generics.ListCreateAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','network','slice',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkSlice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkSlice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class UserDashboardViewList(generics.ListCreateAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','dashboardView','order',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UserDashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UserDashboardView.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerList(generics.ListCreateAPIView):
    queryset = Controller.objects.select_related().all()
    serializer_class = ControllerSerializer
    id_serializer_class = ControllerIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','dashboardviews',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Controller.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = Controller.objects.select_related().all()
    serializer_class = ControllerSerializer
    id_serializer_class = ControllerIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Controller.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class PlanetStackPrivilegeList(generics.ListCreateAPIView):
    queryset = PlanetStackPrivilege.objects.select_related().all()
    serializer_class = PlanetStackPrivilegeSerializer
    id_serializer_class = PlanetStackPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','planetstack','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStackPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return PlanetStackPrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','created','updated','enacted','policed','backend_status','deleted','timezone',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return User.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return User.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','accessControl','images','sites','flavors',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Deployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Deployment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.select_related().all()
    serializer_class = ReservationSerializer
    id_serializer_class = ReservationIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','startTime','slice','duration',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Reservation.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Reservation.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SitePrivilegeList(generics.ListCreateAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','site','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SitePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SitePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerSliceList(generics.ListCreateAPIView):
    queryset = ControllerSlice.objects.select_related().all()
    serializer_class = ControllerSliceSerializer
    id_serializer_class = ControllerSliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice','tenant_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSlice.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerSliceList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerSliceList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerSliceDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerSlice.objects.select_related().all()
    serializer_class = ControllerSliceSerializer
    id_serializer_class = ControllerSliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSlice.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerDashboardViewList(generics.ListCreateAPIView):
    queryset = ControllerDashboardView.objects.select_related().all()
    serializer_class = ControllerDashboardViewSerializer
    id_serializer_class = ControllerDashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','dashboardView','enabled','url',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerDashboardView.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerDashboardViewList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerDashboardViewList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerDashboardViewDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerDashboardView.objects.select_related().all()
    serializer_class = ControllerDashboardViewSerializer
    id_serializer_class = ControllerDashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerDashboardView.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.select_related().all()
    serializer_class = AccountSerializer
    id_serializer_class = AccountIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','site',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Account.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Account.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerRoleList(generics.ListCreateAPIView):
    queryset = ControllerRole.objects.select_related().all()
    serializer_class = ControllerRoleSerializer
    id_serializer_class = ControllerRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerRoleList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerRoleList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerRoleDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerRole.objects.select_related().all()
    serializer_class = ControllerRoleSerializer
    id_serializer_class = ControllerRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkParameterTypeList(generics.ListCreateAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkParameterType.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkParameterType.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SiteCredentialList(generics.ListCreateAPIView):
    queryset = SiteCredential.objects.select_related().all()
    serializer_class = SiteCredentialSerializer
    id_serializer_class = SiteCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class DeploymentPrivilegeList(generics.ListCreateAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','deployment','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DeploymentPrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DeploymentPrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ControllerSlicePrivilegeList(generics.ListCreateAPIView):
    queryset = ControllerSlicePrivilege.objects.select_related().all()
    serializer_class = ControllerSlicePrivilegeSerializer
    id_serializer_class = ControllerSlicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','controller','slice_privilege','role_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSlicePrivilege.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(ControllerSlicePrivilegeList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(ControllerSlicePrivilegeList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class ControllerSlicePrivilegeDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = ControllerSlicePrivilege.objects.select_related().all()
    serializer_class = ControllerSlicePrivilegeSerializer
    id_serializer_class = ControllerSlicePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ControllerSlicePrivilege.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SiteDeploymentList(generics.ListCreateAPIView):
    queryset = SiteDeployment.objects.select_related().all()
    serializer_class = SiteDeploymentSerializer
    id_serializer_class = SiteDeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','site','deployment','controller','availability_zone',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteDeployment.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        obj = serializer.object
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SiteDeploymentList, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(SiteDeploymentList, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class SiteDeploymentDetail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = SiteDeployment.objects.select_related().all()
    serializer_class = SiteDeploymentSerializer
    id_serializer_class = SiteDeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SiteDeployment.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class DeploymentRoleList(generics.ListCreateAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DeploymentRole.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return DeploymentRole.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class UserCredentialList(generics.ListCreateAPIView):
    queryset = UserCredential.objects.select_related().all()
    serializer_class = UserCredentialSerializer
    id_serializer_class = UserCredentialIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','user','name','key_id','enc_value',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UserCredential.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return UserCredential.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class SliceTagList(generics.ListCreateAPIView):
    queryset = SliceTag.objects.select_related().all()
    serializer_class = SliceTagSerializer
    id_serializer_class = SliceTagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','slice','name','value',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceTag.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return SliceTag.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class NetworkTemplateList(generics.ListCreateAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','description','guaranteed_bandwidth','visibility','translation','shared_network_name','shared_network_id','topology_kind','controller_kind',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkTemplate.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return NetworkTemplate.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class RouterList(generics.ListCreateAPIView):
    queryset = Router.objects.select_related().all()
    serializer_class = RouterSerializer
    id_serializer_class = RouterIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','name','owner','networks','networks',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Router.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return Router.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



class ServiceResourceList(generics.ListCreateAPIView):
    queryset = ServiceResource.objects.select_related().all()
    serializer_class = ServiceResourceSerializer
    id_serializer_class = ServiceResourceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','serviceClass','name','maxUnitsDeployment','maxUnitsNode','maxDuration','bucketInRate','bucketMaxSize','cost','calendarReservable',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceResource.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        no_hyperlinks=False
        if hasattr(self.request,"QUERY_PARAMS"):
            no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise RestFrameworkPermissionDenied("You must be authenticated in order to use this API")
        return ServiceResource.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView



