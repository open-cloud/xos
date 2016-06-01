import os
import base64
import string
import sys
import urllib2
import urlparse
import xmlrpclib

from xos.config import Config
from core.models import Service, ServiceController, ServiceControllerResource
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class XOSBuilder(object):
    UI_KINDS=["models", "admin", "django_library", "rest", "tosca_custom_types", "tosca_resource"]
    SYNC_KINDS=["synchronizer"]

    def __init__(self):
        self.source_ui_image = "xosproject/xos"
        self.source_sync_image = "xosproject/xos-synchronizer-openstack"
        self.build_dir = "/opt/xos/BUILD/"

    # stuff that has to do with downloading

    def get_dest_dir(self, scr):
        xos_base = "opt/xos"
        service_name = scr.service_controller.name
        base_dirs = {"models": "%s/services/%s/" % (xos_base, service_name),
                     "admin": "%s/services/%s/" % (xos_base, service_name),
                     "django_library": "%s/services/%s/" % (xos_base, service_name),
                     "synchronizer": "%s/synchronizers/%s/" % (xos_base, service_name),
                     "tosca_custom_types": "%s/tosca/custom_types/" % (xos_base),
                     "tosca_resource": "%s/tosca/resources/" % (xos_base)}
        return base_dirs[scr.kind]

    def get_build_fn(self, scr):
        dest_dir = self.get_dest_dir(scr)
        dest_fn = os.path.split(urlparse.urlsplit(scr.full_url).path)[-1]
        return os.path.join(dest_dir, dest_fn)

    def get_download_fn(self, scr):
        dest_fn = self.get_build_fn(scr)
        return os.path.join(self.build_dir, dest_fn)

    def read_manifest(self, scr, fn):
        manifest = []
        manifest_lines = file(fn).readlines()
        manifest_lines = [x.strip() for x in manifest_lines]
        manifest_lines = [x for x in manifest.lines if x]
        for line in manifest_lines:
            url_parts = urlsplit(scr.full_url)
            url_parts.path = os.path.join(os.path.join(*os.path.split(url_parts).path[:-1]),line)
            url = urlparse.urlunsplit(url_parts)

            build_fn = os.path.join(self.get_dest_dir(scr), line)

            manifest.append( (url, download_fn, build_fn) )
        return manifest

    def download_file(self, url, dest_fn):
        logger.info("Download %s to %s" % (url, dest_fn))
        if not os.path.exists(os.path.dirname(dest_fn)):
            os.makedirs(os.path.dirname(dest_fn))
        obj = urllib2.urlopen(url)
        file(dest_fn,"w").write(obj.read())

    def download_resource(self, scr):
        if scr.format == "manifest":
            manifest_fn = self.get_download_fn(scr)
            self.download_file(scr.full_url, manifest_fn)
            mainfest = self.read_manifest(scr, manifest_fn)
            for (url, download_fn, build_fn) in manifest:
                self.download_file(url, download_fn)
        else:
            self.download_file(scr.full_url, self.get_download_fn(scr))

    def get_docker_lines(self, scr):
        if scr.format == "manifest":
            manifest_fn = self.get_download_fn(scr)
            manifest = self.read_manifest(scr, manifest_fn)
            lines = []
            for (url, download_fn, build_fn) in manifest:
               lines.append("ADD %s /%s" % (build_fn, build_fn))
            return lines
        else:
            build_fn = self.get_build_fn(scr)
            return ["ADD %s /%s" % (build_fn, build_fn)]

    def get_controller_docker_lines(self, controller, kinds):
        dockerfile=[]
        for scr in controller.service_controller_resources.all():
            if scr.kind in kinds:
                lines = self.get_docker_lines(scr)
                dockerfile = dockerfile + lines
        return dockerfile

    # stuff that has to do with building

    def create_ui_dockerfile(self):
        dockerfile_fn = "Dockerfile.UI"

        dockerfile = ["FROM %s" % self.source_ui_image]
        for controller in ServiceController.objects.all():
            dockerfile = dockerfile + self.get_controller_docker_lines(controller, self.UI_KINDS)

        file(os.path.join(self.build_dir, dockerfile_fn), "w").write("\n".join(dockerfile)+"\n")

        return [dockerfile_fn]

    def create_synchronizer_dockerfile(self, controller):
        lines = self.get_controller_docker_lines(controller, self.SYNC_KINDS)
        if not lines:
            return []

        dockerfile_fn = "Dockerfile.%s" % controller.name
        dockerfile = ["FROM %s" % self.source_sync_image]
        dockerfile = dockerfile + lines
        file(os.path.join(self.build_dir, dockerfile_fn), "w").writelines(dockerfile)

        return [dockerfile_fn]

    def run_docker(self, dockerfile_fn):
        pass

    def build_xos(self):
        dockerfiles=[]
        dockerfiles = dockerfiles + self.create_ui_dockerfile()

        for controller in ServiceController.objects.all():
            dockerfiles = dockerfiles + self.create_synchronizer_dockerfile(controller)

        for dockerfile in dockerfiles:
            self.run_docker(dockerfile)



