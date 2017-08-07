
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import grpc_client
from grpc_client import Empty

c=grpc_client.InsecureClient("xos-core.cord.lab")


print "testing insecure ListServiceControllerResource...",
c.stub.ListServiceControllerResource(Empty())
print "Okay"
print "testing insecure ListXOSVolume...",
c.stub.ListXOSVolume(Empty())
print "Okay"
print "testing insecure ListServiceAttribute...",
c.stub.ListServiceAttribute(Empty())
print "Okay"
print "testing insecure ListControllerImages...",
c.stub.ListControllerImages(Empty())
print "Okay"
print "testing insecure ListControllerSitePrivilege...",
c.stub.ListControllerSitePrivilege(Empty())
print "Okay"
print "testing insecure ListImage...",
c.stub.ListImage(Empty())
print "Okay"
print "testing insecure ListControllerNetwork...",
c.stub.ListControllerNetwork(Empty())
print "Okay"
print "testing insecure ListSite...",
c.stub.ListSite(Empty())
print "Okay"
print "testing insecure ListLibrary...",
c.stub.ListLibrary(Empty())
print "Okay"
print "testing insecure ListSliceRole...",
c.stub.ListSliceRole(Empty())
print "Okay"
print "testing insecure ListSiteDeployment...",
c.stub.ListSiteDeployment(Empty())
print "Okay"
print "testing insecure ListXOSComponentLink...",
c.stub.ListXOSComponentLink(Empty())
print "Okay"
print "testing insecure ListTenantPrivilege...",
c.stub.ListTenantPrivilege(Empty())
print "Okay"
print "testing insecure ListTag...",
c.stub.ListTag(Empty())
print "Okay"
print "testing insecure ListServiceMonitoringAgentInfo...",
c.stub.ListServiceMonitoringAgentInfo(Empty())
print "Okay"
print "testing insecure ListXOSComponent...",
c.stub.ListXOSComponent(Empty())
print "Okay"
print "testing insecure ListInvoice...",
c.stub.ListInvoice(Empty())
print "Okay"
print "testing insecure ListSlicePrivilege...",
c.stub.ListSlicePrivilege(Empty())
print "Okay"
print "testing insecure ListFlavor...",
c.stub.ListFlavor(Empty())
print "Okay"
print "testing insecure ListPort...",
c.stub.ListPort(Empty())
print "Okay"
print "testing insecure ListServiceRole...",
c.stub.ListServiceRole(Empty())
print "Okay"
print "testing insecure ListControllerSite...",
c.stub.ListControllerSite(Empty())
print "Okay"
print "testing insecure ListControllerSlice...",
c.stub.ListControllerSlice(Empty())
print "Okay"
print "testing insecure ListTenantRole...",
c.stub.ListTenantRole(Empty())
print "Okay"
print "testing insecure ListSlice...",
c.stub.ListSlice(Empty())
print "Okay"
print "testing insecure ListLoadableModuleResource...",
c.stub.ListLoadableModuleResource(Empty())
print "Okay"
print "testing insecure ListControllerRole...",
c.stub.ListControllerRole(Empty())
print "Okay"
print "testing insecure ListDiag...",
c.stub.ListDiag(Empty())
print "Okay"
print "testing insecure ListXOS...",
c.stub.ListXOS(Empty())
print "Okay"
print "testing insecure ListServiceClass...",
c.stub.ListServiceClass(Empty())
print "Okay"
print "testing insecure ListTenantAttribute...",
c.stub.ListTenantAttribute(Empty())
print "Okay"
print "testing insecure ListSiteRole...",
c.stub.ListSiteRole(Empty())
print "Okay"
print "testing insecure ListSubscriber...",
c.stub.ListSubscriber(Empty())
print "Okay"
print "testing insecure ListInstance...",
c.stub.ListInstance(Empty())
print "Okay"
print "testing insecure ListCharge...",
c.stub.ListCharge(Empty())
print "Okay"
print "testing insecure ListProgram...",
c.stub.ListProgram(Empty())
print "Okay"
print "testing insecure ListRole...",
c.stub.ListRole(Empty())
print "Okay"
print "testing insecure ListNodeLabel...",
c.stub.ListNodeLabel(Empty())
print "Okay"
print "testing insecure ListNetworkTemplate...",
c.stub.ListNetworkTemplate(Empty())
print "Okay"
print "testing insecure ListServiceController...",
c.stub.ListServiceController(Empty())
print "Okay"
print "testing insecure ListLoadableModule...",
c.stub.ListLoadableModule(Empty())
print "Okay"
print "testing insecure ListUsableObject...",
c.stub.ListUsableObject(Empty())
print "Okay"
print "testing insecure ListNode...",
c.stub.ListNode(Empty())
print "Okay"
print "testing insecure ListAddressPool...",
c.stub.ListAddressPool(Empty())
print "Okay"
print "testing insecure ListDashboardView...",
c.stub.ListDashboardView(Empty())
print "Okay"
print "testing insecure ListNetworkParameter...",
c.stub.ListNetworkParameter(Empty())
print "Okay"
print "testing insecure ListImageDeployments...",
c.stub.ListImageDeployments(Empty())
print "Okay"
print "testing insecure ListControllerUser...",
c.stub.ListControllerUser(Empty())
print "Okay"
print "testing insecure ListReservedResource...",
c.stub.ListReservedResource(Empty())
print "Okay"
print "testing insecure ListJournalEntry...",
c.stub.ListJournalEntry(Empty())
print "Okay"
print "testing insecure ListUserCredential...",
c.stub.ListUserCredential(Empty())
print "Okay"
print "testing insecure ListControllerDashboardView...",
c.stub.ListControllerDashboardView(Empty())
print "Okay"
print "testing insecure ListUserDashboardView...",
c.stub.ListUserDashboardView(Empty())
print "Okay"
print "testing insecure ListController...",
c.stub.ListController(Empty())
print "Okay"
print "testing insecure ListTenantRootRole...",
c.stub.ListTenantRootRole(Empty())
print "Okay"
print "testing insecure ListDeployment...",
c.stub.ListDeployment(Empty())
print "Okay"
print "testing insecure ListReservation...",
c.stub.ListReservation(Empty())
print "Okay"
print "testing insecure ListSitePrivilege...",
c.stub.ListSitePrivilege(Empty())
print "Okay"
print "testing insecure ListPayment...",
c.stub.ListPayment(Empty())
print "Okay"
print "testing insecure ListTenant...",
c.stub.ListTenant(Empty())
print "Okay"
print "testing insecure ListNetwork...",
c.stub.ListNetwork(Empty())
print "Okay"
print "testing insecure ListNetworkSlice...",
c.stub.ListNetworkSlice(Empty())
print "Okay"
print "testing insecure ListAccount...",
c.stub.ListAccount(Empty())
print "Okay"
print "testing insecure ListTenantRoot...",
c.stub.ListTenantRoot(Empty())
print "Okay"
print "testing insecure ListService...",
c.stub.ListService(Empty())
print "Okay"
print "testing insecure ListControllerSlicePrivilege...",
c.stub.ListControllerSlicePrivilege(Empty())
print "Okay"
print "testing insecure ListSiteCredential...",
c.stub.ListSiteCredential(Empty())
print "Okay"
print "testing insecure ListDeploymentPrivilege...",
c.stub.ListDeploymentPrivilege(Empty())
print "Okay"
print "testing insecure ListNetworkParameterType...",
c.stub.ListNetworkParameterType(Empty())
print "Okay"
print "testing insecure ListProvider...",
c.stub.ListProvider(Empty())
print "Okay"
print "testing insecure ListTenantWithContainer...",
c.stub.ListTenantWithContainer(Empty())
print "Okay"
print "testing insecure ListDeploymentRole...",
c.stub.ListDeploymentRole(Empty())
print "Okay"
print "testing insecure ListProject...",
c.stub.ListProject(Empty())
print "Okay"
print "testing insecure ListTenantRootPrivilege...",
c.stub.ListTenantRootPrivilege(Empty())
print "Okay"
print "testing insecure ListXOSComponentVolume...",
c.stub.ListXOSComponentVolume(Empty())
print "Okay"
print "testing insecure ListSliceCredential...",
c.stub.ListSliceCredential(Empty())
print "Okay"
print "testing insecure ListSliceTag...",
c.stub.ListSliceTag(Empty())
print "Okay"
print "testing insecure ListCoarseTenant...",
c.stub.ListCoarseTenant(Empty())
print "Okay"
print "testing insecure ListRouter...",
c.stub.ListRouter(Empty())
print "Okay"
print "testing insecure ListServiceResource...",
c.stub.ListServiceResource(Empty())
print "Okay"
print "testing insecure ListServicePrivilege...",
c.stub.ListServicePrivilege(Empty())
print "Okay"
print "testing insecure ListUser...",
c.stub.ListUser(Empty())
print "Okay"

