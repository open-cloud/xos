import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import Controller
from core.models import Image, ControllerImages
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncControllerImages(OpenStackSyncStep):
    provides=[ControllerImages]
    requested_interval=0

    def fetch_pending(self, deleted):
        if (deleted):
            return []
         # smbaker: commented out automatic creation of ControllerImages as
         #    as they will now be configured in GUI. Not sure if this is
         #    sufficient.

#        # ensure images are available across all controllers
#        controller_images = ControllerImages.objects.all()
#        image_deploy_lookup = defaultdict(list)
#        for controller_image in controller_images:
#            image_deploy_lookup[controller_image.image].append(controller_image.controller)
#
#        all_controllers = Controller.objects.all()
#        for image in Image.objects.all():
#            expected_controllers = all_controllers
#            for expected_controller in expected_controllers:
#                if image not in image_deploy_lookup or \
#                  expected_controller not in image_deploy_lookup[image]:
#                    id = ControllerImages(image=image, controller=expected_controller)
#                    id.save()

        # now we return all images that need to be enacted
        return ControllerImages.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, controller_image):
        logger.info("Working on image %s on controller %s" % (controller_image.image.name, controller_image.controller))
        driver = self.driver.admin_driver(controller=controller_image.controller.name)
        images = driver.shell.glance.get_images()
        glance_image = None
        for image in images:
            if image['name'] == controller_image.image.name:
                glance_image = image
                break
        if glance_image:
            logger.info("Found image %s on controller %s" % (controller_image.image.name, controller_image.controller.name))
            controller_image.glance_image_id = glance_image['id']
        elif controller_image.image.path:
            image = {
                'name': controller_image.image.name,
                'is_public': True,
                'disk_format': 'raw',
                'container_format': 'bare',
                'file': controller_image.image.path,
            }

            logger.info("Creating image %s on controller %s" % (controller_image.image.name, controller_image.controller.name))

            glance_image = driver.shell.glanceclient.images.create(name=controller_image.image.name,
                                                                   is_public=True,
                                                                   disk_format='raw',
                                                                   container_format='bare')
            glance_image.update(data=open(controller_image.image.path, 'rb'))

            # While the images returned by driver.shell.glance.get_images()
            #   are dicts, the images returned by driver.shell.glanceclient.images.create
            #   are not dicts. We have to use getattr() instead of [] operator.
            if not glance_image or not getattr(glance_image,"id",None):
                raise Exception, "Add image failed at controller %s" % controller_image.controller.name
            controller_image.glance_image_id = getattr(glance_image, "id")
        controller_image.save()
