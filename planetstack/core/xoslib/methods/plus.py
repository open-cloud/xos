from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

""" PlusSerializerMixin

    Implements Serializer fields that are common to all OpenCloud objects. For
    example, stuff related to backend fields.
"""

class PlusSerializerMixin():
    backendIcon = serializers.SerializerMethodField("getBackendIcon")
    backendHtml = serializers.SerializerMethodField("getBackendHtml")

    # This will cause a descendant class to pull in the methods defined
    # above. See rest_framework/serializers.py: _get_declared_fields().
    base_fields = {"backendIcon": backendIcon, "backendHtml": backendHtml}
    # Rest_framework 3.0 uses _declared_fields instead of base_fields
    _declared_fields = {"backendIcon": backendIcon, "backendHtml": backendHtml}

    def getBackendIcon(self, obj):
        return obj.getBackendIcon()

    def getBackendHtml(self, obj):
        return obj.getBackendHtml()

# XXX this was lifted and hacked up a bit from genapi.py
class PlusListCreateAPIView(generics.ListCreateAPIView):
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
            return super(PlusListCreateAPIView, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super(PlusListCreateAPIView, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret

# XXX this is taken from genapi.py
# XXX find a better way to re-use the code
class PlusRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

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

