import os
import base64
import jinja2
import string
import sys
import urllib2
import urlparse
import xmlrpclib

from xos.config import Config
from core.models import Service, ServiceController, ServiceControllerResource, XOS
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class XOSBuilder(object):
    UI_KINDS=["models", "admin", "django_library", "rest", "tosca_custom_types", "tosca_resource","public_key"]
    SYNC_CONTROLLER_KINDS=["synchronizer", "private_key", "public_key"]
    SYNC_ALLCONTROLLER_KINDS=["models", "django_library"]

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
                     "tosca_resource": "%s/tosca/resources/" % (xos_base),
                     "private_key": "%s/services/%s/keys" % (xos_base, service_name),
                     "public_key": "%s/services/%s/keys/" % (xos_base, service_name)}
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
        manifest_lines = [x for x in manifest_lines if x]
        for line in manifest_lines:
            url_parts = urlparse.urlsplit(scr.full_url)
            new_path = os.path.join(os.path.join(*os.path.split(url_parts.path)[:-1]),line)
            url = urlparse.urlunsplit( (url_parts.scheme, url_parts.netloc, new_path, url_parts.query, url_parts.fragment) )

            build_fn = os.path.join(self.get_dest_dir(scr), line)
            download_fn = os.path.join(self.build_dir, build_fn)

            manifest.append( (url, download_fn, build_fn) )
        return manifest

    def download_file(self, url, dest_fn):
        logger.info("Download %s to %s" % (url, dest_fn))
        if not os.path.exists(os.path.dirname(dest_fn)):
            os.makedirs(os.path.dirname(dest_fn))
        obj = urllib2.urlopen(url)
        file(dest_fn,"w").write(obj.read())

        # make python files executable
        if dest_fn.endswith(".py"): # and contents.startswith("#!"):
            os.chmod(dest_fn, 0755)

    def download_resource(self, scr):
        if scr.format == "manifest":
            manifest_fn = self.get_download_fn(scr)
            self.download_file(scr.full_url, manifest_fn)
            manifest = self.read_manifest(scr, manifest_fn)
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

    def create_xos_app_data(self, name, dockerfile, app_list, migration_list):
        if not os.path.exists(os.path.join(self.build_dir,"opt/xos/xos")):
            os.makedirs(os.path.join(self.build_dir,"opt/xos/xos"))

        if app_list:
            dockerfile.append("COPY opt/xos/xos/%s_xosbuilder_app_list /opt/xos/xos/xosbuilder_app_list" % name)
            file(os.path.join(self.build_dir, "opt/xos/xos/%s_xosbuilder_app_list") % name, "w").write("\n".join(app_list)+"\n")

        if migration_list:
            dockerfile.append("COPY opt/xos/xos/%s_xosbuilder_migration_list /opt/xos/xos/xosbuilder_migration_list" % name)
            file(os.path.join(self.build_dir, "opt/xos/xos/%s_xosbuilder_migration_list") % name, "w").write("\n".join(migration_list)+"\n")

    def create_ui_dockerfile(self):
        dockerfile_fn = "Dockerfile.UI"

        app_list = []
        migration_list = []

        dockerfile = ["FROM %s" % self.source_ui_image]
        for controller in ServiceController.objects.all():
            dockerfile = dockerfile + self.get_controller_docker_lines(controller, self.UI_KINDS)
            if controller.service_controller_resources.filter(kind="models").exists():
                app_list.append("services." + controller.name)
                migration_list.append(controller.name)

        self.create_xos_app_data("ui", dockerfile, app_list, migration_list)

        file(os.path.join(self.build_dir, dockerfile_fn), "w").write("\n".join(dockerfile)+"\n")

        return {"dockerfile_fn": dockerfile_fn,
                "docker_image_name": "xosproject/xos-ui"}

    def create_synchronizer_dockerfile(self, controller):
        # bake in the synchronizer from this controller
        sync_lines = self.get_controller_docker_lines(controller, self.SYNC_CONTROLLER_KINDS)
        if not sync_lines:
            return []

        dockerfile_fn = "Dockerfile.%s" % controller.name
        dockerfile = ["FROM %s" % self.source_sync_image]

        # Now bake in models from this controller as well as the others
        # It's important to bake all services in, because some services'
        # synchronizers may depend on models from another service.
        app_list = []
        for c in ServiceController.objects.all():
            dockerfile = dockerfile + self.get_controller_docker_lines(c, self.SYNC_ALLCONTROLLER_KINDS)
            if controller.service_controller_resources.filter(kind="models").exists():
                app_list.append("services." + controller.name)

        self.create_xos_app_data(controller.name, dockerfile, app_list, None)

        dockerfile = dockerfile + sync_lines
        file(os.path.join(self.build_dir, dockerfile_fn), "w").write("\n".join(dockerfile)+"\n")

        return {"dockerfile_fn": dockerfile_fn,
                "docker_image_name": "xosproject/xos-synchronizer-%s" % controller.name}

    def create_docker_compose(self):
         xos = XOS.objects.all()[0]

         volume_list = []
         for volume in xos.volumes.all():
             volume_list.append({"host_path": volume.host_path,
                                 "container_path": volume.container_path,
                                 "read_only": volume.read_only})

         containers = {}

         containers["xos_db"] = \
                            {"image": "xosproject/xos-postgres",
                             "container_base_name": xos.container_base_name,
                             "expose": [5432]}

         containers["xos_ui"] = \
                            {"image": "xosproject/xos-ui",
                             "container_base_name": xos.container_base_name,
                             "command": "python /opt/xos/manage.py runserver 0.0.0.0:%d --insecure --makemigrations" % xos.ui_port,
                             "ports": {"%d"%xos.ui_port : "%d"%xos.ui_port},
                             "links": ["xos_db"],
                             "volumes": volume_list}

         containers["xos_bootstrap_ui"] = {"image": "xosproject/xos-ui",
                             "container_base_name": xos.container_base_name,
                             "command": "python /opt/xos/manage.py runserver 0.0.0.0:%d --insecure --makemigrations" % xos.bootstrap_ui_port,
                             "ports": {"%d"%xos.bootstrap_ui_port : "%d"%xos.bootstrap_ui_port},
                             "links": ["xos_db"],
                             "volumes": volume_list}

         for c in ServiceController.objects.all():
             containers["xos_synchronizer_%s" % c.name] = \
                            {"image": "xosproject/xos-synchronizer-%s" % controller.name,
                             "container_base_name": xos.container_base_name,
                             "command": 'bash -c "sleep 120; bash /opt/xos/synchronizers/%s/run.sh"',
                             "links": ["xos_db"],
                             "volumes": volume_list}

         vars = { "containers": containers }

         template_loader = jinja2.FileSystemLoader( "/opt/xos/synchronizers/onboarding/templates/" )
         template_env = jinja2.Environment(loader=template_loader)
         template = template_env.get_template("docker-compose.yml.j2")
         buffer = template.render(vars)

         if not os.path.exists("/opt/xos/synchronizers/onboarding/docker-compose"):
             os.makedirs("/opt/xos/synchronizers/onboarding/docker-compose")
         file("/opt/xos/synchronizers/onboarding/docker-compose/docker-compose.yml", "w").write(buffer)

#    def build_xos(self):
#        dockerfiles=[]
#        dockerfiles.append(self.create_ui_dockerfile())
#
#        for controller in ServiceController.objects.all():
#            dockerfiles.append(self.create_synchronizer_dockerfile(controller))



