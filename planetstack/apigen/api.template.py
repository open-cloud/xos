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
        url(r'^xos/$', api_root),
    {% for object in generator.all %}
        url(r'xos/{{ object.rest_name }}/$', {{ object.camel }}List.as_view(), name='{{ object.singular }}-list'),
        url(r'xos/{{ object.rest_name }}/(?P<pk>[a-zA-Z0-9\-]+)/$', {{ object.camel }}Detail.as_view(), name ='{{ object.singular }}-detail'),
    {% endfor %}
    )

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        {% for object in generator.all %}'{{ object.plural }}': reverse('{{ object }}-list', request=request, format=format),
        {% endfor %}
    })

# Based on serializers.py

class XOSModelSerializer(serializers.ModelSerializer):
    def save_object(self, obj, **kwargs):

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

{% for object in generator.all %}

class {{ object.camel }}Serializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    {% for ref in object.refs %}
    {% if ref.multi %}
    {{ ref.plural }} = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='{{ ref }}-detail')
    {% else %}
    {{ ref }} = serializers.HyperlinkedRelatedField(read_only=True, view_name='{{ ref }}-detail')
    {% endif %}
    {% endfor %}
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
        model = {{ object.camel }}
        fields = ('humanReadableName', 'validators', {% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})

class {{ object.camel }}IdSerializer(XOSModelSerializer):
    id = IdField()
    {% for ref in object.refs %}
    {% if ref.multi %}
    {{ ref.plural }} = serializers.PrimaryKeyRelatedField(many=True,  queryset = {{ ref.camel }}.objects.all())
    {% else %}
    {{ ref }} = serializers.PrimaryKeyRelatedField( queryset = {{ ref.camel }}.objects.all())
    {% endif %}
    {% endfor %}
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
        model = {{ object.camel }}
        fields = ('humanReadableName', 'validators', {% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})


{% endfor %}

serializerLookUp = { 
{% for object in generator.all %}
                 {{ object.camel }}: {{ object.camel }}Serializer,
{% endfor %}
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
            raise Exception("Use the List API for creating objects")

        self.object = serializer.save(force_update=True)
        self.post_save(self.object, created=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(PlanetStackRetrieveUpdateDestroyAPIView, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        # REST API drops the string attached to Django's PermissionDenied
        # exception, and replaces it with a generic "Permission Denied"
        if isinstance(exc, DjangoPermissionDenied):
            response=Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
            response.exception=True
            return response
        else:
            return super(PlanetStackRetrieveUpdateDestroyAPIView, self).handle_exception(exc)

class PlanetStackListCreateAPIView(generics.ListCreateAPIView):
    def handle_exception(self, exc):
        # REST API drops the string attached to Django's PermissionDenied
        # exception, and replaces it with a generic "Permission Denied"
        if isinstance(exc, DjangoPermissionDenied):
            response=Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
            response.exception=True
            return response
        else:
            return super(PlanetStackListCreateAPIView, self).handle_exception(exc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if not (serializer.is_valid()):
            response = {"error": "validation",
                        "specific_error": "not serializer.is_valid()",
                        "reasons": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # now do XOS can_update permission checking

        obj = serializer.object
        obj.caller = request.user
        if not obj.can_update(request.user):
            response = {"error": "validation",
                        "specific_error": "failed can_update",
                        "reasons": []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # stuff below is from generics.ListCreateAPIView

        if (hasattr(self, "pre_save")):
            # rest_framework 2.x
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
        else:
            # rest_framework 3.x
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

# Based on core/views/*.py
{% for object in generator.all %}

class {{ object.camel }}List(PlanetStackListCreateAPIView):
    queryset = {{ object.camel }}.objects.select_related().all()
    serializer_class = {{ object.camel }}Serializer
    id_serializer_class = {{ object.camel }}IdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ({% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})

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
        return {{ object.camel }}.select_by_user(self.request.user)


class {{ object.camel }}Detail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = {{ object.camel }}.objects.select_related().all()
    serializer_class = {{ object.camel }}Serializer
    id_serializer_class = {{ object.camel }}IdSerializer

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
        return {{ object.camel }}.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

{% endfor %}
