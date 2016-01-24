import os
import base64
from django.db.models import F, Q
from xos.config import Config, XOS_DIR
from ec2_observer.syncstep import SyncStep
from core.models.image import Image
from ec2_observer.awslib import *


class SyncImages(SyncStep):
    provides=[Image]
    requested_interval=3600

    def fetch_pending(self,deletion):
        if (deletion):
            return []

        images = Image.objects.all()
        image_names = [image.name for image in images]
       
        new_images = []

        try:
            aws_images = json.loads(open(XOS_DIR + '/aws-images').read())
        except:
            aws_images = aws_run('ec2 describe-images --owner 099720109477')
            open(XOS_DIR + '/aws-images','w').write(json.dumps(aws_images))

        

        aws_images=aws_images['Images']
        aws_images=filter(lambda x:x['ImageType']=='machine',aws_images)[:50]

        names = set([])
        for aws_image in aws_images:
            desc_ok = True

            try:
                desc = aws_image['Description']
            except:
                try:
                    desc = aws_image['ImageLocation']
                except:
                    desc_ok = False
            
            if (desc_ok):
                try:
                    desc_ok =  desc and desc not in names and desc not in image_names and '14.04' in desc
                except KeyError:
                    desc_ok = False

            if desc_ok and aws_image['ImageType']=='machine':
                image = Image(disk_format=aws_image['ImageLocation'],
                                name=desc,
                                container_format=aws_image['Hypervisor'],
                                path=aws_image['ImageId'])
                new_images.append(image)
                names.add(image.name)

        #print new_images
        return new_images

    def sync_record(self, image):
        image.save()