c=grpc_client.SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")


print "testing secure ListServiceControllerResource...",
c.stub.ListServiceControllerResource(Empty())
print "Okay"
print "testing secure ListXOSVolume...",
c.stub.ListXOSVolume(Empty())
print "Okay"
print "testing secure ListServiceAttribute...",
c.stub.ListServiceAttribute(Empty())
print "Okay"
print "testing secure ListControllerImages...",
c.stub.ListControllerImages(Empty())
print "Okay"
print "testing secure ListControllerSitePrivilege...",
c.stub.ListControllerSitePrivilege(Empty())
print "Okay"
print "testing secure ListImage...",
c.stub.ListImage(Empty())
print "Okay"
print "testing secure ListControllerNetwork...",
c.stub.ListControllerNetwork(Empty())
print "Okay"
print "testing secure ListSite...",
c.stub.ListSite(Empty())
print "Okay"
print "testing secure ListLibrary...",
c.stub.ListLibrary(Empty())
print "Okay"
print "testing secure ListSliceRole...",
c.stub.ListSliceRole(Empty())
print "Okay"
print "testing secure ListSiteDeployment...",
c.stub.ListSiteDeployment(Empty())
print "Okay"
print "testing secure ListXOSComponentLink...",
c.stub.ListXOSComponentLink(Empty())
print "Okay"
print "testing secure ListTenantPrivilege...",
c.stub.ListTenantPrivilege(Empty())
print "Okay"
print "testing secure ListTag...",
c.stub.ListTag(Empty())
print "Okay"
print "testing secure ListServiceMonitoringAgentInfo...",
c.stub.ListServiceMonitoringAgentInfo(Empty())
print "Okay"
print "testing secure ListXOSComponent...",
c.stub.ListXOSComponent(Empty())
print "Okay"
print "testing secure ListInvoice...",
c.stub.ListInvoice(Empty())
print "Okay"
print "testing secure ListSlicePrivilege...",
c.stub.ListSlicePrivilege(Empty())
print "Okay"
print "testing secure ListFlavor...",
c.stub.ListFlavor(Empty())
print "Okay"
print "testing secure ListPort...",
c.stub.ListPort(Empty())
print "Okay"
print "testing secure ListServiceRole...",
c.stub.ListServiceRole(Empty())
print "Okay"
print "testing secure ListControllerSite...",
c.stub.ListControllerSite(Empty())
print "Okay"
print "testing secure ListControllerSlice...",
c.stub.ListControllerSlice(Empty())
print "Okay"
print "testing secure ListTenantRole...",
c.stub.ListTenantRole(Empty())
print "Okay"
print "testing secure ListSlice...",
c.stub.ListSlice(Empty())
print "Okay"
print "testing secure ListLoadableModuleResource...",
c.stub.ListLoadableModuleResource(Empty())
print "Okay"
print "testing secure ListControllerRole...",
c.stub.ListControllerRole(Empty())
print "Okay"
print "testing secure ListDiag...",
c.stub.ListDiag(Empty())
print "Okay"
print "testing secure ListXOS...",
c.stub.ListXOS(Empty())
print "Okay"
print "testing secure ListServiceClass...",
c.stub.ListServiceClass(Empty())
print "Okay"
print "testing secure ListTenantAttribute...",
c.stub.ListTenantAttribute(Empty())
print "Okay"
print "testing secure ListSiteRole...",
c.stub.ListSiteRole(Empty())
print "Okay"
print "testing secure ListSubscriber...",
c.stub.ListSubscriber(Empty())
print "Okay"
print "testing secure ListInstance...",
c.stub.ListInstance(Empty())
print "Okay"
print "testing secure ListCharge...",
c.stub.ListCharge(Empty())
print "Okay"
print "testing secure ListProgram...",
c.stub.ListProgram(Empty())
print "Okay"
print "testing secure ListRole...",
c.stub.ListRole(Empty())
print "Okay"
print "testing secure ListNodeLabel...",
c.stub.ListNodeLabel(Empty())
print "Okay"
print "testing secure ListNetworkTemplate...",
c.stub.ListNetworkTemplate(Empty())
print "Okay"
print "testing secure ListServiceController...",
c.stub.ListServiceController(Empty())
print "Okay"
print "testing secure ListLoadableModule...",
c.stub.ListLoadableModule(Empty())
print "Okay"
print "testing secure ListUsableObject...",
c.stub.ListUsableObject(Empty())
print "Okay"
print "testing secure ListNode...",
c.stub.ListNode(Empty())
print "Okay"
print "testing secure ListAddressPool...",
c.stub.ListAddressPool(Empty())
print "Okay"
print "testing secure ListDashboardView...",
c.stub.ListDashboardView(Empty())
print "Okay"
print "testing secure ListNetworkParameter...",
c.stub.ListNetworkParameter(Empty())
print "Okay"
print "testing secure ListImageDeployments...",
c.stub.ListImageDeployments(Empty())
print "Okay"
print "testing secure ListControllerUser...",
c.stub.ListControllerUser(Empty())
print "Okay"
print "testing secure ListReservedResource...",
c.stub.ListReservedResource(Empty())
print "Okay"
print "testing secure ListJournalEntry...",
c.stub.ListJournalEntry(Empty())
print "Okay"
print "testing secure ListUserCredential...",
c.stub.ListUserCredential(Empty())
print "Okay"
print "testing secure ListControllerDashboardView...",
c.stub.ListControllerDashboardView(Empty())
print "Okay"
print "testing secure ListUserDashboardView...",
c.stub.ListUserDashboardView(Empty())
print "Okay"
print "testing secure ListController...",
c.stub.ListController(Empty())
print "Okay"
print "testing secure ListTenantRootRole...",
c.stub.ListTenantRootRole(Empty())
print "Okay"
print "testing secure ListDeployment...",
c.stub.ListDeployment(Empty())
print "Okay"
print "testing secure ListReservation...",
c.stub.ListReservation(Empty())
print "Okay"
print "testing secure ListSitePrivilege...",
c.stub.ListSitePrivilege(Empty())
print "Okay"
print "testing secure ListPayment...",
c.stub.ListPayment(Empty())
print "Okay"
print "testing secure ListTenant...",
c.stub.ListTenant(Empty())
print "Okay"
print "testing secure ListNetwork...",
c.stub.ListNetwork(Empty())
print "Okay"
print "testing secure ListNetworkSlice...",
c.stub.ListNetworkSlice(Empty())
print "Okay"
print "testing secure ListAccount...",
c.stub.ListAccount(Empty())
print "Okay"
print "testing secure ListTenantRoot...",
c.stub.ListTenantRoot(Empty())
print "Okay"
print "testing secure ListService...",
c.stub.ListService(Empty())
print "Okay"
print "testing secure ListControllerSlicePrivilege...",
c.stub.ListControllerSlicePrivilege(Empty())
print "Okay"
print "testing secure ListSiteCredential...",
c.stub.ListSiteCredential(Empty())
print "Okay"
print "testing secure ListDeploymentPrivilege...",
c.stub.ListDeploymentPrivilege(Empty())
print "Okay"
print "testing secure ListNetworkParameterType...",
c.stub.ListNetworkParameterType(Empty())
print "Okay"
print "testing secure ListProvider...",
c.stub.ListProvider(Empty())
print "Okay"
print "testing secure ListTenantWithContainer...",
c.stub.ListTenantWithContainer(Empty())
print "Okay"
print "testing secure ListDeploymentRole...",
c.stub.ListDeploymentRole(Empty())
print "Okay"
print "testing secure ListProject...",
c.stub.ListProject(Empty())
print "Okay"
print "testing secure ListTenantRootPrivilege...",
c.stub.ListTenantRootPrivilege(Empty())
print "Okay"
print "testing secure ListXOSComponentVolume...",
c.stub.ListXOSComponentVolume(Empty())
print "Okay"
print "testing secure ListSliceCredential...",
c.stub.ListSliceCredential(Empty())
print "Okay"
print "testing secure ListSliceTag...",
c.stub.ListSliceTag(Empty())
print "Okay"
print "testing secure ListCoarseTenant...",
c.stub.ListCoarseTenant(Empty())
print "Okay"
print "testing secure ListRouter...",
c.stub.ListRouter(Empty())
print "Okay"
print "testing secure ListServiceResource...",
c.stub.ListServiceResource(Empty())
print "Okay"
print "testing secure ListServicePrivilege...",
c.stub.ListServicePrivilege(Empty())
print "Okay"
print "testing secure ListUser...",
c.stub.ListUser(Empty())
print "Okay"
