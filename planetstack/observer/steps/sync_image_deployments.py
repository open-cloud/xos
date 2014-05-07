import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.deployment import Deployment
from core.models.image import Image, ImageDeployments

class SyncImageDeployments(OpenStackSyncStep):
    provides=[ImageDeployments]
    requested_interval=0

    def fetch_pending(self):
        # ensure images are available across all deployments
        image_deployments = ImageDeployments.objects.all()
        image_deploy_lookup = defaultdict(list)
        for image_deployment in image_deployments:
            image_deploy_lookup[image_deployment.image].append(image_deployment.deployment)
        
        all_deployments = Deployment.objects.all() 
        for image in Image.objects.all():
            expected_deployments = all_deployments
            for expected_deployment in expected_deployments:
                if image not in image_deploy_lookup or \
                  expected_deployment not in image_deploy_lookup[image]:
                    id = ImageDeployments(image=image, deployment=expected_deployment)
                    id.save()
            
        # now we return all images that need to be enacted
        return ImageDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None)) 
                      
    def sync_record(self, image_deployment):
        driver = self.driver.admin_driver(deployment=image_deployment.deployment.name)
        image = {
            'name': image_deployment.image.name,
            'is_public': True,
            'disk_format': 'raw', 
            'container_format': 'bare',
            'file': image_deployment.image.path, 
        }  
        glance_image = driver.shell.glance.add_image(image)  
        image_deployment.glance_image_id = glance_image['id']
        image_deployment.save()
