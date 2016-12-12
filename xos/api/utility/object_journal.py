import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from rest_framework import filters
from rest_framework import pagination
from core.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.db import models

class JournalEntrySerializer(PlusModelSerializer):
    id = serializers.CharField(read_only=True)
    objClassName = serializers.CharField()
    objId = serializers.CharField()
    objUnicode = serializers.CharField()
    operation = serializers.CharField()
    msg = serializers.CharField()
    timestamp = serializers.DateTimeField()

    class Meta:
        model = JournalEntry
        fields = ('id', 'objClassName', 'objId', 'objUnicode', 'operation', 'msg', 'timestamp')

# Note: Supports order and limit
#           /api/utility/object_journal/?ordering=-timestamp&limit=100

class ObjectJournalViewSet(XOSViewSet):
    base_name = "object_journal"
    method_name = "object_journal"
    method_kind = "viewset"
    serializer_class = JournalEntrySerializer
    queryset = JournalEntry.objects.all()
    ordering_filter = filters.OrderingFilter()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'objClassName', 'objId', 'objUnicode', 'operation', 'timestamp')
    pagination_class = pagination.LimitOffsetPagination

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ObjectJournalViewSet, self).get_urlpatterns(api_path=api_path)

        #patterns.append( self.list_url("html/$", {"get": "get_oj_html"}, "oj_html") )

        return patterns

    def filter_queryset(self, queryset):
        queryset = super(ObjectJournalViewSet, self).filter_queryset(queryset)
        return self.ordering_filter.filter_queryset(self.request, queryset, self)

    def list(self, request):
        if hasattr(self.request,"query_params"):
            format = self.request.query_params.get('output_format', "json")
            limit = int(self.request.query_params.get('limit', 1000000))
        else:
            format = "json"
            limit = 1000000

        if format=="json":
            return super(ObjectJournalViewSet, self).list(request)

        if format=="html":
            lines=[]
            for obj in self.filter_queryset(self.get_queryset()).all():
                lines.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></TR>" % (obj.id, obj.objClassName, obj.objId, obj.objUnicode, obj.operation, obj.msg or ""))
            lines = lines[:limit]
            return HttpResponse("<html><head></head><body><table>%s</table></body></html>" % "\n".join(lines), content_type="text/html")

        if format=="ascii":
            lines=[]
            for obj in self.filter_queryset(self.get_queryset()).all():
                lines.append("%-10s %-24s %-10s %-32s %-48s %s" % (obj.id, obj.objClassName, obj.objId, str(obj.objUnicode)[:32], obj.operation, obj.msg or ""))
            lines = lines[:limit]
            return HttpResponse("\n".join(lines), content_type="text/ascii")

        return HttpResponse("unknown format")





