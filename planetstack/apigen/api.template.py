from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from rest_framework import filters
from django.conf.urls import patterns, url

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
        url(r'^plstackapi/$', api_root),
    {% for object in generator.all %}
        url(r'plstackapi/{{ object.rest_name }}/$', {{ object.camel }}List.as_view(), name='{{ object.singular }}-list'),
        url(r'plstackapi/{{ object.rest_name }}/(?P<pk>[a-zA-Z0-9\-]+)/$', {{ object.camel }}Detail.as_view(), name ='{{ object.singular }}-detail'),
    {% endfor %}
    )

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        {% for object in generator.all %}'{{ object.plural }}': reverse('{{ object }}-list', request=request, format=format),
        {% endfor %}
    })

# Based on serializers.py

{% for object in generator.all %}

class {{ object.camel }}Serializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    {% for ref in object.refs %}
    {% if ref.multi %}
    {{ ref.plural }} = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='{{ ref }}-detail')
    {% else %}
    {{ ref }} = serializers.HyperlinkedRelatedField(read_only=True, view_name='{{ ref }}-detail')
    {% endif %}
    {% endfor %}
    class Meta:
        model = {{ object.camel }}
        fields = ({% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})

class {{ object.camel }}IdSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    {% for ref in object.refs %}
    {% if ref.multi %}
    {{ ref.plural }} = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='{{ ref }}-detail')
    {% else %}
    {{ ref }} = serializers.HyperlinkedRelatedField(read_only=True, view_name='{{ ref }}-detail')
    {% endif %}
    {% endfor %}
    class Meta:
        model = {{ object.camel }}
        fields = ({% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})


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
            print "UpdateModelMixin: not serializer.is_valid"
            print serializer.errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.pre_save(serializer.object)
        except ValidationError as err:
            # full_clean on model instance may be called in pre_save,
            # so we have to handle eventual errors.
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)

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


# Based on core/views/*.py
{% for object in generator.all %}

class {{ object.camel }}List(generics.ListCreateAPIView):
    queryset = {{ object.camel }}.objects.select_related().all()
    serializer_class = {{ object.camel }}Serializer
    id_serializer_class = {{ object.camel }}IdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ({% for prop in object.props %}'{{ prop }}',{% endfor %}{% for ref in object.refs %}{%if ref.multi %}'{{ ref.plural }}'{% else %}'{{ ref }}'{% endif %},{% endfor %})

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return {{ object.camel }}.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        obj = {{ object.camel }}(**request.DATA)
        obj.caller = request.user
        if obj.can_update(request.user):
            return super({{ object.camel }}List, self).create(request, *args, **kwargs)
        else:
            raise Exception("failed obj.can_update")

        ret = super({{ object.camel }}List, self).create(request, *args, **kwargs)
        if (ret.status_code%100 != 200):
            raise Exception(ret.data)

        return ret


class {{ object.camel }}Detail(PlanetStackRetrieveUpdateDestroyAPIView):
    queryset = {{ object.camel }}.objects.select_related().all()
    serializer_class = {{ object.camel }}Serializer
    id_serializer_class = {{ object.camel }}IdSerializer

    def get_serializer_class(self):
        no_hyperlinks = self.request.QUERY_PARAMS.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return {{ object.camel }}.select_by_user(self.request.user)

    # update() is handled by PlanetStackRetrieveUpdateDestroyAPIView

    # destroy() is handled by PlanetStackRetrieveUpdateDestroyAPIView

{% endfor %}
