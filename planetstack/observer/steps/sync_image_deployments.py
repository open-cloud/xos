import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import Deployment
from core.models import Image, ImageDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncImageDeployments(OpenStackSyncStep):
    provides=[ImageDeployments]
    requested_interval=0

    def fetch_pending(self):
         # smbaker: commented out automatic creation of ImageDeployments as
         #    as they will now be configured in GUI. Not sure if this is
         #    sufficient.

#        # ensure images are available across all deployments
#        image_deployments = ImageDeployments.objects.all()
#        image_deploy_lookup = defaultdict(list)
#        for image_deployment in image_deployments:
#            image_deploy_lookup[image_deployment.image].append(image_deployment.deployment)
#
#        all_deployments = Deployment.objects.all()
#        for image in Image.objects.all():
#            expected_deployments = all_deployments
#            for expected_deployment in expected_deployments:
#                if image not in image_deploy_lookup or \
#                  expected_deployment not in image_deploy_lookup[image]:
#                    id = ImageDeployments(image=image, deployment=expected_deployment)
#                    id.save()

        # now we return all images that need to be enacted
        return ImageDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, image_deployment):
        logger.info("Working on image %s on deployment %s" % (image_deployment.image.name, image_deployment.deployment.name))
        driver = self.driver.admin_driver(deployment=image_deployment.deployment.name)
        images = driver.shell.glance.get_images()
        glance_image = None
        for image in images:
            if image['name'] == image_deployment.image.name:
                glance_image = image
                break
        if glance_image:
            logger.info("Found image %s on deployment %s" % (image_deployment.image.name, image_deployment.deployment.name))
            image_deployment.glance_image_id = glance_image['id']
        elif image_deployment.image.path:
            image = {
                'name': image_deployment.image.name,
                'is_public': True,
                'disk_format': 'raw',
                'container_format': 'bare',
                'file': image_deployment.image.path,
            }

            logger.info("Creating image %s on deployment %s" % (image_deployment.image.name, image_deployment.deployment.name))

            glance_image = driver.shell.glanceclient.images.create(name=image_deployment.image.name,
                                                                   is_public=True,
                                                                   disk_format='raw',
                                                                   container_format='bare')
            glance_image.update(data=open(image_deployment.image.path, 'rb'))

            # While the images returned by driver.shell.glance.get_images()
            #   are dicts, the images returned by driver.shell.glanceclient.images.create
            #   are not dicts. We have to use getattr() instead of [] operator.
            if not glance_image or not getattr(glance_image,"id",None):
                raise Exception, "Add image failed at deployment %s" % image_deployment.deployment.name
            image_deployment.glance_image_id = getattr(glance_image, "id")
        image_deployment.save()
