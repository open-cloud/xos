import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import Controller
from core.models import Image, ControllerImages
from util.logger import Logger, logging
from observer.ansible import *

logger = Logger(level=logging.INFO)

class SyncControllerImages(OpenStackSyncStep):
    provides=[ControllerImages]
    observes = ControllerImages
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
                        'filepath':controller_image.image.path,
                        'ansible_tag': '%s@%s'%(controller_image.image.name,controller_image.controller.name), # name of ansible playbook
                        }


        res = run_template('sync_controller_images.yaml', image_fields, path='controller_images', expected_num=1)

        image_id = res[0]['id']
        controller_image.glance_image_id = image_id
	controller_image.backend_status = '1 - OK'
        controller_image.save()
