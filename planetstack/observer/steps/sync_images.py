import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.image import Image

class SyncImages(OpenStackSyncStep):
    provides=[Image]
    requested_interval=0

    def fetch_pending(self):
        # get list of images on disk
        images_path = Config().observer_images_directory 
        available_images = {}
        for f in os.listdir(images_path):
            if os.path.isfile(os.path.join(images_path ,f)):
                available_images[f] = os.path.join(images_path ,f)

        images = Image.objects.all()
        image_names = [image.name for image in images]

        for image_name in available_images:
            #remove file extension
            clean_name = ".".join(image_name.split('.')[:-1])
            if clean_name not in image_names:
                image = Image(name=clean_name,
                              disk_format='raw',
                              container_format='bare', 
                              path = available_images[image_name])
                image.save()
       
        
        return Image.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None)) 

    def sync_record(self, image):
        image.save()
