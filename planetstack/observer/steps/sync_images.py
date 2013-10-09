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
        images = Image.objects.all()
        image_names = [image.name for image in images]
       
        new_images = []
        glance_images = self.driver.shell.glance.get_images()
        for glance_image in glance_images:
            if glance_image['name'] not in image_names:
                image = Image(image_id=glance_image['id'],
                              name=glance_image['name'],
                              disk_format=glance_image['disk_format'],
                              container_format=glance_image['container_format'])
                new_images.append(image)   
 
        return new_images

    def sync_record(self, image):
        image.save()
