import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models.image import Image
from awslib import *

class SyncImages(OpenStackSyncStep):
    provides=[Image]
    requested_interval=3600

    def fetch_pending(self):
        images = Image.objects.all()
        image_names = [image.name for image in images]
       
        new_images = []

		aws_images = aws_run('ec2 describe-images')

        for aws_image in aws_images:
            if aws_image not in image_names:
                image = Image(image_id=image_id,
                              name=aws_image['name'],
                              disk_format='XXX'
                              container_format='XXX'
                new_images.append(image)   
 
        return new_images

    def sync_record(self, image):
        image.save()
