from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from core.models import *
from django.forms import widgets

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

# Based on api_root.py

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
	{{ ref.plural }} = serializers.HyperlinkedRelatedField(view_name='{{ ref }}-detail')
	{% endfor %}
	class Meta:
		model = {{ object }}
		fields = ({% for prop in object.props %}'{{ prop }}',{% endfor %})
{% endfor %}

serializerLookUp = { 
{% for object in generator.all %}
                 {{ object.camel }}: {{ object.camel }}Serializer,
{% endfor %}
                 None: None,
                }

# Based on core/views/*.py
{% for object in generator.all %}

class {{ object.camel }}List(generics.ListCreateAPIView):
    #queryset = {{ object.camel }}.objects.all()
    serializer_class = {{ object.camel }}Serializer
    
    def get_queryset(self):
        return {{ object.camel }}.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        #obj = {{ object.camel }}().update(request.DATA)
        obj = self.get_object()
        if obj.can_update(request.user):
            return super({{ object.camel }}List, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class {{ object.camel }}Detail(generics.RetrieveUpdateDestroyAPIView):
    #queryset = {{ object.camel }}.objects.all()
    serializer_class = {{ object.camel }}Serializer
    
    def get_queryset(self):
        return {{ object.camel }}.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super({{ object.camel }}Detail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super({{ object.camel }}Detail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
     

{% endfor %}
