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
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from apibase import XOSRetrieveUpdateDestroyAPIView, XOSListCreateAPIView, XOSNotAuthenticated

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
    # legacy - deprecated
        url(r'^xos/$', api_root),
    
        url(r'xos/serviceattributes/$', ServiceAttributeList.as_view(), name='serviceattribute-list-legacy'),
        url(r'xos/serviceattributes/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceAttributeDetail.as_view(), name ='serviceattribute-detail-legacy'),
    
        url(r'xos/controllerimages/$', ControllerImagesList.as_view(), name='controllerimages-list-legacy'),
        url(r'xos/controllerimages/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerImagesDetail.as_view(), name ='controllerimages-detail-legacy'),
    
        url(r'xos/controllersiteprivileges/$', ControllerSitePrivilegeList.as_view(), name='controllersiteprivilege-list-legacy'),
        url(r'xos/controllersiteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSitePrivilegeDetail.as_view(), name ='controllersiteprivilege-detail-legacy'),
    
        url(r'xos/images/$', ImageList.as_view(), name='image-list-legacy'),
        url(r'xos/images/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDetail.as_view(), name ='image-detail-legacy'),
    
        url(r'xos/controllernetworks/$', ControllerNetworkList.as_view(), name='controllernetwork-list-legacy'),
        url(r'xos/controllernetworks/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerNetworkDetail.as_view(), name ='controllernetwork-detail-legacy'),
    
        url(r'xos/sites/$', SiteList.as_view(), name='site-list-legacy'),
        url(r'xos/sites/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDetail.as_view(), name ='site-detail-legacy'),
    
        url(r'xos/slice_roles/$', SliceRoleList.as_view(), name='slicerole-list-legacy'),
        url(r'xos/slice_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceRoleDetail.as_view(), name ='slicerole-detail-legacy'),
    
        url(r'xos/xosguiextensions/$', XOSGuiExtensionList.as_view(), name='xosguiextension-list-legacy'),
        url(r'xos/xosguiextensions/(?P<pk>[a-zA-Z0-9\-]+)/$', XOSGuiExtensionDetail.as_view(), name ='xosguiextension-detail-legacy'),
    
        url(r'xos/serviceinstancelinks/$', ServiceInstanceLinkList.as_view(), name='serviceinstancelink-list-legacy'),
        url(r'xos/serviceinstancelinks/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceLinkDetail.as_view(), name ='serviceinstancelink-detail-legacy'),
    
        url(r'xos/slice_privileges/$', SlicePrivilegeList.as_view(), name='sliceprivilege-list-legacy'),
        url(r'xos/slice_privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SlicePrivilegeDetail.as_view(), name ='sliceprivilege-detail-legacy'),
    
        url(r'xos/controllerprivileges/$', ControllerPrivilegeList.as_view(), name='controllerprivilege-list-legacy'),
        url(r'xos/controllerprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerPrivilegeDetail.as_view(), name ='controllerprivilege-detail-legacy'),
    
        url(r'xos/flavors/$', FlavorList.as_view(), name='flavor-list-legacy'),
        url(r'xos/flavors/(?P<pk>[a-zA-Z0-9\-]+)/$', FlavorDetail.as_view(), name ='flavor-detail-legacy'),
    
        url(r'xos/serviceroles/$', ServiceRoleList.as_view(), name='servicerole-list-legacy'),
        url(r'xos/serviceroles/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceRoleDetail.as_view(), name ='servicerole-detail-legacy'),
    
        url(r'xos/controllersites/$', ControllerSiteList.as_view(), name='controllersite-list-legacy'),
        url(r'xos/controllersites/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSiteDetail.as_view(), name ='controllersite-detail-legacy'),
    
        url(r'xos/controllerslices/$', ControllerSliceList.as_view(), name='controllerslice-list-legacy'),
        url(r'xos/controllerslices/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSliceDetail.as_view(), name ='controllerslice-detail-legacy'),
    
        url(r'xos/servicedependencys/$', ServiceDependencyList.as_view(), name='servicedependency-list-legacy'),
        url(r'xos/servicedependencys/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDependencyDetail.as_view(), name ='servicedependency-detail-legacy'),
    
        url(r'xos/networks/$', NetworkList.as_view(), name='network-list-legacy'),
        url(r'xos/networks/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkDetail.as_view(), name ='network-detail-legacy'),
    
        url(r'xos/controllerroles/$', ControllerRoleList.as_view(), name='controllerrole-list-legacy'),
        url(r'xos/controllerroles/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerRoleDetail.as_view(), name ='controllerrole-detail-legacy'),
    
        url(r'xos/diags/$', DiagList.as_view(), name='diag-list-legacy'),
        url(r'xos/diags/(?P<pk>[a-zA-Z0-9\-]+)/$', DiagDetail.as_view(), name ='diag-detail-legacy'),
    
        url(r'xos/ports/$', PortList.as_view(), name='port-list-legacy'),
        url(r'xos/ports/(?P<pk>[a-zA-Z0-9\-]+)/$', PortDetail.as_view(), name ='port-detail-legacy'),
    
        url(r'xos/instances/$', InstanceList.as_view(), name='instance-list-legacy'),
        url(r'xos/instances/(?P<pk>[a-zA-Z0-9\-]+)/$', InstanceDetail.as_view(), name ='instance-detail-legacy'),
    
        url(r'xos/roles/$', RoleList.as_view(), name='role-list-legacy'),
        url(r'xos/roles/(?P<pk>[a-zA-Z0-9\-]+)/$', RoleDetail.as_view(), name ='role-detail-legacy'),
    
        url(r'xos/serviceinterfaces/$', ServiceInterfaceList.as_view(), name='serviceinterface-list-legacy'),
        url(r'xos/serviceinterfaces/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInterfaceDetail.as_view(), name ='serviceinterface-detail-legacy'),
    
        url(r'xos/nodelabels/$', NodeLabelList.as_view(), name='nodelabel-list-legacy'),
        url(r'xos/nodelabels/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeLabelDetail.as_view(), name ='nodelabel-detail-legacy'),
    
        url(r'xos/privileges/$', PrivilegeList.as_view(), name='privilege-list-legacy'),
        url(r'xos/privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', PrivilegeDetail.as_view(), name ='privilege-detail-legacy'),
    
        url(r'xos/nodes/$', NodeList.as_view(), name='node-list-legacy'),
        url(r'xos/nodes/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeDetail.as_view(), name ='node-detail-legacy'),
    
        url(r'xos/addresspools/$', AddressPoolList.as_view(), name='addresspool-list-legacy'),
        url(r'xos/addresspools/(?P<pk>[a-zA-Z0-9\-]+)/$', AddressPoolDetail.as_view(), name ='addresspool-detail-legacy'),
    
        url(r'xos/dashboardviews/$', DashboardViewList.as_view(), name='dashboardview-list-legacy'),
        url(r'xos/dashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', DashboardViewDetail.as_view(), name ='dashboardview-detail-legacy'),
    
        url(r'xos/networkparameters/$', NetworkParameterList.as_view(), name='networkparameter-list-legacy'),
        url(r'xos/networkparameters/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterDetail.as_view(), name ='networkparameter-detail-legacy'),
    
        url(r'xos/imagedeploymentses/$', ImageDeploymentsList.as_view(), name='imagedeployments-list-legacy'),
        url(r'xos/imagedeploymentses/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDeploymentsDetail.as_view(), name ='imagedeployments-detail-legacy'),
    
        url(r'xos/controllerusers/$', ControllerUserList.as_view(), name='controlleruser-list-legacy'),
        url(r'xos/controllerusers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerUserDetail.as_view(), name ='controlleruser-detail-legacy'),
    
        url(r'xos/servicemonitoringagentinfos/$', ServiceMonitoringAgentInfoList.as_view(), name='servicemonitoringagentinfo-list-legacy'),
        url(r'xos/servicemonitoringagentinfos/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceMonitoringAgentInfoDetail.as_view(), name ='servicemonitoringagentinfo-detail-legacy'),
    
        url(r'xos/controllerdashboardviews/$', ControllerDashboardViewList.as_view(), name='controllerdashboardview-list-legacy'),
        url(r'xos/controllerdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDashboardViewDetail.as_view(), name ='controllerdashboardview-detail-legacy'),
    
        url(r'xos/userdashboardviews/$', UserDashboardViewList.as_view(), name='userdashboardview-list-legacy'),
        url(r'xos/userdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDashboardViewDetail.as_view(), name ='userdashboardview-detail-legacy'),
    
        url(r'xos/controllers/$', ControllerList.as_view(), name='controller-list-legacy'),
        url(r'xos/controllers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDetail.as_view(), name ='controller-detail-legacy'),
    
        url(r'xos/slices/$', SliceList.as_view(), name='slice-list-legacy'),
        url(r'xos/slices/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceDetail.as_view(), name ='slice-detail-legacy'),
    
        url(r'xos/users/$', UserList.as_view(), name='user-list-legacy'),
        url(r'xos/users/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDetail.as_view(), name ='user-detail-legacy'),
    
        url(r'xos/deployments/$', DeploymentList.as_view(), name='deployment-list-legacy'),
        url(r'xos/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name ='deployment-detail-legacy'),
    
        url(r'xos/siteprivileges/$', SitePrivilegeList.as_view(), name='siteprivilege-list-legacy'),
        url(r'xos/siteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SitePrivilegeDetail.as_view(), name ='siteprivilege-detail-legacy'),
    
        url(r'xos/site_roles/$', SiteRoleList.as_view(), name='siterole-list-legacy'),
        url(r'xos/site_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteRoleDetail.as_view(), name ='siterole-detail-legacy'),
    
        url(r'xos/xoses/$', XOSList.as_view(), name='xos-list-legacy'),
        url(r'xos/xoses/(?P<pk>[a-zA-Z0-9\-]+)/$', XOSDetail.as_view(), name ='xos-detail-legacy'),
    
        url(r'xos/networkslices/$', NetworkSliceList.as_view(), name='networkslice-list-legacy'),
        url(r'xos/networkslices/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliceDetail.as_view(), name ='networkslice-detail-legacy'),
    
        url(r'xos/services/$', ServiceList.as_view(), name='service-list-legacy'),
        url(r'xos/services/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDetail.as_view(), name ='service-detail-legacy'),
    
        url(r'xos/controllersliceprivileges/$', ControllerSlicePrivilegeList.as_view(), name='controllersliceprivilege-list-legacy'),
        url(r'xos/controllersliceprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSlicePrivilegeDetail.as_view(), name ='controllersliceprivilege-detail-legacy'),
    
        url(r'xos/serviceinstanceattributes/$', ServiceInstanceAttributeList.as_view(), name='serviceinstanceattribute-list-legacy'),
        url(r'xos/serviceinstanceattributes/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceAttributeDetail.as_view(), name ='serviceinstanceattribute-detail-legacy'),
    
        url(r'xos/deploymentprivileges/$', DeploymentPrivilegeList.as_view(), name='deploymentprivilege-list-legacy'),
        url(r'xos/deploymentprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentPrivilegeDetail.as_view(), name ='deploymentprivilege-detail-legacy'),
    
        url(r'xos/networkparametertypes/$', NetworkParameterTypeList.as_view(), name='networkparametertype-list-legacy'),
        url(r'xos/networkparametertypes/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterTypeDetail.as_view(), name ='networkparametertype-detail-legacy'),
    
        url(r'xos/sitedeployments/$', SiteDeploymentList.as_view(), name='sitedeployment-list-legacy'),
        url(r'xos/sitedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDeploymentDetail.as_view(), name ='sitedeployment-detail-legacy'),
    
        url(r'xos/tenantwithcontainers/$', TenantWithContainerList.as_view(), name='tenantwithcontainer-list-legacy'),
        url(r'xos/tenantwithcontainers/(?P<pk>[a-zA-Z0-9\-]+)/$', TenantWithContainerDetail.as_view(), name ='tenantwithcontainer-detail-legacy'),
    
        url(r'xos/deploymentroles/$', DeploymentRoleList.as_view(), name='deploymentrole-list-legacy'),
        url(r'xos/deploymentroles/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentRoleDetail.as_view(), name ='deploymentrole-detail-legacy'),
    
        url(r'xos/tags/$', TagList.as_view(), name='tag-list-legacy'),
        url(r'xos/tags/(?P<pk>[a-zA-Z0-9\-]+)/$', TagDetail.as_view(), name ='tag-detail-legacy'),
    
        url(r'xos/interfacetypes/$', InterfaceTypeList.as_view(), name='interfacetype-list-legacy'),
        url(r'xos/interfacetypes/(?P<pk>[a-zA-Z0-9\-]+)/$', InterfaceTypeDetail.as_view(), name ='interfacetype-detail-legacy'),
    
        url(r'xos/networktemplates/$', NetworkTemplateList.as_view(), name='networktemplate-list-legacy'),
        url(r'xos/networktemplates/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkTemplateDetail.as_view(), name ='networktemplate-detail-legacy'),
    
        url(r'xos/serviceprivileges/$', ServicePrivilegeList.as_view(), name='serviceprivilege-list-legacy'),
        url(r'xos/serviceprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ServicePrivilegeDetail.as_view(), name ='serviceprivilege-detail-legacy'),
    
        url(r'xos/serviceinstances/$', ServiceInstanceList.as_view(), name='serviceinstance-list-legacy'),
        url(r'xos/serviceinstances/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceDetail.as_view(), name ='serviceinstance-detail-legacy'),
    
    ) + patterns('',
    # new - use these instead of the above
        url(r'^api/core/$', api_root),
    
        url(r'api/core/serviceattributes/$', ServiceAttributeList.as_view(), name='serviceattribute-list'),
        url(r'api/core/serviceattributes/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceAttributeDetail.as_view(), name ='serviceattribute-detail'),
    
        url(r'api/core/controllerimages/$', ControllerImagesList.as_view(), name='controllerimages-list'),
        url(r'api/core/controllerimages/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerImagesDetail.as_view(), name ='controllerimages-detail'),
    
        url(r'api/core/controllersiteprivileges/$', ControllerSitePrivilegeList.as_view(), name='controllersiteprivilege-list'),
        url(r'api/core/controllersiteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSitePrivilegeDetail.as_view(), name ='controllersiteprivilege-detail'),
    
        url(r'api/core/images/$', ImageList.as_view(), name='image-list'),
        url(r'api/core/images/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDetail.as_view(), name ='image-detail'),
    
        url(r'api/core/controllernetworks/$', ControllerNetworkList.as_view(), name='controllernetwork-list'),
        url(r'api/core/controllernetworks/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerNetworkDetail.as_view(), name ='controllernetwork-detail'),
    
        url(r'api/core/sites/$', SiteList.as_view(), name='site-list'),
        url(r'api/core/sites/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDetail.as_view(), name ='site-detail'),
    
        url(r'api/core/slice_roles/$', SliceRoleList.as_view(), name='slicerole-list'),
        url(r'api/core/slice_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceRoleDetail.as_view(), name ='slicerole-detail'),
    
        url(r'api/core/xosguiextensions/$', XOSGuiExtensionList.as_view(), name='xosguiextension-list'),
        url(r'api/core/xosguiextensions/(?P<pk>[a-zA-Z0-9\-]+)/$', XOSGuiExtensionDetail.as_view(), name ='xosguiextension-detail'),
    
        url(r'api/core/serviceinstancelinks/$', ServiceInstanceLinkList.as_view(), name='serviceinstancelink-list'),
        url(r'api/core/serviceinstancelinks/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceLinkDetail.as_view(), name ='serviceinstancelink-detail'),
    
        url(r'api/core/slice_privileges/$', SlicePrivilegeList.as_view(), name='sliceprivilege-list'),
        url(r'api/core/slice_privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SlicePrivilegeDetail.as_view(), name ='sliceprivilege-detail'),
    
        url(r'api/core/controllerprivileges/$', ControllerPrivilegeList.as_view(), name='controllerprivilege-list'),
        url(r'api/core/controllerprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerPrivilegeDetail.as_view(), name ='controllerprivilege-detail'),
    
        url(r'api/core/flavors/$', FlavorList.as_view(), name='flavor-list'),
        url(r'api/core/flavors/(?P<pk>[a-zA-Z0-9\-]+)/$', FlavorDetail.as_view(), name ='flavor-detail'),
    
        url(r'api/core/serviceroles/$', ServiceRoleList.as_view(), name='servicerole-list'),
        url(r'api/core/serviceroles/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceRoleDetail.as_view(), name ='servicerole-detail'),
    
        url(r'api/core/controllersites/$', ControllerSiteList.as_view(), name='controllersite-list'),
        url(r'api/core/controllersites/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSiteDetail.as_view(), name ='controllersite-detail'),
    
        url(r'api/core/controllerslices/$', ControllerSliceList.as_view(), name='controllerslice-list'),
        url(r'api/core/controllerslices/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSliceDetail.as_view(), name ='controllerslice-detail'),
    
        url(r'api/core/servicedependencys/$', ServiceDependencyList.as_view(), name='servicedependency-list'),
        url(r'api/core/servicedependencys/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDependencyDetail.as_view(), name ='servicedependency-detail'),
    
        url(r'api/core/networks/$', NetworkList.as_view(), name='network-list'),
        url(r'api/core/networks/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkDetail.as_view(), name ='network-detail'),
    
        url(r'api/core/controllerroles/$', ControllerRoleList.as_view(), name='controllerrole-list'),
        url(r'api/core/controllerroles/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerRoleDetail.as_view(), name ='controllerrole-detail'),
    
        url(r'api/core/diags/$', DiagList.as_view(), name='diag-list'),
        url(r'api/core/diags/(?P<pk>[a-zA-Z0-9\-]+)/$', DiagDetail.as_view(), name ='diag-detail'),
    
        url(r'api/core/ports/$', PortList.as_view(), name='port-list'),
        url(r'api/core/ports/(?P<pk>[a-zA-Z0-9\-]+)/$', PortDetail.as_view(), name ='port-detail'),
    
        url(r'api/core/instances/$', InstanceList.as_view(), name='instance-list'),
        url(r'api/core/instances/(?P<pk>[a-zA-Z0-9\-]+)/$', InstanceDetail.as_view(), name ='instance-detail'),
    
        url(r'api/core/roles/$', RoleList.as_view(), name='role-list'),
        url(r'api/core/roles/(?P<pk>[a-zA-Z0-9\-]+)/$', RoleDetail.as_view(), name ='role-detail'),
    
        url(r'api/core/serviceinterfaces/$', ServiceInterfaceList.as_view(), name='serviceinterface-list'),
        url(r'api/core/serviceinterfaces/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInterfaceDetail.as_view(), name ='serviceinterface-detail'),
    
        url(r'api/core/nodelabels/$', NodeLabelList.as_view(), name='nodelabel-list'),
        url(r'api/core/nodelabels/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeLabelDetail.as_view(), name ='nodelabel-detail'),
    
        url(r'api/core/privileges/$', PrivilegeList.as_view(), name='privilege-list'),
        url(r'api/core/privileges/(?P<pk>[a-zA-Z0-9\-]+)/$', PrivilegeDetail.as_view(), name ='privilege-detail'),
    
        url(r'api/core/nodes/$', NodeList.as_view(), name='node-list'),
        url(r'api/core/nodes/(?P<pk>[a-zA-Z0-9\-]+)/$', NodeDetail.as_view(), name ='node-detail'),
    
        url(r'api/core/addresspools/$', AddressPoolList.as_view(), name='addresspool-list'),
        url(r'api/core/addresspools/(?P<pk>[a-zA-Z0-9\-]+)/$', AddressPoolDetail.as_view(), name ='addresspool-detail'),
    
        url(r'api/core/dashboardviews/$', DashboardViewList.as_view(), name='dashboardview-list'),
        url(r'api/core/dashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', DashboardViewDetail.as_view(), name ='dashboardview-detail'),
    
        url(r'api/core/networkparameters/$', NetworkParameterList.as_view(), name='networkparameter-list'),
        url(r'api/core/networkparameters/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterDetail.as_view(), name ='networkparameter-detail'),
    
        url(r'api/core/imagedeploymentses/$', ImageDeploymentsList.as_view(), name='imagedeployments-list'),
        url(r'api/core/imagedeploymentses/(?P<pk>[a-zA-Z0-9\-]+)/$', ImageDeploymentsDetail.as_view(), name ='imagedeployments-detail'),
    
        url(r'api/core/controllerusers/$', ControllerUserList.as_view(), name='controlleruser-list'),
        url(r'api/core/controllerusers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerUserDetail.as_view(), name ='controlleruser-detail'),
    
        url(r'api/core/servicemonitoringagentinfos/$', ServiceMonitoringAgentInfoList.as_view(), name='servicemonitoringagentinfo-list'),
        url(r'api/core/servicemonitoringagentinfos/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceMonitoringAgentInfoDetail.as_view(), name ='servicemonitoringagentinfo-detail'),
    
        url(r'api/core/controllerdashboardviews/$', ControllerDashboardViewList.as_view(), name='controllerdashboardview-list'),
        url(r'api/core/controllerdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDashboardViewDetail.as_view(), name ='controllerdashboardview-detail'),
    
        url(r'api/core/userdashboardviews/$', UserDashboardViewList.as_view(), name='userdashboardview-list'),
        url(r'api/core/userdashboardviews/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDashboardViewDetail.as_view(), name ='userdashboardview-detail'),
    
        url(r'api/core/controllers/$', ControllerList.as_view(), name='controller-list'),
        url(r'api/core/controllers/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerDetail.as_view(), name ='controller-detail'),
    
        url(r'api/core/slices/$', SliceList.as_view(), name='slice-list'),
        url(r'api/core/slices/(?P<pk>[a-zA-Z0-9\-]+)/$', SliceDetail.as_view(), name ='slice-detail'),
    
        url(r'api/core/users/$', UserList.as_view(), name='user-list'),
        url(r'api/core/users/(?P<pk>[a-zA-Z0-9\-]+)/$', UserDetail.as_view(), name ='user-detail'),
    
        url(r'api/core/deployments/$', DeploymentList.as_view(), name='deployment-list'),
        url(r'api/core/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name ='deployment-detail'),
    
        url(r'api/core/siteprivileges/$', SitePrivilegeList.as_view(), name='siteprivilege-list'),
        url(r'api/core/siteprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', SitePrivilegeDetail.as_view(), name ='siteprivilege-detail'),
    
        url(r'api/core/site_roles/$', SiteRoleList.as_view(), name='siterole-list'),
        url(r'api/core/site_roles/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteRoleDetail.as_view(), name ='siterole-detail'),
    
        url(r'api/core/xoses/$', XOSList.as_view(), name='xos-list'),
        url(r'api/core/xoses/(?P<pk>[a-zA-Z0-9\-]+)/$', XOSDetail.as_view(), name ='xos-detail'),
    
        url(r'api/core/networkslices/$', NetworkSliceList.as_view(), name='networkslice-list'),
        url(r'api/core/networkslices/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkSliceDetail.as_view(), name ='networkslice-detail'),
    
        url(r'api/core/services/$', ServiceList.as_view(), name='service-list'),
        url(r'api/core/services/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceDetail.as_view(), name ='service-detail'),
    
        url(r'api/core/controllersliceprivileges/$', ControllerSlicePrivilegeList.as_view(), name='controllersliceprivilege-list'),
        url(r'api/core/controllersliceprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ControllerSlicePrivilegeDetail.as_view(), name ='controllersliceprivilege-detail'),
    
        url(r'api/core/serviceinstanceattributes/$', ServiceInstanceAttributeList.as_view(), name='serviceinstanceattribute-list'),
        url(r'api/core/serviceinstanceattributes/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceAttributeDetail.as_view(), name ='serviceinstanceattribute-detail'),
    
        url(r'api/core/deploymentprivileges/$', DeploymentPrivilegeList.as_view(), name='deploymentprivilege-list'),
        url(r'api/core/deploymentprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentPrivilegeDetail.as_view(), name ='deploymentprivilege-detail'),
    
        url(r'api/core/networkparametertypes/$', NetworkParameterTypeList.as_view(), name='networkparametertype-list'),
        url(r'api/core/networkparametertypes/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkParameterTypeDetail.as_view(), name ='networkparametertype-detail'),
    
        url(r'api/core/sitedeployments/$', SiteDeploymentList.as_view(), name='sitedeployment-list'),
        url(r'api/core/sitedeployments/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteDeploymentDetail.as_view(), name ='sitedeployment-detail'),
    
        url(r'api/core/tenantwithcontainers/$', TenantWithContainerList.as_view(), name='tenantwithcontainer-list'),
        url(r'api/core/tenantwithcontainers/(?P<pk>[a-zA-Z0-9\-]+)/$', TenantWithContainerDetail.as_view(), name ='tenantwithcontainer-detail'),
    
        url(r'api/core/deploymentroles/$', DeploymentRoleList.as_view(), name='deploymentrole-list'),
        url(r'api/core/deploymentroles/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentRoleDetail.as_view(), name ='deploymentrole-detail'),
    
        url(r'api/core/tags/$', TagList.as_view(), name='tag-list'),
        url(r'api/core/tags/(?P<pk>[a-zA-Z0-9\-]+)/$', TagDetail.as_view(), name ='tag-detail'),
    
        url(r'api/core/interfacetypes/$', InterfaceTypeList.as_view(), name='interfacetype-list'),
        url(r'api/core/interfacetypes/(?P<pk>[a-zA-Z0-9\-]+)/$', InterfaceTypeDetail.as_view(), name ='interfacetype-detail'),
    
        url(r'api/core/networktemplates/$', NetworkTemplateList.as_view(), name='networktemplate-list'),
        url(r'api/core/networktemplates/(?P<pk>[a-zA-Z0-9\-]+)/$', NetworkTemplateDetail.as_view(), name ='networktemplate-detail'),
    
        url(r'api/core/serviceprivileges/$', ServicePrivilegeList.as_view(), name='serviceprivilege-list'),
        url(r'api/core/serviceprivileges/(?P<pk>[a-zA-Z0-9\-]+)/$', ServicePrivilegeDetail.as_view(), name ='serviceprivilege-detail'),
    
        url(r'api/core/serviceinstances/$', ServiceInstanceList.as_view(), name='serviceinstance-list'),
        url(r'api/core/serviceinstances/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceInstanceDetail.as_view(), name ='serviceinstance-detail'),
    
    )

@api_view(['GET'])
def api_root_legacy(request, format=None):
    return Response({
        'serviceattributes': reverse('serviceattribute-list-legacy', request=request, format=format),
        'controllerimageses': reverse('controllerimages-list-legacy', request=request, format=format),
        'controllersiteprivileges': reverse('controllersiteprivilege-list-legacy', request=request, format=format),
        'images': reverse('image-list-legacy', request=request, format=format),
        'controllernetworks': reverse('controllernetwork-list-legacy', request=request, format=format),
        'sites': reverse('site-list-legacy', request=request, format=format),
        'sliceroles': reverse('slicerole-list-legacy', request=request, format=format),
        'xosguiextensions': reverse('xosguiextension-list-legacy', request=request, format=format),
        'serviceinstancelinks': reverse('serviceinstancelink-list-legacy', request=request, format=format),
        'sliceprivileges': reverse('sliceprivilege-list-legacy', request=request, format=format),
        'controllerprivileges': reverse('controllerprivilege-list-legacy', request=request, format=format),
        'flavors': reverse('flavor-list-legacy', request=request, format=format),
        'serviceroles': reverse('servicerole-list-legacy', request=request, format=format),
        'controllersites': reverse('controllersite-list-legacy', request=request, format=format),
        'controllerslices': reverse('controllerslice-list-legacy', request=request, format=format),
        'servicedependencys': reverse('servicedependency-list-legacy', request=request, format=format),
        'networks': reverse('network-list-legacy', request=request, format=format),
        'controllerroles': reverse('controllerrole-list-legacy', request=request, format=format),
        'diags': reverse('diag-list-legacy', request=request, format=format),
        'ports': reverse('port-list-legacy', request=request, format=format),
        'instances': reverse('instance-list-legacy', request=request, format=format),
        'roles': reverse('role-list-legacy', request=request, format=format),
        'serviceinterfaces': reverse('serviceinterface-list-legacy', request=request, format=format),
        'nodelabels': reverse('nodelabel-list-legacy', request=request, format=format),
        'privileges': reverse('privilege-list-legacy', request=request, format=format),
        'nodes': reverse('node-list-legacy', request=request, format=format),
        'addresspools': reverse('addresspool-list-legacy', request=request, format=format),
        'dashboardviews': reverse('dashboardview-list-legacy', request=request, format=format),
        'networkparameters': reverse('networkparameter-list-legacy', request=request, format=format),
        'imagedeploymentses': reverse('imagedeployments-list-legacy', request=request, format=format),
        'controllerusers': reverse('controlleruser-list-legacy', request=request, format=format),
        'servicemonitoringagentinfos': reverse('servicemonitoringagentinfo-list-legacy', request=request, format=format),
        'controllerdashboardviews': reverse('controllerdashboardview-list-legacy', request=request, format=format),
        'userdashboardviews': reverse('userdashboardview-list-legacy', request=request, format=format),
        'controllers': reverse('controller-list-legacy', request=request, format=format),
        'slices': reverse('slice-list-legacy', request=request, format=format),
        'users': reverse('user-list-legacy', request=request, format=format),
        'deployments': reverse('deployment-list-legacy', request=request, format=format),
        'siteprivileges': reverse('siteprivilege-list-legacy', request=request, format=format),
        'siteroles': reverse('siterole-list-legacy', request=request, format=format),
        'xoses': reverse('xos-list-legacy', request=request, format=format),
        'networkslices': reverse('networkslice-list-legacy', request=request, format=format),
        'services': reverse('service-list-legacy', request=request, format=format),
        'controllersliceprivileges': reverse('controllersliceprivilege-list-legacy', request=request, format=format),
        'serviceinstanceattributes': reverse('serviceinstanceattribute-list-legacy', request=request, format=format),
        'deploymentprivileges': reverse('deploymentprivilege-list-legacy', request=request, format=format),
        'networkparametertypes': reverse('networkparametertype-list-legacy', request=request, format=format),
        'sitedeployments': reverse('sitedeployment-list-legacy', request=request, format=format),
        'tenantwithcontainers': reverse('tenantwithcontainer-list-legacy', request=request, format=format),
        'deploymentroles': reverse('deploymentrole-list-legacy', request=request, format=format),
        'tags': reverse('tag-list-legacy', request=request, format=format),
        'interfacetypes': reverse('interfacetype-list-legacy', request=request, format=format),
        'networktemplates': reverse('networktemplate-list-legacy', request=request, format=format),
        'serviceprivileges': reverse('serviceprivilege-list-legacy', request=request, format=format),
        'serviceinstances': reverse('serviceinstance-list-legacy', request=request, format=format),
        
    })

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'serviceattributes': reverse('serviceattribute-list', request=request, format=format),
        'controllerimageses': reverse('controllerimages-list', request=request, format=format),
        'controllersiteprivileges': reverse('controllersiteprivilege-list', request=request, format=format),
        'images': reverse('image-list', request=request, format=format),
        'controllernetworks': reverse('controllernetwork-list', request=request, format=format),
        'sites': reverse('site-list', request=request, format=format),
        'sliceroles': reverse('slicerole-list', request=request, format=format),
        'xosguiextensions': reverse('xosguiextension-list', request=request, format=format),
        'serviceinstancelinks': reverse('serviceinstancelink-list', request=request, format=format),
        'sliceprivileges': reverse('sliceprivilege-list', request=request, format=format),
        'controllerprivileges': reverse('controllerprivilege-list', request=request, format=format),
        'flavors': reverse('flavor-list', request=request, format=format),
        'serviceroles': reverse('servicerole-list', request=request, format=format),
        'controllersites': reverse('controllersite-list', request=request, format=format),
        'controllerslices': reverse('controllerslice-list', request=request, format=format),
        'servicedependencys': reverse('servicedependency-list', request=request, format=format),
        'networks': reverse('network-list', request=request, format=format),
        'controllerroles': reverse('controllerrole-list', request=request, format=format),
        'diags': reverse('diag-list', request=request, format=format),
        'ports': reverse('port-list', request=request, format=format),
        'instances': reverse('instance-list', request=request, format=format),
        'roles': reverse('role-list', request=request, format=format),
        'serviceinterfaces': reverse('serviceinterface-list', request=request, format=format),
        'nodelabels': reverse('nodelabel-list', request=request, format=format),
        'privileges': reverse('privilege-list', request=request, format=format),
        'nodes': reverse('node-list', request=request, format=format),
        'addresspools': reverse('addresspool-list', request=request, format=format),
        'dashboardviews': reverse('dashboardview-list', request=request, format=format),
        'networkparameters': reverse('networkparameter-list', request=request, format=format),
        'imagedeploymentses': reverse('imagedeployments-list', request=request, format=format),
        'controllerusers': reverse('controlleruser-list', request=request, format=format),
        'servicemonitoringagentinfos': reverse('servicemonitoringagentinfo-list', request=request, format=format),
        'controllerdashboardviews': reverse('controllerdashboardview-list', request=request, format=format),
        'userdashboardviews': reverse('userdashboardview-list', request=request, format=format),
        'controllers': reverse('controller-list', request=request, format=format),
        'slices': reverse('slice-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'deployments': reverse('deployment-list', request=request, format=format),
        'siteprivileges': reverse('siteprivilege-list', request=request, format=format),
        'siteroles': reverse('siterole-list', request=request, format=format),
        'xoses': reverse('xos-list', request=request, format=format),
        'networkslices': reverse('networkslice-list', request=request, format=format),
        'services': reverse('service-list', request=request, format=format),
        'controllersliceprivileges': reverse('controllersliceprivilege-list', request=request, format=format),
        'serviceinstanceattributes': reverse('serviceinstanceattribute-list', request=request, format=format),
        'deploymentprivileges': reverse('deploymentprivilege-list', request=request, format=format),
        'networkparametertypes': reverse('networkparametertype-list', request=request, format=format),
        'sitedeployments': reverse('sitedeployment-list', request=request, format=format),
        'tenantwithcontainers': reverse('tenantwithcontainer-list', request=request, format=format),
        'deploymentroles': reverse('deploymentrole-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
        'interfacetypes': reverse('interfacetype-list', request=request, format=format),
        'networktemplates': reverse('networktemplate-list', request=request, format=format),
        'serviceprivileges': reverse('serviceprivilege-list', request=request, format=format),
        'serviceinstances': reverse('serviceinstance-list', request=request, format=format),
        
    })

# Based on serializers.py

class XOSModelSerializer(serializers.ModelSerializer):
    # TODO: Rest Framework 3.x doesn't support save_object()
    def NEED_TO_UPDATE_save_object(self, obj, **kwargs):

        """ rest_framework can't deal with ManyToMany relations that have a
            through table. In xos, most of the through tables we have
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','glance_image_id','image','controller',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','glance_image_id','image','controller',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','site_privilege',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','site_privilege',)




class ImageSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Image
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','kind','disk_format','container_format','path','tag',)

class ImageIdSerializer(XOSModelSerializer):
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
        model = Image
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','kind','disk_format','container_format','path','tag',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','subnet','start_ip','stop_ip','net_id','router_id','subnet_id','gateway','segmentation_id','network','controller',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','subnet','start_ip','stop_ip','net_id','router_id','subnet_id','gateway','segmentation_id','network','controller',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_url','enabled','hosts_nodes','hosts_users','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)

class SiteIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    deployments = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Deployment.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_url','enabled','hosts_nodes','hosts_users','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)




class XOSGuiExtensionSerializer(serializers.HyperlinkedModelSerializer):
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
        model = XOSGuiExtension
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','files',)

class XOSGuiExtensionIdSerializer(XOSModelSerializer):
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
        model = XOSGuiExtension
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','files',)




class ServiceInstanceLinkSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceInstanceLink
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','provider_service_instance','subscriber_service_instance','subscriber_service','subscriber_network',)

class ServiceInstanceLinkIdSerializer(XOSModelSerializer):
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
        model = ServiceInstanceLink
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','provider_service_instance','subscriber_service_instance','subscriber_service','subscriber_network',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','slice','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','slice','role',)




class ControllerPrivilegeSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ControllerPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','privilege',)

class ControllerPrivilegeIdSerializer(XOSModelSerializer):
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
        model = ControllerPrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','privilege',)




class FlavorSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Flavor
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','flavor',)

class FlavorIdSerializer(XOSModelSerializer):
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
        model = Flavor
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','flavor',)




class ServiceRoleSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

class ServiceRoleIdSerializer(XOSModelSerializer):
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
        model = ServiceRole
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','site','controller',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','site','controller',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','controller','slice',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','controller','slice',)




class ServiceDependencySerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceDependency
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','connect_method','provider_service','subscriber_service',)

class ServiceDependencyIdSerializer(XOSModelSerializer):
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
        model = ServiceDependency
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','connect_method','provider_service','subscriber_service',)




class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
    
    
    
    slices = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='slice-detail')
    
    
    
    instances = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='instance-detail')
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','subnet','start_ip','end_ip','ports','labels','permit_all_slices','autoconnect','template','owner','slices','slices','instances',)

class NetworkIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    slices = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Slice.objects.all())
    
    
    
    slices = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Slice.objects.all())
    
    
    
    instances = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Instance.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','subnet','start_ip','end_ip','ports','labels','permit_all_slices','autoconnect','template','owner','slices','slices','instances',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)




class DiagSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Diag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)

class DiagIdSerializer(XOSModelSerializer):
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
        model = Diag
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)




class PortSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Port
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','ip','port_id','mac','xos_created','network','instance',)

class PortIdSerializer(XOSModelSerializer):
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
        model = Port
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','ip','port_id','mac','xos_created','network','instance',)




class InstanceSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Instance
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','instance_id','instance_uuid','name','instance_name','ip','numberCores','userData','isolation','volumes','image','creator','slice','deployment','node','flavor','parent','networks',)

class InstanceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Network.objects.all())
    
    
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
        model = Instance
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','instance_id','instance_uuid','name','instance_name','ip','numberCores','userData','isolation','volumes','image','creator','slice','deployment','node','flavor','parent','networks',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_type','role','description',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_type','role','description',)




class ServiceInterfaceSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceInterface
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','service','interface_type',)

class ServiceInterfaceIdSerializer(XOSModelSerializer):
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
        model = ServiceInterface
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','service','interface_type',)




class NodeLabelSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    nodes = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='node-detail')
    
    
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
        model = NodeLabel
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','nodes',)

class NodeLabelIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    nodes = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Node.objects.all())
    
    
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
        model = NodeLabel
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','nodes',)




class PrivilegeSerializer(serializers.HyperlinkedModelSerializer):
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
        model = Privilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','accessor_id','accessor_type','object_id','object_type','permission','granted','expires',)

class PrivilegeIdSerializer(XOSModelSerializer):
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
        model = Privilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','accessor_id','accessor_type','object_id','object_type','permission','granted','expires',)




class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    nodelabels = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='nodelabel-detail')
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_deployment','nodelabels',)

class NodeIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    nodelabels = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = NodeLabel.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_deployment','nodelabels',)




class AddressPoolSerializer(serializers.HyperlinkedModelSerializer):
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
        model = AddressPool
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','addresses','gateway_ip','gateway_mac','cidr','inuse','service',)

class AddressPoolIdSerializer(XOSModelSerializer):
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
        model = AddressPool
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','addresses','gateway_ip','gateway_mac','cidr','inuse','service',)




class DashboardViewSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    controllers = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='controller-detail')
    
    
    
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
        model = DashboardView
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','url','enabled','icon','icon_active','controllers','deployments',)

class DashboardViewIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    controllers = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Controller.objects.all())
    
    
    
    deployments = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Deployment.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','url','enabled','icon','icon_active','controllers','deployments',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','value','content_type','object_id','parameter',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','value','content_type','object_id','parameter',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','image','deployment',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','image','deployment',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','kuser_id','user','controller',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','kuser_id','user','controller',)




class ServiceMonitoringAgentInfoSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceMonitoringAgentInfo
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','target_uri','service',)

class ServiceMonitoringAgentInfoIdSerializer(XOSModelSerializer):
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
        model = ServiceMonitoringAgentInfo
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','target_uri','service',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','enabled','url','controller','dashboardView',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','enabled','url','controller','dashboardView',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','dashboardView','order',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','dashboardView','order',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','domain','rabbit_host','rabbit_user','rabbit_password','deployment','dashboardviews',)

class ControllerIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    dashboardviews = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = DashboardView.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','domain','rabbit_host','rabbit_user','rabbit_password','deployment','dashboardviews',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','enabled','description','slice_url','max_instances','network','exposed_ports','mount_data_sets','default_isolation','site','service','creator','default_flavor','default_image','default_node','networks','networks',)

class SliceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Network.objects.all())
    
    
    
    networks = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Network.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','enabled','description','slice_url','max_instances','network','exposed_ports','mount_data_sets','default_isolation','site','service','creator','default_flavor','default_image','default_node','networks','networks',)




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
        fields = ('humanReadableName', 'validators', 'id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','is_appuser','login_page','created','updated','enacted','policed','backend_status','backend_need_delete','backend_need_reap','deleted','write_protect','lazy_blocked','no_sync','no_policy','timezone','policy_status',)

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
        fields = ('humanReadableName', 'validators', 'id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','is_appuser','login_page','created','updated','enacted','policed','backend_status','backend_need_delete','backend_need_reap','deleted','write_protect','lazy_blocked','no_sync','no_policy','timezone','policy_status',)




class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    
    sites = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='site-detail')
    
    
    
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
        model = Deployment
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','accessControl','sites','dashboardviews',)

class DeploymentIdSerializer(XOSModelSerializer):
    id = IdField()
    
    
    sites = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = Site.objects.all())
    
    
    
    dashboardviews = serializers.PrimaryKeyRelatedField(many=True,  required=False, queryset = DashboardView.objects.all())
    
    
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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','accessControl','sites','dashboardviews',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','site','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','site','role',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)




class XOSSerializer(serializers.HyperlinkedModelSerializer):
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
        model = XOS
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)

class XOSIdSerializer(XOSModelSerializer):
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
        model = XOS
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','network','slice',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','network','slice',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','slice_privilege',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','slice_privilege',)




class ServiceInstanceAttributeSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceInstanceAttribute
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service_instance',)

class ServiceInstanceAttributeIdSerializer(XOSModelSerializer):
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
        model = ServiceInstanceAttribute
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service_instance',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','deployment','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','deployment','role',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','availability_zone','site','deployment','controller',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','availability_zone','site','deployment','controller',)




class TenantWithContainerSerializer(serializers.HyperlinkedModelSerializer):
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
        model = TenantWithContainer
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner','external_hostname','external_container','instance','creator',)

class TenantWithContainerIdSerializer(XOSModelSerializer):
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
        model = TenantWithContainer
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner','external_hostname','external_container','instance','creator',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','content_type','object_id','service',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','content_type','object_id','service',)




class InterfaceTypeSerializer(serializers.HyperlinkedModelSerializer):
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
        model = InterfaceType
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','direction',)

class InterfaceTypeIdSerializer(XOSModelSerializer):
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
        model = InterfaceType
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','direction',)




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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','visibility','translation','access','shared_network_name','shared_network_id','topology_kind','controller_kind','vtn_kind',)

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
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','visibility','translation','access','shared_network_name','shared_network_id','topology_kind','controller_kind','vtn_kind',)




class ServicePrivilegeSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','service','role',)

class ServicePrivilegeIdSerializer(XOSModelSerializer):
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
        model = ServicePrivilege
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','service','role',)




class ServiceInstanceSerializer(serializers.HyperlinkedModelSerializer):
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
        model = ServiceInstance
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner',)

class ServiceInstanceIdSerializer(XOSModelSerializer):
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
        model = ServiceInstance
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner',)




serializerLookUp = {

                 ServiceAttribute: ServiceAttributeSerializer,

                 ControllerImages: ControllerImagesSerializer,

                 ControllerSitePrivilege: ControllerSitePrivilegeSerializer,

                 Image: ImageSerializer,

                 ControllerNetwork: ControllerNetworkSerializer,

                 Site: SiteSerializer,

                 SliceRole: SliceRoleSerializer,

                 XOSGuiExtension: XOSGuiExtensionSerializer,

                 ServiceInstanceLink: ServiceInstanceLinkSerializer,

                 SlicePrivilege: SlicePrivilegeSerializer,

                 ControllerPrivilege: ControllerPrivilegeSerializer,

                 Flavor: FlavorSerializer,

                 ServiceRole: ServiceRoleSerializer,

                 ControllerSite: ControllerSiteSerializer,

                 ControllerSlice: ControllerSliceSerializer,

                 ServiceDependency: ServiceDependencySerializer,

                 Network: NetworkSerializer,

                 ControllerRole: ControllerRoleSerializer,

                 Diag: DiagSerializer,

                 Port: PortSerializer,

                 Instance: InstanceSerializer,

                 Role: RoleSerializer,

                 ServiceInterface: ServiceInterfaceSerializer,

                 NodeLabel: NodeLabelSerializer,

                 Privilege: PrivilegeSerializer,

                 Node: NodeSerializer,

                 AddressPool: AddressPoolSerializer,

                 DashboardView: DashboardViewSerializer,

                 NetworkParameter: NetworkParameterSerializer,

                 ImageDeployments: ImageDeploymentsSerializer,

                 ControllerUser: ControllerUserSerializer,

                 ServiceMonitoringAgentInfo: ServiceMonitoringAgentInfoSerializer,

                 ControllerDashboardView: ControllerDashboardViewSerializer,

                 UserDashboardView: UserDashboardViewSerializer,

                 Controller: ControllerSerializer,

                 Slice: SliceSerializer,

                 User: UserSerializer,

                 Deployment: DeploymentSerializer,

                 SitePrivilege: SitePrivilegeSerializer,

                 SiteRole: SiteRoleSerializer,

                 XOS: XOSSerializer,

                 NetworkSlice: NetworkSliceSerializer,

                 Service: ServiceSerializer,

                 ControllerSlicePrivilege: ControllerSlicePrivilegeSerializer,

                 ServiceInstanceAttribute: ServiceInstanceAttributeSerializer,

                 DeploymentPrivilege: DeploymentPrivilegeSerializer,

                 NetworkParameterType: NetworkParameterTypeSerializer,

                 SiteDeployment: SiteDeploymentSerializer,

                 TenantWithContainer: TenantWithContainerSerializer,

                 DeploymentRole: DeploymentRoleSerializer,

                 Tag: TagSerializer,

                 InterfaceType: InterfaceTypeSerializer,

                 NetworkTemplate: NetworkTemplateSerializer,

                 ServicePrivilege: ServicePrivilegeSerializer,

                 ServiceInstance: ServiceInstanceSerializer,

                 None: None,
                }

# Based on core/views/*.py


class ServiceAttributeList(XOSListCreateAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer
    id_serializer_class = ServiceAttributeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceAttribute.select_by_user(self.request.user)


class ServiceAttributeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceAttribute.objects.select_related().all()
    serializer_class = ServiceAttributeSerializer
    id_serializer_class = ServiceAttributeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceAttribute.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerImagesList(XOSListCreateAPIView):
    queryset = ControllerImages.objects.select_related().all()
    serializer_class = ControllerImagesSerializer
    id_serializer_class = ControllerImagesIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','glance_image_id','image','controller',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerImages.select_by_user(self.request.user)


class ControllerImagesDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerImages.objects.select_related().all()
    serializer_class = ControllerImagesSerializer
    id_serializer_class = ControllerImagesIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerImages.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerSitePrivilegeList(XOSListCreateAPIView):
    queryset = ControllerSitePrivilege.objects.select_related().all()
    serializer_class = ControllerSitePrivilegeSerializer
    id_serializer_class = ControllerSitePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','site_privilege',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSitePrivilege.select_by_user(self.request.user)


class ControllerSitePrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerSitePrivilege.objects.select_related().all()
    serializer_class = ControllerSitePrivilegeSerializer
    id_serializer_class = ControllerSitePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSitePrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ImageList(XOSListCreateAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','kind','disk_format','container_format','path','tag',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Image.select_by_user(self.request.user)


class ImageDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Image.objects.select_related().all()
    serializer_class = ImageSerializer
    id_serializer_class = ImageIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Image.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerNetworkList(XOSListCreateAPIView):
    queryset = ControllerNetwork.objects.select_related().all()
    serializer_class = ControllerNetworkSerializer
    id_serializer_class = ControllerNetworkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','subnet','start_ip','stop_ip','net_id','router_id','subnet_id','gateway','segmentation_id','network','controller',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerNetwork.select_by_user(self.request.user)


class ControllerNetworkDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerNetwork.objects.select_related().all()
    serializer_class = ControllerNetworkSerializer
    id_serializer_class = ControllerNetworkIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerNetwork.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SiteList(XOSListCreateAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_url','enabled','hosts_nodes','hosts_users','longitude','latitude','login_base','is_public','abbreviated_name','deployments',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Site.select_by_user(self.request.user)


class SiteDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Site.objects.select_related().all()
    serializer_class = SiteSerializer
    id_serializer_class = SiteIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Site.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SliceRoleList(XOSListCreateAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SliceRole.select_by_user(self.request.user)


class SliceRoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SliceRole.objects.select_related().all()
    serializer_class = SliceRoleSerializer
    id_serializer_class = SliceRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SliceRole.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class XOSGuiExtensionList(XOSListCreateAPIView):
    queryset = XOSGuiExtension.objects.select_related().all()
    serializer_class = XOSGuiExtensionSerializer
    id_serializer_class = XOSGuiExtensionIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','files',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return XOSGuiExtension.select_by_user(self.request.user)


class XOSGuiExtensionDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = XOSGuiExtension.objects.select_related().all()
    serializer_class = XOSGuiExtensionSerializer
    id_serializer_class = XOSGuiExtensionIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return XOSGuiExtension.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceInstanceLinkList(XOSListCreateAPIView):
    queryset = ServiceInstanceLink.objects.select_related().all()
    serializer_class = ServiceInstanceLinkSerializer
    id_serializer_class = ServiceInstanceLinkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','provider_service_instance','subscriber_service_instance','subscriber_service','subscriber_network',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstanceLink.select_by_user(self.request.user)


class ServiceInstanceLinkDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceInstanceLink.objects.select_related().all()
    serializer_class = ServiceInstanceLinkSerializer
    id_serializer_class = ServiceInstanceLinkIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstanceLink.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SlicePrivilegeList(XOSListCreateAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','slice','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SlicePrivilege.select_by_user(self.request.user)


class SlicePrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SlicePrivilege.objects.select_related().all()
    serializer_class = SlicePrivilegeSerializer
    id_serializer_class = SlicePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SlicePrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerPrivilegeList(XOSListCreateAPIView):
    queryset = ControllerPrivilege.objects.select_related().all()
    serializer_class = ControllerPrivilegeSerializer
    id_serializer_class = ControllerPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','privilege',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerPrivilege.select_by_user(self.request.user)


class ControllerPrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerPrivilege.objects.select_related().all()
    serializer_class = ControllerPrivilegeSerializer
    id_serializer_class = ControllerPrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerPrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class FlavorList(XOSListCreateAPIView):
    queryset = Flavor.objects.select_related().all()
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','flavor',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Flavor.select_by_user(self.request.user)


class FlavorDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Flavor.objects.select_related().all()
    serializer_class = FlavorSerializer
    id_serializer_class = FlavorIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Flavor.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceRoleList(XOSListCreateAPIView):
    queryset = ServiceRole.objects.select_related().all()
    serializer_class = ServiceRoleSerializer
    id_serializer_class = ServiceRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceRole.select_by_user(self.request.user)


class ServiceRoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceRole.objects.select_related().all()
    serializer_class = ServiceRoleSerializer
    id_serializer_class = ServiceRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceRole.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerSiteList(XOSListCreateAPIView):
    queryset = ControllerSite.objects.select_related().all()
    serializer_class = ControllerSiteSerializer
    id_serializer_class = ControllerSiteIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','site','controller',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSite.select_by_user(self.request.user)


class ControllerSiteDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerSite.objects.select_related().all()
    serializer_class = ControllerSiteSerializer
    id_serializer_class = ControllerSiteIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSite.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerSliceList(XOSListCreateAPIView):
    queryset = ControllerSlice.objects.select_related().all()
    serializer_class = ControllerSliceSerializer
    id_serializer_class = ControllerSliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','tenant_id','controller','slice',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSlice.select_by_user(self.request.user)


class ControllerSliceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerSlice.objects.select_related().all()
    serializer_class = ControllerSliceSerializer
    id_serializer_class = ControllerSliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSlice.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceDependencyList(XOSListCreateAPIView):
    queryset = ServiceDependency.objects.select_related().all()
    serializer_class = ServiceDependencySerializer
    id_serializer_class = ServiceDependencyIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','connect_method','provider_service','subscriber_service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceDependency.select_by_user(self.request.user)


class ServiceDependencyDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceDependency.objects.select_related().all()
    serializer_class = ServiceDependencySerializer
    id_serializer_class = ServiceDependencyIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceDependency.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NetworkList(XOSListCreateAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','subnet','start_ip','end_ip','ports','labels','permit_all_slices','autoconnect','template','owner','slices','slices','instances',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Network.select_by_user(self.request.user)


class NetworkDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Network.objects.select_related().all()
    serializer_class = NetworkSerializer
    id_serializer_class = NetworkIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Network.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerRoleList(XOSListCreateAPIView):
    queryset = ControllerRole.objects.select_related().all()
    serializer_class = ControllerRoleSerializer
    id_serializer_class = ControllerRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerRole.select_by_user(self.request.user)


class ControllerRoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerRole.objects.select_related().all()
    serializer_class = ControllerRoleSerializer
    id_serializer_class = ControllerRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerRole.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class DiagList(XOSListCreateAPIView):
    queryset = Diag.objects.select_related().all()
    serializer_class = DiagSerializer
    id_serializer_class = DiagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Diag.select_by_user(self.request.user)


class DiagDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Diag.objects.select_related().all()
    serializer_class = DiagSerializer
    id_serializer_class = DiagIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Diag.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class PortList(XOSListCreateAPIView):
    queryset = Port.objects.select_related().all()
    serializer_class = PortSerializer
    id_serializer_class = PortIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','ip','port_id','mac','xos_created','network','instance',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Port.select_by_user(self.request.user)


class PortDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Port.objects.select_related().all()
    serializer_class = PortSerializer
    id_serializer_class = PortIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Port.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class InstanceList(XOSListCreateAPIView):
    queryset = Instance.objects.select_related().all()
    serializer_class = InstanceSerializer
    id_serializer_class = InstanceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','instance_id','instance_uuid','name','instance_name','ip','numberCores','userData','isolation','volumes','image','creator','slice','deployment','node','flavor','parent','networks',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Instance.select_by_user(self.request.user)


class InstanceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Instance.objects.select_related().all()
    serializer_class = InstanceSerializer
    id_serializer_class = InstanceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Instance.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class RoleList(XOSListCreateAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_type','role','description',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Role.select_by_user(self.request.user)


class RoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    id_serializer_class = RoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Role.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceInterfaceList(XOSListCreateAPIView):
    queryset = ServiceInterface.objects.select_related().all()
    serializer_class = ServiceInterfaceSerializer
    id_serializer_class = ServiceInterfaceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','service','interface_type',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInterface.select_by_user(self.request.user)


class ServiceInterfaceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceInterface.objects.select_related().all()
    serializer_class = ServiceInterfaceSerializer
    id_serializer_class = ServiceInterfaceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInterface.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NodeLabelList(XOSListCreateAPIView):
    queryset = NodeLabel.objects.select_related().all()
    serializer_class = NodeLabelSerializer
    id_serializer_class = NodeLabelIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','nodes',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NodeLabel.select_by_user(self.request.user)


class NodeLabelDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = NodeLabel.objects.select_related().all()
    serializer_class = NodeLabelSerializer
    id_serializer_class = NodeLabelIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NodeLabel.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class PrivilegeList(XOSListCreateAPIView):
    queryset = Privilege.objects.select_related().all()
    serializer_class = PrivilegeSerializer
    id_serializer_class = PrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','accessor_id','accessor_type','object_id','object_type','permission','granted','expires',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Privilege.select_by_user(self.request.user)


class PrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Privilege.objects.select_related().all()
    serializer_class = PrivilegeSerializer
    id_serializer_class = PrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Privilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NodeList(XOSListCreateAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','site_deployment','nodelabels',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Node.select_by_user(self.request.user)


class NodeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Node.objects.select_related().all()
    serializer_class = NodeSerializer
    id_serializer_class = NodeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Node.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class AddressPoolList(XOSListCreateAPIView):
    queryset = AddressPool.objects.select_related().all()
    serializer_class = AddressPoolSerializer
    id_serializer_class = AddressPoolIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','addresses','gateway_ip','gateway_mac','cidr','inuse','service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return AddressPool.select_by_user(self.request.user)


class AddressPoolDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = AddressPool.objects.select_related().all()
    serializer_class = AddressPoolSerializer
    id_serializer_class = AddressPoolIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return AddressPool.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class DashboardViewList(XOSListCreateAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','url','enabled','icon','icon_active','controllers','deployments',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DashboardView.select_by_user(self.request.user)


class DashboardViewDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = DashboardView.objects.select_related().all()
    serializer_class = DashboardViewSerializer
    id_serializer_class = DashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DashboardView.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NetworkParameterList(XOSListCreateAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','value','content_type','object_id','parameter',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkParameter.select_by_user(self.request.user)


class NetworkParameterDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = NetworkParameter.objects.select_related().all()
    serializer_class = NetworkParameterSerializer
    id_serializer_class = NetworkParameterIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkParameter.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ImageDeploymentsList(XOSListCreateAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    id_serializer_class = ImageDeploymentsIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','image','deployment',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ImageDeployments.select_by_user(self.request.user)


class ImageDeploymentsDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ImageDeployments.objects.select_related().all()
    serializer_class = ImageDeploymentsSerializer
    id_serializer_class = ImageDeploymentsIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ImageDeployments.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerUserList(XOSListCreateAPIView):
    queryset = ControllerUser.objects.select_related().all()
    serializer_class = ControllerUserSerializer
    id_serializer_class = ControllerUserIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','kuser_id','user','controller',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerUser.select_by_user(self.request.user)


class ControllerUserDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerUser.objects.select_related().all()
    serializer_class = ControllerUserSerializer
    id_serializer_class = ControllerUserIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerUser.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceMonitoringAgentInfoList(XOSListCreateAPIView):
    queryset = ServiceMonitoringAgentInfo.objects.select_related().all()
    serializer_class = ServiceMonitoringAgentInfoSerializer
    id_serializer_class = ServiceMonitoringAgentInfoIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','target_uri','service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceMonitoringAgentInfo.select_by_user(self.request.user)


class ServiceMonitoringAgentInfoDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceMonitoringAgentInfo.objects.select_related().all()
    serializer_class = ServiceMonitoringAgentInfoSerializer
    id_serializer_class = ServiceMonitoringAgentInfoIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceMonitoringAgentInfo.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerDashboardViewList(XOSListCreateAPIView):
    queryset = ControllerDashboardView.objects.select_related().all()
    serializer_class = ControllerDashboardViewSerializer
    id_serializer_class = ControllerDashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','enabled','url','controller','dashboardView',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerDashboardView.select_by_user(self.request.user)


class ControllerDashboardViewDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerDashboardView.objects.select_related().all()
    serializer_class = ControllerDashboardViewSerializer
    id_serializer_class = ControllerDashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerDashboardView.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class UserDashboardViewList(XOSListCreateAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','dashboardView','order',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return UserDashboardView.select_by_user(self.request.user)


class UserDashboardViewDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = UserDashboardView.objects.select_related().all()
    serializer_class = UserDashboardViewSerializer
    id_serializer_class = UserDashboardViewIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return UserDashboardView.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerList(XOSListCreateAPIView):
    queryset = Controller.objects.select_related().all()
    serializer_class = ControllerSerializer
    id_serializer_class = ControllerIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','backend_type','version','auth_url','admin_user','admin_password','admin_tenant','domain','rabbit_host','rabbit_user','rabbit_password','deployment','dashboardviews',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Controller.select_by_user(self.request.user)


class ControllerDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Controller.objects.select_related().all()
    serializer_class = ControllerSerializer
    id_serializer_class = ControllerIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Controller.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SliceList(XOSListCreateAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','enabled','description','slice_url','max_instances','network','exposed_ports','mount_data_sets','default_isolation','site','service','creator','default_flavor','default_image','default_node','networks','networks',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Slice.select_by_user(self.request.user)


class SliceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.select_related().all()
    serializer_class = SliceSerializer
    id_serializer_class = SliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Slice.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class UserList(XOSListCreateAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','password','last_login','email','username','firstname','lastname','phone','user_url','site','public_key','is_active','is_admin','is_staff','is_readonly','is_registering','is_appuser','login_page','created','updated','enacted','policed','backend_status','backend_need_delete','backend_need_reap','deleted','write_protect','lazy_blocked','no_sync','no_policy','timezone','policy_status',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return User.select_by_user(self.request.user)


class UserDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    id_serializer_class = UserIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return User.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class DeploymentList(XOSListCreateAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','accessControl','sites','dashboardviews',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Deployment.select_by_user(self.request.user)


class DeploymentDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.select_related().all()
    serializer_class = DeploymentSerializer
    id_serializer_class = DeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Deployment.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SitePrivilegeList(XOSListCreateAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','site','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SitePrivilege.select_by_user(self.request.user)


class SitePrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SitePrivilege.objects.select_related().all()
    serializer_class = SitePrivilegeSerializer
    id_serializer_class = SitePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SitePrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SiteRoleList(XOSListCreateAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteRole.select_by_user(self.request.user)


class SiteRoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SiteRole.objects.select_related().all()
    serializer_class = SiteRoleSerializer
    id_serializer_class = SiteRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteRole.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class XOSList(XOSListCreateAPIView):
    queryset = XOS.objects.select_related().all()
    serializer_class = XOSSerializer
    id_serializer_class = XOSIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return XOS.select_by_user(self.request.user)


class XOSDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = XOS.objects.select_related().all()
    serializer_class = XOSSerializer
    id_serializer_class = XOSIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return XOS.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NetworkSliceList(XOSListCreateAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','network','slice',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkSlice.select_by_user(self.request.user)


class NetworkSliceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = NetworkSlice.objects.select_related().all()
    serializer_class = NetworkSliceSerializer
    id_serializer_class = NetworkSliceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkSlice.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceList(XOSListCreateAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Service.select_by_user(self.request.user)


class ServiceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related().all()
    serializer_class = ServiceSerializer
    id_serializer_class = ServiceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Service.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ControllerSlicePrivilegeList(XOSListCreateAPIView):
    queryset = ControllerSlicePrivilege.objects.select_related().all()
    serializer_class = ControllerSlicePrivilegeSerializer
    id_serializer_class = ControllerSlicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role_id','controller','slice_privilege',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSlicePrivilege.select_by_user(self.request.user)


class ControllerSlicePrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ControllerSlicePrivilege.objects.select_related().all()
    serializer_class = ControllerSlicePrivilegeSerializer
    id_serializer_class = ControllerSlicePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ControllerSlicePrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceInstanceAttributeList(XOSListCreateAPIView):
    queryset = ServiceInstanceAttribute.objects.select_related().all()
    serializer_class = ServiceInstanceAttributeSerializer
    id_serializer_class = ServiceInstanceAttributeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','service_instance',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstanceAttribute.select_by_user(self.request.user)


class ServiceInstanceAttributeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceInstanceAttribute.objects.select_related().all()
    serializer_class = ServiceInstanceAttributeSerializer
    id_serializer_class = ServiceInstanceAttributeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstanceAttribute.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class DeploymentPrivilegeList(XOSListCreateAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','deployment','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DeploymentPrivilege.select_by_user(self.request.user)


class DeploymentPrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = DeploymentPrivilege.objects.select_related().all()
    serializer_class = DeploymentPrivilegeSerializer
    id_serializer_class = DeploymentPrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DeploymentPrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NetworkParameterTypeList(XOSListCreateAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkParameterType.select_by_user(self.request.user)


class NetworkParameterTypeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = NetworkParameterType.objects.select_related().all()
    serializer_class = NetworkParameterTypeSerializer
    id_serializer_class = NetworkParameterTypeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkParameterType.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SiteDeploymentList(XOSListCreateAPIView):
    queryset = SiteDeployment.objects.select_related().all()
    serializer_class = SiteDeploymentSerializer
    id_serializer_class = SiteDeploymentIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','availability_zone','site','deployment','controller',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteDeployment.select_by_user(self.request.user)


class SiteDeploymentDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SiteDeployment.objects.select_related().all()
    serializer_class = SiteDeploymentSerializer
    id_serializer_class = SiteDeploymentIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteDeployment.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class TenantWithContainerList(XOSListCreateAPIView):
    queryset = TenantWithContainer.objects.select_related().all()
    serializer_class = TenantWithContainerSerializer
    id_serializer_class = TenantWithContainerIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner','external_hostname','external_container','instance','creator',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return TenantWithContainer.select_by_user(self.request.user)


class TenantWithContainerDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = TenantWithContainer.objects.select_related().all()
    serializer_class = TenantWithContainerSerializer
    id_serializer_class = TenantWithContainerIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return TenantWithContainer.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class DeploymentRoleList(XOSListCreateAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DeploymentRole.select_by_user(self.request.user)


class DeploymentRoleDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = DeploymentRole.objects.select_related().all()
    serializer_class = DeploymentRoleSerializer
    id_serializer_class = DeploymentRoleIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return DeploymentRole.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class TagList(XOSListCreateAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','value','content_type','object_id','service',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Tag.select_by_user(self.request.user)


class TagDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.select_related().all()
    serializer_class = TagSerializer
    id_serializer_class = TagIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return Tag.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class InterfaceTypeList(XOSListCreateAPIView):
    queryset = InterfaceType.objects.select_related().all()
    serializer_class = InterfaceTypeSerializer
    id_serializer_class = InterfaceTypeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','direction',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return InterfaceType.select_by_user(self.request.user)


class InterfaceTypeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = InterfaceType.objects.select_related().all()
    serializer_class = InterfaceTypeSerializer
    id_serializer_class = InterfaceTypeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return InterfaceType.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class NetworkTemplateList(XOSListCreateAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','description','visibility','translation','access','shared_network_name','shared_network_id','topology_kind','controller_kind','vtn_kind',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkTemplate.select_by_user(self.request.user)


class NetworkTemplateDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = NetworkTemplate.objects.select_related().all()
    serializer_class = NetworkTemplateSerializer
    id_serializer_class = NetworkTemplateIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return NetworkTemplate.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServicePrivilegeList(XOSListCreateAPIView):
    queryset = ServicePrivilege.objects.select_related().all()
    serializer_class = ServicePrivilegeSerializer
    id_serializer_class = ServicePrivilegeIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','user','service','role',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServicePrivilege.select_by_user(self.request.user)


class ServicePrivilegeDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServicePrivilege.objects.select_related().all()
    serializer_class = ServicePrivilegeSerializer
    id_serializer_class = ServicePrivilegeIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServicePrivilege.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceInstanceList(XOSListCreateAPIView):
    queryset = ServiceInstance.objects.select_related().all()
    serializer_class = ServiceInstanceSerializer
    id_serializer_class = ServiceInstanceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_need_delete','backend_need_reap','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','policy_status','name','service_specific_id','service_specific_attribute','owner',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstance.select_by_user(self.request.user)


class ServiceInstanceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceInstance.objects.select_related().all()
    serializer_class = ServiceInstanceSerializer
    id_serializer_class = ServiceInstanceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceInstance.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView

