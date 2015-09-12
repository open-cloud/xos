from view_common import *
from core.xoslib.objects.sliceplus import SlicePlus

# This was intended to serve as a download feature for the tenant view. Found
# a better way to do it. This is deprecated.

class DownloadSSHCommandsView(View):
    url = r'^sshcommands/(?P<sliceid>\d+)/$'

    def get(self, request, sliceid=None, **kwargs):
        #slice = Slices.objects.get(id=sliceid);
        #for instance in slice.instances.all():
        #    if (instance.instance_id && instance.instance_name):

        slice = SlicePlus.objects.get(id=sliceid)

        return HttpResponse(slice.getSliceInfo()["sshCommands"], content_type='text/text')

