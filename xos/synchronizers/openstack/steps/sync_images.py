import os
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from core.models.image import Image
from xos.logger import observer_logger as logger

class SyncImages(OpenStackSyncStep):
    provides=[Image]
    requested_interval=0
    observes=Image

    def fetch_pending(self, deleted):
        # Images come from the back end
        # You can't delete them
        if (deleted):
            logger.info("SyncImages: returning because deleted=True")
            return []

        # get list of images on disk
        images_path = Config().observer_images_directory

        logger.info("SyncImages: deleted=False, images_path=%s" % images_path)

        available_images = {}
        if os.path.exists(images_path):
            for f in os.listdir(images_path):
                filename = os.path.join(images_path, f)
                if os.path.isfile(filename) and filename.endswith(".img"):
                    available_images[f] = filename

        logger.info("SyncImages: available_images = %s" % str(available_images))

        images = Image.objects.all()
        image_names = [image.name for image in images]

        for image_name in available_images:
            #remove file extension
            clean_name = ".".join(image_name.split('.')[:-1])
            if clean_name not in image_names:
                logger.info("SyncImages: adding %s" % clean_name)
                image = Image(name=clean_name,
                              disk_format='raw',
                              container_format='bare', 
                              path = available_images[image_name])
                image.save()

        return Image.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None)) 

    def sync_record(self, image):
        image.save()
