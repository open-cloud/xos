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

        # now we return all images that need to be enacted
        return ControllerImages.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, controller_image):
        logger.info("Working on image %s on controller %s" % (controller_image.image.name, controller_image.controller))

	image_fields = {'endpoint':controller_image.controller.auth_url,
			'admin_user':controller_image.controller.admin_user,
			'admin_password':controller_image.controller.admin_password,
			'name':controller_image.image.name,
			'filepath':controller_image.image.path
			}

	res = run_template('sync_controller_images.yaml', image_fields)

	if (len(res)!=1):
	    raise Exception('Could not sync image %s'%controller_image.image.name)
	else:
	    image_id = res[0]['id'] 
            controller_image.glance_image_id = image_id
            controller_image.save()
