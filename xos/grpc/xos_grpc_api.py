import base64
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
from core.models import *
from xos.exceptions import *

class XosService(xos_pb2.xosServicer):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

    def getProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.__name__)
        return pClass

    def getPluralProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.__name__ + "s")
        return pClass

    def convertFloat(self, x):
        if not x:
            return 0
        else:
            return float(x)

    def convertDateTime(self, x):
        if not x:
            return 0
        else:
            return time.mktime(x.timetuple())

    def convertForeignKey(self, x):
        if not x:
            return 0
        else:
            return int(x.id)

    def objToProto(self, obj):
        p_obj = self.getProtoClass(obj.__class__)()
        for field in obj._meta.fields:
            if getattr(obj, field.name) == None:
                continue

            ftype = field.get_internal_type()
            if (ftype == "CharField") or (ftype == "TextField") or (ftype == "SlugField"):
                setattr(p_obj, field.name, str(getattr(obj, field.name)))
            elif (ftype == "BooleanField"):
                setattr(p_obj, field.name, getattr(obj, field.name))
            elif (ftype == "AutoField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "ForeignKey"):
                setattr(p_obj, field.name+"_id", self.convertForeignKey(getattr(obj, field.name)))
            elif (ftype == "DateTimeField"):
                setattr(p_obj, field.name, self.convertDateTime(getattr(obj, field.name)))
            elif (ftype == "FloatField"):
                setattr(p_obj, field.name, float(getattr(obj, field.name)))
            elif (ftype == "GenericIPAddressField"):
                setattr(p_obj, field.name, str(getattr(obj, field.name)))
        return p_obj

    def protoToArgs(self, djangoClass, message):
        args={}
        fmap={}
        fset={}
        for field in djangoClass._meta.fields:
            fmap[field.name] = field
            if field.get_internal_type() == "ForeignKey":
               # foreign key can be represented as an id
               fmap[field.name + "_id"] = field

        for (fieldDesc, val) in message.ListFields():
            name = fieldDesc.name
            if name in fmap:
                if (name=="id"):
                    # don't let anyone set the id
                    continue
                ftype = fmap[name].get_internal_type()
                if (ftype == "CharField") or (ftype == "TextField") or (ftype == "SlugField"):
                    args[name] = val
                elif (ftype == "BooleanField"):
                    args[name] = val
                elif (ftype == "AutoField"):
                    args[name] = val
                elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField"):
                    args[name] = val
                elif (ftype == "ForeignKey"):
                    args[name] = val # field name already has "_id" at the end
                elif (ftype == "DateTimeField"):
                    pass # do something special here
                elif (ftype == "FloatField"):
                    args[name] = val
                elif (ftype == "GenericIPAddressField"):
                    args[name] = val
                fset[name] = True

        return args

    def querysetToProto(self, djangoClass, queryset):
        objs = queryset
        p_objs = self.getPluralProtoClass(djangoClass)()

        for obj in objs:
           new_obj = p_objs.items.add()
           new_obj.CopyFrom(self.objToProto(obj))

        return p_objs

    def get(self, djangoClass, id):
        obj = djangoClass.objects.get(id=id)
        return self.objToProto(obj)

    def create(self, djangoClass, user, request):
        args = self.protoToArgs(djangoClass, request)
        new_obj = djangoClass(**args)
        new_obj.caller = user
        if (not user) or (not new_obj.can_update(user)):
            raise XOSPermissionDenied()
        new_obj.save()
        return self.objToProto(new_obj)

    def update(self, djangoClass, user, id, message):
        obj = djangoClass.objects.get(id=id)
        obj.caller = user
        if (not user) or (not obj.can_update(user)):
            raise XOSPermissionDenied()
        args = self.protoToArgs(djangoClass, message)
        for (k,v) in args.iteritems():
            setattr(obj, k, v)
        obj.save()
        return self.objToProto(obj)

    def delete(self, djangoClass, user, id):
      obj = djangoClass.objects.get(id=id)
      if (not user) or (not obj.can_update(user)):
          raise XOSPermissionDenied()
      obj.delete()
      return Empty()

    def authenticate(self, context):
        for (k, v) in context.invocation_metadata():
            if (k.lower()=="authorization"):
                (method, auth) = v.split(" ",1)
                if (method.lower() == "basic"):
                    auth = base64.b64decode(auth)
                    (username, password) = auth.split(":")
                    user = django_authenticate(username=username, password=password)
                    if not user:
                        raise Exception("failed to authenticate %s:%s" % (username, password))
                    print "authenticated %s:%s as %s" % (username, password, user)
                    return user

        return None



    def ListServiceControllerResource(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceControllerResource, ServiceControllerResource.objects.all())

    def GetServiceControllerResource(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceControllerResource, request.id)

    def CreateServiceControllerResource(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceControllerResource, user, request)

    def DeleteServiceControllerResource(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceControllerResource, user, request.id)

    def UpdateServiceControllerResource(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceControllerResource, user, request.id, request)


    def ListXOSVolume(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(XOSVolume, XOSVolume.objects.all())

    def GetXOSVolume(self, request, context):
      user=self.authenticate(context)
      return self.get(XOSVolume, request.id)

    def CreateXOSVolume(self, request, context):
      user=self.authenticate(context)
      return self.create(XOSVolume, user, request)

    def DeleteXOSVolume(self, request, context):
      user=self.authenticate(context)
      return self.delete(XOSVolume, user, request.id)

    def UpdateXOSVolume(self, request, context):
      user=self.authenticate(context)
      return self.update(XOSVolume, user, request.id, request)


    def ListServiceAttribute(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceAttribute, ServiceAttribute.objects.all())

    def GetServiceAttribute(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceAttribute, request.id)

    def CreateServiceAttribute(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceAttribute, user, request)

    def DeleteServiceAttribute(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceAttribute, user, request.id)

    def UpdateServiceAttribute(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceAttribute, user, request.id, request)


    def ListControllerImages(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerImages, ControllerImages.objects.all())

    def GetControllerImages(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerImages, request.id)

    def CreateControllerImages(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerImages, user, request)

    def DeleteControllerImages(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerImages, user, request.id)

    def UpdateControllerImages(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerImages, user, request.id, request)


    def ListControllerSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerSitePrivilege, ControllerSitePrivilege.objects.all())

    def GetControllerSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerSitePrivilege, request.id)

    def CreateControllerSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerSitePrivilege, user, request)

    def DeleteControllerSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerSitePrivilege, user, request.id)

    def UpdateControllerSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerSitePrivilege, user, request.id, request)


    def ListImage(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Image, Image.objects.all())

    def GetImage(self, request, context):
      user=self.authenticate(context)
      return self.get(Image, request.id)

    def CreateImage(self, request, context):
      user=self.authenticate(context)
      return self.create(Image, user, request)

    def DeleteImage(self, request, context):
      user=self.authenticate(context)
      return self.delete(Image, user, request.id)

    def UpdateImage(self, request, context):
      user=self.authenticate(context)
      return self.update(Image, user, request.id, request)


    def ListControllerNetwork(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerNetwork, ControllerNetwork.objects.all())

    def GetControllerNetwork(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerNetwork, request.id)

    def CreateControllerNetwork(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerNetwork, user, request)

    def DeleteControllerNetwork(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerNetwork, user, request.id)

    def UpdateControllerNetwork(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerNetwork, user, request.id, request)


    def ListSite(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Site, Site.objects.all())

    def GetSite(self, request, context):
      user=self.authenticate(context)
      return self.get(Site, request.id)

    def CreateSite(self, request, context):
      user=self.authenticate(context)
      return self.create(Site, user, request)

    def DeleteSite(self, request, context):
      user=self.authenticate(context)
      return self.delete(Site, user, request.id)

    def UpdateSite(self, request, context):
      user=self.authenticate(context)
      return self.update(Site, user, request.id, request)


    def ListLibrary(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Library, Library.objects.all())

    def GetLibrary(self, request, context):
      user=self.authenticate(context)
      return self.get(Library, request.id)

    def CreateLibrary(self, request, context):
      user=self.authenticate(context)
      return self.create(Library, user, request)

    def DeleteLibrary(self, request, context):
      user=self.authenticate(context)
      return self.delete(Library, user, request.id)

    def UpdateLibrary(self, request, context):
      user=self.authenticate(context)
      return self.update(Library, user, request.id, request)


    def ListSliceRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SliceRole, SliceRole.objects.all())

    def GetSliceRole(self, request, context):
      user=self.authenticate(context)
      return self.get(SliceRole, request.id)

    def CreateSliceRole(self, request, context):
      user=self.authenticate(context)
      return self.create(SliceRole, user, request)

    def DeleteSliceRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(SliceRole, user, request.id)

    def UpdateSliceRole(self, request, context):
      user=self.authenticate(context)
      return self.update(SliceRole, user, request.id, request)


    def ListSiteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SiteDeployment, SiteDeployment.objects.all())

    def GetSiteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.get(SiteDeployment, request.id)

    def CreateSiteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.create(SiteDeployment, user, request)

    def DeleteSiteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.delete(SiteDeployment, user, request.id)

    def UpdateSiteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.update(SiteDeployment, user, request.id, request)


    def ListXOSComponentLink(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(XOSComponentLink, XOSComponentLink.objects.all())

    def GetXOSComponentLink(self, request, context):
      user=self.authenticate(context)
      return self.get(XOSComponentLink, request.id)

    def CreateXOSComponentLink(self, request, context):
      user=self.authenticate(context)
      return self.create(XOSComponentLink, user, request)

    def DeleteXOSComponentLink(self, request, context):
      user=self.authenticate(context)
      return self.delete(XOSComponentLink, user, request.id)

    def UpdateXOSComponentLink(self, request, context):
      user=self.authenticate(context)
      return self.update(XOSComponentLink, user, request.id, request)


    def ListTenantPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantPrivilege, TenantPrivilege.objects.all())

    def GetTenantPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantPrivilege, request.id)

    def CreateTenantPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantPrivilege, user, request)

    def DeleteTenantPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantPrivilege, user, request.id)

    def UpdateTenantPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantPrivilege, user, request.id, request)


    def ListTag(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Tag, Tag.objects.all())

    def GetTag(self, request, context):
      user=self.authenticate(context)
      return self.get(Tag, request.id)

    def CreateTag(self, request, context):
      user=self.authenticate(context)
      return self.create(Tag, user, request)

    def DeleteTag(self, request, context):
      user=self.authenticate(context)
      return self.delete(Tag, user, request.id)

    def UpdateTag(self, request, context):
      user=self.authenticate(context)
      return self.update(Tag, user, request.id, request)


    def ListServiceMonitoringAgentInfo(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceMonitoringAgentInfo, ServiceMonitoringAgentInfo.objects.all())

    def GetServiceMonitoringAgentInfo(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceMonitoringAgentInfo, request.id)

    def CreateServiceMonitoringAgentInfo(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceMonitoringAgentInfo, user, request)

    def DeleteServiceMonitoringAgentInfo(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceMonitoringAgentInfo, user, request.id)

    def UpdateServiceMonitoringAgentInfo(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceMonitoringAgentInfo, user, request.id, request)


    def ListXOSComponent(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(XOSComponent, XOSComponent.objects.all())

    def GetXOSComponent(self, request, context):
      user=self.authenticate(context)
      return self.get(XOSComponent, request.id)

    def CreateXOSComponent(self, request, context):
      user=self.authenticate(context)
      return self.create(XOSComponent, user, request)

    def DeleteXOSComponent(self, request, context):
      user=self.authenticate(context)
      return self.delete(XOSComponent, user, request.id)

    def UpdateXOSComponent(self, request, context):
      user=self.authenticate(context)
      return self.update(XOSComponent, user, request.id, request)


    def ListInvoice(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Invoice, Invoice.objects.all())

    def GetInvoice(self, request, context):
      user=self.authenticate(context)
      return self.get(Invoice, request.id)

    def CreateInvoice(self, request, context):
      user=self.authenticate(context)
      return self.create(Invoice, user, request)

    def DeleteInvoice(self, request, context):
      user=self.authenticate(context)
      return self.delete(Invoice, user, request.id)

    def UpdateInvoice(self, request, context):
      user=self.authenticate(context)
      return self.update(Invoice, user, request.id, request)


    def ListSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SlicePrivilege, SlicePrivilege.objects.all())

    def GetSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(SlicePrivilege, request.id)

    def CreateSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(SlicePrivilege, user, request)

    def DeleteSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(SlicePrivilege, user, request.id)

    def UpdateSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(SlicePrivilege, user, request.id, request)


    def ListFlavor(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Flavor, Flavor.objects.all())

    def GetFlavor(self, request, context):
      user=self.authenticate(context)
      return self.get(Flavor, request.id)

    def CreateFlavor(self, request, context):
      user=self.authenticate(context)
      return self.create(Flavor, user, request)

    def DeleteFlavor(self, request, context):
      user=self.authenticate(context)
      return self.delete(Flavor, user, request.id)

    def UpdateFlavor(self, request, context):
      user=self.authenticate(context)
      return self.update(Flavor, user, request.id, request)


    def ListPort(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Port, Port.objects.all())

    def GetPort(self, request, context):
      user=self.authenticate(context)
      return self.get(Port, request.id)

    def CreatePort(self, request, context):
      user=self.authenticate(context)
      return self.create(Port, user, request)

    def DeletePort(self, request, context):
      user=self.authenticate(context)
      return self.delete(Port, user, request.id)

    def UpdatePort(self, request, context):
      user=self.authenticate(context)
      return self.update(Port, user, request.id, request)


    def ListServiceRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceRole, ServiceRole.objects.all())

    def GetServiceRole(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceRole, request.id)

    def CreateServiceRole(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceRole, user, request)

    def DeleteServiceRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceRole, user, request.id)

    def UpdateServiceRole(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceRole, user, request.id, request)


    def ListControllerSite(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerSite, ControllerSite.objects.all())

    def GetControllerSite(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerSite, request.id)

    def CreateControllerSite(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerSite, user, request)

    def DeleteControllerSite(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerSite, user, request.id)

    def UpdateControllerSite(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerSite, user, request.id, request)


    def ListControllerSlice(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerSlice, ControllerSlice.objects.all())

    def GetControllerSlice(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerSlice, request.id)

    def CreateControllerSlice(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerSlice, user, request)

    def DeleteControllerSlice(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerSlice, user, request.id)

    def UpdateControllerSlice(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerSlice, user, request.id, request)


    def ListTenantRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantRole, TenantRole.objects.all())

    def GetTenantRole(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantRole, request.id)

    def CreateTenantRole(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantRole, user, request)

    def DeleteTenantRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantRole, user, request.id)

    def UpdateTenantRole(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantRole, user, request.id, request)


    def ListSlice(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Slice, Slice.objects.all())

    def GetSlice(self, request, context):
      user=self.authenticate(context)
      return self.get(Slice, request.id)

    def CreateSlice(self, request, context):
      user=self.authenticate(context)
      return self.create(Slice, user, request)

    def DeleteSlice(self, request, context):
      user=self.authenticate(context)
      return self.delete(Slice, user, request.id)

    def UpdateSlice(self, request, context):
      user=self.authenticate(context)
      return self.update(Slice, user, request.id, request)


    def ListLoadableModuleResource(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(LoadableModuleResource, LoadableModuleResource.objects.all())

    def GetLoadableModuleResource(self, request, context):
      user=self.authenticate(context)
      return self.get(LoadableModuleResource, request.id)

    def CreateLoadableModuleResource(self, request, context):
      user=self.authenticate(context)
      return self.create(LoadableModuleResource, user, request)

    def DeleteLoadableModuleResource(self, request, context):
      user=self.authenticate(context)
      return self.delete(LoadableModuleResource, user, request.id)

    def UpdateLoadableModuleResource(self, request, context):
      user=self.authenticate(context)
      return self.update(LoadableModuleResource, user, request.id, request)


    def ListControllerRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerRole, ControllerRole.objects.all())

    def GetControllerRole(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerRole, request.id)

    def CreateControllerRole(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerRole, user, request)

    def DeleteControllerRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerRole, user, request.id)

    def UpdateControllerRole(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerRole, user, request.id, request)


    def ListDiag(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Diag, Diag.objects.all())

    def GetDiag(self, request, context):
      user=self.authenticate(context)
      return self.get(Diag, request.id)

    def CreateDiag(self, request, context):
      user=self.authenticate(context)
      return self.create(Diag, user, request)

    def DeleteDiag(self, request, context):
      user=self.authenticate(context)
      return self.delete(Diag, user, request.id)

    def UpdateDiag(self, request, context):
      user=self.authenticate(context)
      return self.update(Diag, user, request.id, request)


    def ListXOS(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(XOS, XOS.objects.all())

    def GetXOS(self, request, context):
      user=self.authenticate(context)
      return self.get(XOS, request.id)

    def CreateXOS(self, request, context):
      user=self.authenticate(context)
      return self.create(XOS, user, request)

    def DeleteXOS(self, request, context):
      user=self.authenticate(context)
      return self.delete(XOS, user, request.id)

    def UpdateXOS(self, request, context):
      user=self.authenticate(context)
      return self.update(XOS, user, request.id, request)


    def ListServiceClass(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceClass, ServiceClass.objects.all())

    def GetServiceClass(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceClass, request.id)

    def CreateServiceClass(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceClass, user, request)

    def DeleteServiceClass(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceClass, user, request.id)

    def UpdateServiceClass(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceClass, user, request.id, request)


    def ListTenantAttribute(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantAttribute, TenantAttribute.objects.all())

    def GetTenantAttribute(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantAttribute, request.id)

    def CreateTenantAttribute(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantAttribute, user, request)

    def DeleteTenantAttribute(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantAttribute, user, request.id)

    def UpdateTenantAttribute(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantAttribute, user, request.id, request)


    def ListSiteRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SiteRole, SiteRole.objects.all())

    def GetSiteRole(self, request, context):
      user=self.authenticate(context)
      return self.get(SiteRole, request.id)

    def CreateSiteRole(self, request, context):
      user=self.authenticate(context)
      return self.create(SiteRole, user, request)

    def DeleteSiteRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(SiteRole, user, request.id)

    def UpdateSiteRole(self, request, context):
      user=self.authenticate(context)
      return self.update(SiteRole, user, request.id, request)


    def ListSubscriber(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Subscriber, Subscriber.objects.all())

    def GetSubscriber(self, request, context):
      user=self.authenticate(context)
      return self.get(Subscriber, request.id)

    def CreateSubscriber(self, request, context):
      user=self.authenticate(context)
      return self.create(Subscriber, user, request)

    def DeleteSubscriber(self, request, context):
      user=self.authenticate(context)
      return self.delete(Subscriber, user, request.id)

    def UpdateSubscriber(self, request, context):
      user=self.authenticate(context)
      return self.update(Subscriber, user, request.id, request)


    def ListInstance(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Instance, Instance.objects.all())

    def GetInstance(self, request, context):
      user=self.authenticate(context)
      return self.get(Instance, request.id)

    def CreateInstance(self, request, context):
      user=self.authenticate(context)
      return self.create(Instance, user, request)

    def DeleteInstance(self, request, context):
      user=self.authenticate(context)
      return self.delete(Instance, user, request.id)

    def UpdateInstance(self, request, context):
      user=self.authenticate(context)
      return self.update(Instance, user, request.id, request)


    def ListCharge(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Charge, Charge.objects.all())

    def GetCharge(self, request, context):
      user=self.authenticate(context)
      return self.get(Charge, request.id)

    def CreateCharge(self, request, context):
      user=self.authenticate(context)
      return self.create(Charge, user, request)

    def DeleteCharge(self, request, context):
      user=self.authenticate(context)
      return self.delete(Charge, user, request.id)

    def UpdateCharge(self, request, context):
      user=self.authenticate(context)
      return self.update(Charge, user, request.id, request)


    def ListProgram(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Program, Program.objects.all())

    def GetProgram(self, request, context):
      user=self.authenticate(context)
      return self.get(Program, request.id)

    def CreateProgram(self, request, context):
      user=self.authenticate(context)
      return self.create(Program, user, request)

    def DeleteProgram(self, request, context):
      user=self.authenticate(context)
      return self.delete(Program, user, request.id)

    def UpdateProgram(self, request, context):
      user=self.authenticate(context)
      return self.update(Program, user, request.id, request)


    def ListRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Role, Role.objects.all())

    def GetRole(self, request, context):
      user=self.authenticate(context)
      return self.get(Role, request.id)

    def CreateRole(self, request, context):
      user=self.authenticate(context)
      return self.create(Role, user, request)

    def DeleteRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(Role, user, request.id)

    def UpdateRole(self, request, context):
      user=self.authenticate(context)
      return self.update(Role, user, request.id, request)


    def ListNodeLabel(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(NodeLabel, NodeLabel.objects.all())

    def GetNodeLabel(self, request, context):
      user=self.authenticate(context)
      return self.get(NodeLabel, request.id)

    def CreateNodeLabel(self, request, context):
      user=self.authenticate(context)
      return self.create(NodeLabel, user, request)

    def DeleteNodeLabel(self, request, context):
      user=self.authenticate(context)
      return self.delete(NodeLabel, user, request.id)

    def UpdateNodeLabel(self, request, context):
      user=self.authenticate(context)
      return self.update(NodeLabel, user, request.id, request)


    def ListNetworkTemplate(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(NetworkTemplate, NetworkTemplate.objects.all())

    def GetNetworkTemplate(self, request, context):
      user=self.authenticate(context)
      return self.get(NetworkTemplate, request.id)

    def CreateNetworkTemplate(self, request, context):
      user=self.authenticate(context)
      return self.create(NetworkTemplate, user, request)

    def DeleteNetworkTemplate(self, request, context):
      user=self.authenticate(context)
      return self.delete(NetworkTemplate, user, request.id)

    def UpdateNetworkTemplate(self, request, context):
      user=self.authenticate(context)
      return self.update(NetworkTemplate, user, request.id, request)


    def ListServiceController(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceController, ServiceController.objects.all())

    def GetServiceController(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceController, request.id)

    def CreateServiceController(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceController, user, request)

    def DeleteServiceController(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceController, user, request.id)

    def UpdateServiceController(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceController, user, request.id, request)


    def ListLoadableModule(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(LoadableModule, LoadableModule.objects.all())

    def GetLoadableModule(self, request, context):
      user=self.authenticate(context)
      return self.get(LoadableModule, request.id)

    def CreateLoadableModule(self, request, context):
      user=self.authenticate(context)
      return self.create(LoadableModule, user, request)

    def DeleteLoadableModule(self, request, context):
      user=self.authenticate(context)
      return self.delete(LoadableModule, user, request.id)

    def UpdateLoadableModule(self, request, context):
      user=self.authenticate(context)
      return self.update(LoadableModule, user, request.id, request)


    def ListUsableObject(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(UsableObject, UsableObject.objects.all())

    def GetUsableObject(self, request, context):
      user=self.authenticate(context)
      return self.get(UsableObject, request.id)

    def CreateUsableObject(self, request, context):
      user=self.authenticate(context)
      return self.create(UsableObject, user, request)

    def DeleteUsableObject(self, request, context):
      user=self.authenticate(context)
      return self.delete(UsableObject, user, request.id)

    def UpdateUsableObject(self, request, context):
      user=self.authenticate(context)
      return self.update(UsableObject, user, request.id, request)


    def ListNode(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Node, Node.objects.all())

    def GetNode(self, request, context):
      user=self.authenticate(context)
      return self.get(Node, request.id)

    def CreateNode(self, request, context):
      user=self.authenticate(context)
      return self.create(Node, user, request)

    def DeleteNode(self, request, context):
      user=self.authenticate(context)
      return self.delete(Node, user, request.id)

    def UpdateNode(self, request, context):
      user=self.authenticate(context)
      return self.update(Node, user, request.id, request)


    def ListAddressPool(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(AddressPool, AddressPool.objects.all())

    def GetAddressPool(self, request, context):
      user=self.authenticate(context)
      return self.get(AddressPool, request.id)

    def CreateAddressPool(self, request, context):
      user=self.authenticate(context)
      return self.create(AddressPool, user, request)

    def DeleteAddressPool(self, request, context):
      user=self.authenticate(context)
      return self.delete(AddressPool, user, request.id)

    def UpdateAddressPool(self, request, context):
      user=self.authenticate(context)
      return self.update(AddressPool, user, request.id, request)


    def ListDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(DashboardView, DashboardView.objects.all())

    def GetDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.get(DashboardView, request.id)

    def CreateDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.create(DashboardView, user, request)

    def DeleteDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.delete(DashboardView, user, request.id)

    def UpdateDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.update(DashboardView, user, request.id, request)


    def ListNetworkParameter(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(NetworkParameter, NetworkParameter.objects.all())

    def GetNetworkParameter(self, request, context):
      user=self.authenticate(context)
      return self.get(NetworkParameter, request.id)

    def CreateNetworkParameter(self, request, context):
      user=self.authenticate(context)
      return self.create(NetworkParameter, user, request)

    def DeleteNetworkParameter(self, request, context):
      user=self.authenticate(context)
      return self.delete(NetworkParameter, user, request.id)

    def UpdateNetworkParameter(self, request, context):
      user=self.authenticate(context)
      return self.update(NetworkParameter, user, request.id, request)


    def ListImageDeployments(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ImageDeployments, ImageDeployments.objects.all())

    def GetImageDeployments(self, request, context):
      user=self.authenticate(context)
      return self.get(ImageDeployments, request.id)

    def CreateImageDeployments(self, request, context):
      user=self.authenticate(context)
      return self.create(ImageDeployments, user, request)

    def DeleteImageDeployments(self, request, context):
      user=self.authenticate(context)
      return self.delete(ImageDeployments, user, request.id)

    def UpdateImageDeployments(self, request, context):
      user=self.authenticate(context)
      return self.update(ImageDeployments, user, request.id, request)


    def ListControllerUser(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerUser, ControllerUser.objects.all())

    def GetControllerUser(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerUser, request.id)

    def CreateControllerUser(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerUser, user, request)

    def DeleteControllerUser(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerUser, user, request.id)

    def UpdateControllerUser(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerUser, user, request.id, request)


    def ListReservedResource(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ReservedResource, ReservedResource.objects.all())

    def GetReservedResource(self, request, context):
      user=self.authenticate(context)
      return self.get(ReservedResource, request.id)

    def CreateReservedResource(self, request, context):
      user=self.authenticate(context)
      return self.create(ReservedResource, user, request)

    def DeleteReservedResource(self, request, context):
      user=self.authenticate(context)
      return self.delete(ReservedResource, user, request.id)

    def UpdateReservedResource(self, request, context):
      user=self.authenticate(context)
      return self.update(ReservedResource, user, request.id, request)


    def ListJournalEntry(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(JournalEntry, JournalEntry.objects.all())

    def GetJournalEntry(self, request, context):
      user=self.authenticate(context)
      return self.get(JournalEntry, request.id)

    def CreateJournalEntry(self, request, context):
      user=self.authenticate(context)
      return self.create(JournalEntry, user, request)

    def DeleteJournalEntry(self, request, context):
      user=self.authenticate(context)
      return self.delete(JournalEntry, user, request.id)

    def UpdateJournalEntry(self, request, context):
      user=self.authenticate(context)
      return self.update(JournalEntry, user, request.id, request)


    def ListUserCredential(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(UserCredential, UserCredential.objects.all())

    def GetUserCredential(self, request, context):
      user=self.authenticate(context)
      return self.get(UserCredential, request.id)

    def CreateUserCredential(self, request, context):
      user=self.authenticate(context)
      return self.create(UserCredential, user, request)

    def DeleteUserCredential(self, request, context):
      user=self.authenticate(context)
      return self.delete(UserCredential, user, request.id)

    def UpdateUserCredential(self, request, context):
      user=self.authenticate(context)
      return self.update(UserCredential, user, request.id, request)


    def ListControllerDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerDashboardView, ControllerDashboardView.objects.all())

    def GetControllerDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerDashboardView, request.id)

    def CreateControllerDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerDashboardView, user, request)

    def DeleteControllerDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerDashboardView, user, request.id)

    def UpdateControllerDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerDashboardView, user, request.id, request)


    def ListUserDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(UserDashboardView, UserDashboardView.objects.all())

    def GetUserDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.get(UserDashboardView, request.id)

    def CreateUserDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.create(UserDashboardView, user, request)

    def DeleteUserDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.delete(UserDashboardView, user, request.id)

    def UpdateUserDashboardView(self, request, context):
      user=self.authenticate(context)
      return self.update(UserDashboardView, user, request.id, request)


    def ListController(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Controller, Controller.objects.all())

    def GetController(self, request, context):
      user=self.authenticate(context)
      return self.get(Controller, request.id)

    def CreateController(self, request, context):
      user=self.authenticate(context)
      return self.create(Controller, user, request)

    def DeleteController(self, request, context):
      user=self.authenticate(context)
      return self.delete(Controller, user, request.id)

    def UpdateController(self, request, context):
      user=self.authenticate(context)
      return self.update(Controller, user, request.id, request)


    def ListTenantRootRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantRootRole, TenantRootRole.objects.all())

    def GetTenantRootRole(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantRootRole, request.id)

    def CreateTenantRootRole(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantRootRole, user, request)

    def DeleteTenantRootRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantRootRole, user, request.id)

    def UpdateTenantRootRole(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantRootRole, user, request.id, request)


    def ListDeployment(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Deployment, Deployment.objects.all())

    def GetDeployment(self, request, context):
      user=self.authenticate(context)
      return self.get(Deployment, request.id)

    def CreateDeployment(self, request, context):
      user=self.authenticate(context)
      return self.create(Deployment, user, request)

    def DeleteDeployment(self, request, context):
      user=self.authenticate(context)
      return self.delete(Deployment, user, request.id)

    def UpdateDeployment(self, request, context):
      user=self.authenticate(context)
      return self.update(Deployment, user, request.id, request)


    def ListReservation(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Reservation, Reservation.objects.all())

    def GetReservation(self, request, context):
      user=self.authenticate(context)
      return self.get(Reservation, request.id)

    def CreateReservation(self, request, context):
      user=self.authenticate(context)
      return self.create(Reservation, user, request)

    def DeleteReservation(self, request, context):
      user=self.authenticate(context)
      return self.delete(Reservation, user, request.id)

    def UpdateReservation(self, request, context):
      user=self.authenticate(context)
      return self.update(Reservation, user, request.id, request)


    def ListSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SitePrivilege, SitePrivilege.objects.all())

    def GetSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(SitePrivilege, request.id)

    def CreateSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(SitePrivilege, user, request)

    def DeleteSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(SitePrivilege, user, request.id)

    def UpdateSitePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(SitePrivilege, user, request.id, request)


    def ListPayment(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Payment, Payment.objects.all())

    def GetPayment(self, request, context):
      user=self.authenticate(context)
      return self.get(Payment, request.id)

    def CreatePayment(self, request, context):
      user=self.authenticate(context)
      return self.create(Payment, user, request)

    def DeletePayment(self, request, context):
      user=self.authenticate(context)
      return self.delete(Payment, user, request.id)

    def UpdatePayment(self, request, context):
      user=self.authenticate(context)
      return self.update(Payment, user, request.id, request)


    def ListTenant(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Tenant, Tenant.objects.all())

    def GetTenant(self, request, context):
      user=self.authenticate(context)
      return self.get(Tenant, request.id)

    def CreateTenant(self, request, context):
      user=self.authenticate(context)
      return self.create(Tenant, user, request)

    def DeleteTenant(self, request, context):
      user=self.authenticate(context)
      return self.delete(Tenant, user, request.id)

    def UpdateTenant(self, request, context):
      user=self.authenticate(context)
      return self.update(Tenant, user, request.id, request)


    def ListNetwork(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Network, Network.objects.all())

    def GetNetwork(self, request, context):
      user=self.authenticate(context)
      return self.get(Network, request.id)

    def CreateNetwork(self, request, context):
      user=self.authenticate(context)
      return self.create(Network, user, request)

    def DeleteNetwork(self, request, context):
      user=self.authenticate(context)
      return self.delete(Network, user, request.id)

    def UpdateNetwork(self, request, context):
      user=self.authenticate(context)
      return self.update(Network, user, request.id, request)


    def ListNetworkSlice(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(NetworkSlice, NetworkSlice.objects.all())

    def GetNetworkSlice(self, request, context):
      user=self.authenticate(context)
      return self.get(NetworkSlice, request.id)

    def CreateNetworkSlice(self, request, context):
      user=self.authenticate(context)
      return self.create(NetworkSlice, user, request)

    def DeleteNetworkSlice(self, request, context):
      user=self.authenticate(context)
      return self.delete(NetworkSlice, user, request.id)

    def UpdateNetworkSlice(self, request, context):
      user=self.authenticate(context)
      return self.update(NetworkSlice, user, request.id, request)


    def ListAccount(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Account, Account.objects.all())

    def GetAccount(self, request, context):
      user=self.authenticate(context)
      return self.get(Account, request.id)

    def CreateAccount(self, request, context):
      user=self.authenticate(context)
      return self.create(Account, user, request)

    def DeleteAccount(self, request, context):
      user=self.authenticate(context)
      return self.delete(Account, user, request.id)

    def UpdateAccount(self, request, context):
      user=self.authenticate(context)
      return self.update(Account, user, request.id, request)


    def ListTenantRoot(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantRoot, TenantRoot.objects.all())

    def GetTenantRoot(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantRoot, request.id)

    def CreateTenantRoot(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantRoot, user, request)

    def DeleteTenantRoot(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantRoot, user, request.id)

    def UpdateTenantRoot(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantRoot, user, request.id, request)


    def ListService(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Service, Service.objects.all())

    def GetService(self, request, context):
      user=self.authenticate(context)
      return self.get(Service, request.id)

    def CreateService(self, request, context):
      user=self.authenticate(context)
      return self.create(Service, user, request)

    def DeleteService(self, request, context):
      user=self.authenticate(context)
      return self.delete(Service, user, request.id)

    def UpdateService(self, request, context):
      user=self.authenticate(context)
      return self.update(Service, user, request.id, request)


    def ListControllerSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ControllerSlicePrivilege, ControllerSlicePrivilege.objects.all())

    def GetControllerSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(ControllerSlicePrivilege, request.id)

    def CreateControllerSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(ControllerSlicePrivilege, user, request)

    def DeleteControllerSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(ControllerSlicePrivilege, user, request.id)

    def UpdateControllerSlicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(ControllerSlicePrivilege, user, request.id, request)


    def ListSiteCredential(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SiteCredential, SiteCredential.objects.all())

    def GetSiteCredential(self, request, context):
      user=self.authenticate(context)
      return self.get(SiteCredential, request.id)

    def CreateSiteCredential(self, request, context):
      user=self.authenticate(context)
      return self.create(SiteCredential, user, request)

    def DeleteSiteCredential(self, request, context):
      user=self.authenticate(context)
      return self.delete(SiteCredential, user, request.id)

    def UpdateSiteCredential(self, request, context):
      user=self.authenticate(context)
      return self.update(SiteCredential, user, request.id, request)


    def ListDeploymentPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(DeploymentPrivilege, DeploymentPrivilege.objects.all())

    def GetDeploymentPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(DeploymentPrivilege, request.id)

    def CreateDeploymentPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(DeploymentPrivilege, user, request)

    def DeleteDeploymentPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(DeploymentPrivilege, user, request.id)

    def UpdateDeploymentPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(DeploymentPrivilege, user, request.id, request)


    def ListNetworkParameterType(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(NetworkParameterType, NetworkParameterType.objects.all())

    def GetNetworkParameterType(self, request, context):
      user=self.authenticate(context)
      return self.get(NetworkParameterType, request.id)

    def CreateNetworkParameterType(self, request, context):
      user=self.authenticate(context)
      return self.create(NetworkParameterType, user, request)

    def DeleteNetworkParameterType(self, request, context):
      user=self.authenticate(context)
      return self.delete(NetworkParameterType, user, request.id)

    def UpdateNetworkParameterType(self, request, context):
      user=self.authenticate(context)
      return self.update(NetworkParameterType, user, request.id, request)


    def ListProvider(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Provider, Provider.objects.all())

    def GetProvider(self, request, context):
      user=self.authenticate(context)
      return self.get(Provider, request.id)

    def CreateProvider(self, request, context):
      user=self.authenticate(context)
      return self.create(Provider, user, request)

    def DeleteProvider(self, request, context):
      user=self.authenticate(context)
      return self.delete(Provider, user, request.id)

    def UpdateProvider(self, request, context):
      user=self.authenticate(context)
      return self.update(Provider, user, request.id, request)


    def ListTenantWithContainer(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantWithContainer, TenantWithContainer.objects.all())

    def GetTenantWithContainer(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantWithContainer, request.id)

    def CreateTenantWithContainer(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantWithContainer, user, request)

    def DeleteTenantWithContainer(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantWithContainer, user, request.id)

    def UpdateTenantWithContainer(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantWithContainer, user, request.id, request)


    def ListDeploymentRole(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(DeploymentRole, DeploymentRole.objects.all())

    def GetDeploymentRole(self, request, context):
      user=self.authenticate(context)
      return self.get(DeploymentRole, request.id)

    def CreateDeploymentRole(self, request, context):
      user=self.authenticate(context)
      return self.create(DeploymentRole, user, request)

    def DeleteDeploymentRole(self, request, context):
      user=self.authenticate(context)
      return self.delete(DeploymentRole, user, request.id)

    def UpdateDeploymentRole(self, request, context):
      user=self.authenticate(context)
      return self.update(DeploymentRole, user, request.id, request)


    def ListProject(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Project, Project.objects.all())

    def GetProject(self, request, context):
      user=self.authenticate(context)
      return self.get(Project, request.id)

    def CreateProject(self, request, context):
      user=self.authenticate(context)
      return self.create(Project, user, request)

    def DeleteProject(self, request, context):
      user=self.authenticate(context)
      return self.delete(Project, user, request.id)

    def UpdateProject(self, request, context):
      user=self.authenticate(context)
      return self.update(Project, user, request.id, request)


    def ListTenantRootPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(TenantRootPrivilege, TenantRootPrivilege.objects.all())

    def GetTenantRootPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(TenantRootPrivilege, request.id)

    def CreateTenantRootPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(TenantRootPrivilege, user, request)

    def DeleteTenantRootPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(TenantRootPrivilege, user, request.id)

    def UpdateTenantRootPrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(TenantRootPrivilege, user, request.id, request)


    def ListXOSComponentVolume(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(XOSComponentVolume, XOSComponentVolume.objects.all())

    def GetXOSComponentVolume(self, request, context):
      user=self.authenticate(context)
      return self.get(XOSComponentVolume, request.id)

    def CreateXOSComponentVolume(self, request, context):
      user=self.authenticate(context)
      return self.create(XOSComponentVolume, user, request)

    def DeleteXOSComponentVolume(self, request, context):
      user=self.authenticate(context)
      return self.delete(XOSComponentVolume, user, request.id)

    def UpdateXOSComponentVolume(self, request, context):
      user=self.authenticate(context)
      return self.update(XOSComponentVolume, user, request.id, request)


    def ListSliceCredential(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SliceCredential, SliceCredential.objects.all())

    def GetSliceCredential(self, request, context):
      user=self.authenticate(context)
      return self.get(SliceCredential, request.id)

    def CreateSliceCredential(self, request, context):
      user=self.authenticate(context)
      return self.create(SliceCredential, user, request)

    def DeleteSliceCredential(self, request, context):
      user=self.authenticate(context)
      return self.delete(SliceCredential, user, request.id)

    def UpdateSliceCredential(self, request, context):
      user=self.authenticate(context)
      return self.update(SliceCredential, user, request.id, request)


    def ListSliceTag(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(SliceTag, SliceTag.objects.all())

    def GetSliceTag(self, request, context):
      user=self.authenticate(context)
      return self.get(SliceTag, request.id)

    def CreateSliceTag(self, request, context):
      user=self.authenticate(context)
      return self.create(SliceTag, user, request)

    def DeleteSliceTag(self, request, context):
      user=self.authenticate(context)
      return self.delete(SliceTag, user, request.id)

    def UpdateSliceTag(self, request, context):
      user=self.authenticate(context)
      return self.update(SliceTag, user, request.id, request)


    def ListCoarseTenant(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(CoarseTenant, CoarseTenant.objects.all())

    def GetCoarseTenant(self, request, context):
      user=self.authenticate(context)
      return self.get(CoarseTenant, request.id)

    def CreateCoarseTenant(self, request, context):
      user=self.authenticate(context)
      return self.create(CoarseTenant, user, request)

    def DeleteCoarseTenant(self, request, context):
      user=self.authenticate(context)
      return self.delete(CoarseTenant, user, request.id)

    def UpdateCoarseTenant(self, request, context):
      user=self.authenticate(context)
      return self.update(CoarseTenant, user, request.id, request)


    def ListRouter(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(Router, Router.objects.all())

    def GetRouter(self, request, context):
      user=self.authenticate(context)
      return self.get(Router, request.id)

    def CreateRouter(self, request, context):
      user=self.authenticate(context)
      return self.create(Router, user, request)

    def DeleteRouter(self, request, context):
      user=self.authenticate(context)
      return self.delete(Router, user, request.id)

    def UpdateRouter(self, request, context):
      user=self.authenticate(context)
      return self.update(Router, user, request.id, request)


    def ListServiceResource(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServiceResource, ServiceResource.objects.all())

    def GetServiceResource(self, request, context):
      user=self.authenticate(context)
      return self.get(ServiceResource, request.id)

    def CreateServiceResource(self, request, context):
      user=self.authenticate(context)
      return self.create(ServiceResource, user, request)

    def DeleteServiceResource(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServiceResource, user, request.id)

    def UpdateServiceResource(self, request, context):
      user=self.authenticate(context)
      return self.update(ServiceResource, user, request.id, request)


    def ListServicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(ServicePrivilege, ServicePrivilege.objects.all())

    def GetServicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.get(ServicePrivilege, request.id)

    def CreateServicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.create(ServicePrivilege, user, request)

    def DeleteServicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.delete(ServicePrivilege, user, request.id)

    def UpdateServicePrivilege(self, request, context):
      user=self.authenticate(context)
      return self.update(ServicePrivilege, user, request.id, request)


    def ListUser(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto(User, User.objects.all())

    def GetUser(self, request, context):
      user=self.authenticate(context)
      return self.get(User, request.id)

    def CreateUser(self, request, context):
      user=self.authenticate(context)
      return self.create(User, user, request)

    def DeleteUser(self, request, context):
      user=self.authenticate(context)
      return self.delete(User, user, request.id)

    def UpdateUser(self, request, context):
      user=self.authenticate(context)
      return self.update(User, user, request.id, request)



