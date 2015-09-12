from view_common import *

class DashboardSliceInteractions(View):
    def get(self, request, name="users", **kwargs):
        colors = ["#005586", "#6ebe49", "orange", "#707170", "#00c4b3", "#077767", "dodgerblue", "#a79b94", "#c4e76a", "red"]

        groups = []
        matrix = []
        slices = list(Slice.objects.all())

        ids_by_slice = self.build_id_list(slices, name)

        slices = [x for x in slices if (len(ids_by_slice[x])>0)]

        for i,slice in enumerate(slices):
            groups.append({"name": slice.name, "color": colors[i%len(colors)]})
            row=self.buildMatrix(slice, slices, name, ids_by_slice)
            matrix.append(row)

        result = {"groups": groups, "matrix": matrix}

        if name=="users":
            result["title"] = "Slice interactions by user privilege"
            result["objectName"] = "users"
        elif name=="networks":
            result["title"] = "Slice interactions by network membership"
            result["objectName"] = "networks"
        elif name=="sites":
            result["title"] = "Slice interactions by site ownership"
            result["objectName"] = "sites"
        elif name=="instance_sites":
            result["title"] = "Slice interactions by instance sites"
            result["objectName"] = "sites"
        elif name=="instance_nodes":
            result["title"] = "Slice interactions by instance nodes"
            result["objectName"] = "nodes"

        return HttpResponse(json.dumps(result), content_type='application/javascript')

    def build_id_list(self, slices, name):
        ids_by_slice = {}
        for slice in slices:
            # build up a list of object ids that are used by each slice
            ids_by_slice[slice] = self.getIds(slice, name)

        return ids_by_slice

    def buildMatrix(self, slice, slices, name, ids_by_slice):
        not_only_my_ids = []

        # build up a list of object ids that are used by other slices
        for otherSlice in ids_by_slice.keys():
            if (slice != otherSlice):
                for id in ids_by_slice[otherSlice]:
                    if not id in not_only_my_ids:
                        not_only_my_ids.append(id)

        # build up a list of ids that are used only by the slice, and not
        # shared with any other slice
        only_my_ids = []
        for id in ids_by_slice[slice]:
             if id not in not_only_my_ids:
                  only_my_ids.append(id)

        row = []
        for otherSlice in ids_by_slice.keys():
            if (otherSlice == slice):
                row.append(len(only_my_ids))
            else:
                row.append(self.inCommonIds(ids_by_slice[slice], ids_by_slice[otherSlice]))

        return row

    def getIds(self, slice, name):
        ids=[]
        if name=="users":
            for sp in slice.slice_privileges.all():
                    if sp.user.id not in ids:
                        ids.append(sp.user.id)
        elif name=="networks":
            for sp in slice.networkslices.all():
                    if sp.network.id not in ids:
                        ids.append(sp.network.id)
        elif name=="sites":
            ids = [slice.site.id]
        elif name=="instance_sites":
            for sp in slice.instances.all():
                 if sp.node.site.id not in ids:
                     ids.append(sp.node.site.id)
        elif name=="instance_nodes":
            for sp in slice.instances.all():
                 if sp.node.id not in ids:
                     ids.append(sp.node.id)
        return ids

    def inCommonIds(self, ids1, ids2):
        count = 0
        for id in ids1:
            if id in ids2:
                count+=1
        return count


