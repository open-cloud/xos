import os
import sys

from core.models import User,Image

class XOSImageSelector(object):
    def __init__(self, user, distribution=None, type=None, architecture=None, version=None):
        self.user = user

    def get_allowed_images(self):
        # TODO: logic to get images that the user can use
        nodes = Image.objects.all()
        return nodes

    def get_image(self):
        images = self.get_allowed_images()

        # TODO: pick image based on parameters

        found_imgs=images.filter(name="Ubuntu 14.04 LTS")   # portal
        if found_imgs:
            return found_imgs[0]

        found_imgs=images.filter(name="Ubuntu-14.04-LTS")    # demo
        if found_imgs:
            return found_imgs[0]

        found_imgs=images.filter(name="trusty-server-multi-nic")    # demo
        if found_imgs:
            return found_imgs[0]

        raise Exception("Failed to find an acceptable image")

