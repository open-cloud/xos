from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied as RestFrameworkPermissionDenied
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from xos.exceptions import *

class XOSRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

    # To handle fine-grained field permissions, we have to check can_update
    # the object has been updated but before it has been saved.

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        self.object = self.get_object()

        if self.object is None:
            raise XOSProgrammingError("Use the List API for creating objects")

        serializer = self.get_serializer(self.object, data=request.data, partial=partial)

        if not serializer.is_valid():
            raise XOSValidationError(fields=serializer._errors)

        # Do the XOS perm check

        assert(serializer.instance is not None)
        obj = serializer.instance
        for attr, value in serializer.validated_data.items():
            setattr(obj, attr, value)
        obj.caller = request.user
        if not obj.can_update(request.user):
            raise XOSPermissionDenied()

        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            self.perform_destroy(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        # REST API drops the string attached to Django's PermissionDenied
        # exception, and replaces it with a generic "Permission Denied"
        if isinstance(exc, DjangoPermissionDenied):
            response=Response({'detail': {"error": "PermissionDenied", "specific_error": str(exc), "fields": {}}}, status=status.HTTP_403_FORBIDDEN)
            response.exception=True
            return response
        else:
            return super(XOSRetrieveUpdateDestroyAPIView, self).handle_exception(exc)

class XOSListCreateAPIView(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # In rest_framework 3.x: we can pass raise_exception=True instead of
        # raising the exception ourselves
        if not serializer.is_valid():
            raise XOSValidationError(fields=serializer._errors)

        # now do XOS can_update permission checking
        obj = serializer.Meta.model(**serializer.validated_data)
        obj.caller = request.user
        if not obj.can_update(request.user):
            raise XOSPermissionDenied()

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def handle_exception(self, exc):
        # REST API drops the string attached to Django's PermissionDenied
        # exception, and replaces it with a generic "Permission Denied"
        if isinstance(exc, DjangoPermissionDenied):
            response=Response({'detail': {"error": "PermissionDenied", "specific_error": str(exc), "fields": {}}}, status=status.HTTP_403_FORBIDDEN)
            response.exception=True
            return response
        else:
            return super(XOSListCreateAPIView, self).handle_exception(exc)

