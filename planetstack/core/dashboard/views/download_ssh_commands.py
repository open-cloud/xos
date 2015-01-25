from view_common import *
from core.xoslib.objects.sliceplus import SlicePlus

class DownloadSSHCommandsView(View):
    url = r'^sshcommands/(?P<sliceid>\d+)/$'

    def get(self, request, sliceid=None, **kwargs):
        #slice = Slices.objects.get(id=sliceid);
        #for sliver in slice.slivers.all():
        #    if (sliver.instance_id && sliver.instance_name):

        slice = SlicePlus.objects.get(id=sliceid)


        return HttpResponse(slice.getSliceInfo()["sshCommands"], content_type='text/text')

