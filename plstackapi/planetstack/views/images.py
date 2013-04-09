from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.images import add_image, delete_image, get_images
from plstackapi.planetstack.serializers import ImageSerializer
from plstackapi.util.request import parse_request


class ImageListCreate(APIView):
    """ 
    List all images or create a new image.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'image' in data:
            """Not Implemented"""
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            images = get_images(data['auth'])
            serializer = ImageSerializer(images, many=True)
            return Response(serializer.data)
        
            
class ImageRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete an image  
    """

    def post(self, request, pk, format=None):
        """Retrieve an image """
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        images = get_images(data['auth'], {'name': pk})
        if not images:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ImageSerializer(images[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update image not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

    def delete(self, request, pk, format=None):
        """delete image not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

            
            
        
