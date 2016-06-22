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
    UI_KINDS=["models", "admin", "admin_template", "django_library", "rest_service", "rest_tenant", "tosca_custom_types", "tosca_resource","public_key"]
    SYNC_CONTROLLER_KINDS=["synchronizer", "private_key", "public_key"]
    SYNC_ALLCONTROLLER_KINDS=["models", "django_library"]

    def __init__(self):
        self.source_sync_image = "xosproject/xos-synchronizer-openstack"
        self.build_dir = "/opt/xos/BUILD/"

    # stuff that has to do with downloading

    def get_dest_dir(self, scr):
        xos_base = "opt/xos"
        service_name = scr.service_controller.name
        base_dirs = {"models": "%s/services/%s/" % (xos_base, service_name),
                     "admin": "%s/services/%s/" % (xos_base, service_name),
                     "admin_template": "%s/services/%s/templates/" % (xos_base, service_name),
                     "django_library": "%s/services/%s/" % (xos_base, service_name),
                     "synchronizer": "%s/synchronizers/%s/" % (xos_base, service_name),
                     "tosca_custom_types": "%s/tosca/custom_types/" % (xos_base),
                     "tosca_resource": "%s/tosca/resources/" % (xos_base),
                     "rest_service": "%s/api/service/" % (xos_base),
                     "rest_tenant": "%s/api/tenant/" % (xos_base),
                     "private_key": "%s/services/%s/keys/" % (xos_base, service_name),
                     "public_key": "%s/services/%s/keys/" % (xos_base, service_name)}
        dest_dir = base_dirs[scr.kind]

        if scr.subdirectory:
            dest_dir = os.path.join(dest_dir, scr.subdirectory)

        return dest_dir

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

# XXX docker creates a new container and commits it for every single COPY
# line in the dockerfile. This causes services with many files (for example,
# vsg) to take ~ 10-15 minutes to build the docker file. So instead we'll copy
# the whole build directory, and then run a script that copies the files
# we want.

#    def get_docker_lines(self, scr):
#        if scr.format == "manifest":
#            manifest_fn = self.get_download_fn(scr)
#            manifest = self.read_manifest(scr, manifest_fn)
#            lines = []
#            for (url, download_fn, build_fn) in manifest:
#               script.append("mkdir -p
#               #lines.append("COPY %s /%s" % (build_fn, build_fn))
#            return lines
#        else:
#            build_fn = self.get_build_fn(scr)
#            #return ["COPY %s /%s" % (build_fn, build_fn)]

#    def get_controller_docker_lines(self, controller, kinds):
#        need_service_init_py = False
#        dockerfile=[]
#        for scr in controller.service_controller_resources.all():
#            if scr.kind in kinds:
#                lines = self.get_docker_lines(scr)
#                dockerfile = dockerfile + lines
#            if scr.kind in ["admin", "models"]:
#                need_service_init_py = True
#
#        if need_service_init_py:
#            file(os.path.join(self.build_dir, "opt/xos/empty__init__.py"),"w").write("")
#            dockerfile.append("COPY opt/xos/empty__init__.py /opt/xos/services/%s/__init__.py" % controller.name)
#
#        return dockerfile

    def get_script_lines(self, scr):
        if scr.format == "manifest":
            manifest_fn = self.get_download_fn(scr)
            manifest = self.read_manifest(scr, manifest_fn)
            lines = []
            for (url, download_fn, build_fn) in manifest:
               lines.append("mkdir -p /%s" % os.path.dirname(build_fn))
               lines.append("cp /build/%s /%s" % (build_fn, build_fn))
            return lines
        else:
            build_fn = self.get_build_fn(scr)
            return ["mkdir -p /%s" % os.path.dirname(build_fn),
                    "cp /build/%s /%s" % (build_fn, build_fn)]

    def get_controller_script_lines(self, controller, kinds):
        need_service_init_py = False
        script=[]
        for scr in controller.service_controller_resources.all():
            if scr.kind in kinds:
                lines = self.get_script_lines(scr)
                script = script + lines
            if scr.kind in ["admin", "models"]:
                need_service_init_py = True

        if need_service_init_py:
            script.append("echo > /opt/xos/services/%s/__init__.py" % controller.name)

        return script

    def check_controller_unready(self, controller):
        unready_resources=[]
        for scr in controller.service_controller_resources.all():
            if (not scr.backend_status) or (not scr.backend_status.startswith("1")):
                unready_resources.append(scr)

        return unready_resources

    # stuff that has to do with building

    def create_xos_app_data(self, name, script, app_list, migration_list):
        if not os.path.exists(os.path.join(self.build_dir,"opt/xos/xos")):
            os.makedirs(os.path.join(self.build_dir,"opt/xos/xos"))

        if app_list:
            script.append("mkdir -p /opt/xos/xos")
            script.append("cp /build/opt/xos/xos/%s_xosbuilder_app_list /opt/xos/xos/xosbuilder_app_list" % name)
            #dockerfile.append("COPY opt/xos/xos/%s_xosbuilder_app_list /opt/xos/xos/xosbuilder_app_list" % name)
            file(os.path.join(self.build_dir, "opt/xos/xos/%s_xosbuilder_app_list") % name, "w").write("\n".join(app_list)+"\n")

        if migration_list:
            script.append("mkdir -p /opt/xos/xos")
            script.append("cp /build/opt/xos/xos/%s_xosbuilder_migration_list /opt/xos/xos/xosbuilder_migration_list" % name)
            #dockerfile.append("COPY opt/xos/xos/%s_xosbuilder_migration_list /opt/xos/xos/xosbuilder_migration_list" % name)
            file(os.path.join(self.build_dir, "opt/xos/xos/%s_xosbuilder_migration_list") % name, "w").write("\n".join(migration_list)+"\n")

    def create_ui_dockerfile(self):
        xos = XOS.objects.all()[0]
        dockerfile_fn = "Dockerfile.UI"

        app_list = []
        migration_list = []

        dockerfile = ["FROM %s" % xos.source_ui_image]
        script = []
        for controller in ServiceController.objects.all():
            if self.check_controller_unready(controller):
                 logger.warning("Controller %s has unready resources" % str(controller))
                 continue

            #dockerfile = dockerfile + self.get_controller_docker_lines(controller, self.UI_KINDS)
            script = script + self.get_controller_script_lines(controller, self.UI_KINDS)
            if controller.service_controller_resources.filter(kind="models").exists():
                app_list.append("services." + controller.name)
                migration_list.append(controller.name)

        self.create_xos_app_data("ui", script, app_list, migration_list)

        file(os.path.join(self.build_dir, "install-xos.sh"), "w").write("\n".join(script)+"\n")
        dockerfile.append("COPY . /build/")
        dockerfile.append("RUN bash /build/install-xos.sh")

        file(os.path.join(self.build_dir, dockerfile_fn), "w").write("\n".join(dockerfile)+"\n")

        return {"dockerfile_fn": dockerfile_fn,
                "docker_image_name": "xosproject/xos-ui"}

    def create_synchronizer_dockerfile(self, controller):
        # bake in the synchronizer from this controller
        sync_lines = self.get_controller_script_lines(controller, self.SYNC_CONTROLLER_KINDS)
        if not sync_lines:
            return []

        dockerfile_fn = "Dockerfile.%s" % controller.name
        dockerfile = ["FROM %s" % self.source_sync_image]
        script = []

        # Now bake in models from this controller as well as the others
        # It's important to bake all services in, because some services'
        # synchronizers may depend on models from another service.
        app_list = []
        for c in ServiceController.objects.all():
            #dockerfile = dockerfile + self.get_controller_docker_lines(c, self.SYNC_ALLCONTROLLER_KINDS)
            script = script + self.get_controller_script_lines(c, self.SYNC_ALLCONTROLLER_KINDS)
            if controller.service_controller_resources.filter(kind="models").exists():
                app_list.append("services." + c.name)

        self.create_xos_app_data(controller.name, script, app_list, None)

        script = script + sync_lines

        file(os.path.join(self.build_dir, "install-%s.sh" % controller.name), "w").write("\n".join(script)+"\n")
        dockerfile.append("COPY . /build/")
        dockerfile.append("RUN bash /build/install-%s.sh" % controller.name)

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

#         containers["xos_db"] = \
#                            {"image": "xosproject/xos-postgres",
#                             "expose": [5432]}

         containers["xos_ui"] = \
                            {"image": "xosproject/xos-ui",
                             "command": "python /opt/xos/manage.py runserver 0.0.0.0:%d --insecure --makemigrations" % xos.ui_port,
                             "ports": {"%d"%xos.ui_port : "%d"%xos.ui_port},
                             #"links": ["xos_db"],
                             "external_links": ["%s:%s" % (xos.db_container_name, "xos_db")],
                             "volumes": volume_list}

#         containers["xos_bootstrap_ui"] = {"image": "xosproject/xos",
#                             "command": "python /opt/xos/manage.py runserver 0.0.0.0:%d --insecure --makemigrations" % xos.bootstrap_ui_port,
#                             "ports": {"%d"%xos.bootstrap_ui_port : "%d"%xos.bootstrap_ui_port},
#                             #"external_links": ["%s:%s" % (xos.db_container_name, "xos_db")],
#                             "links": ["xos_db"],
#                             "volumes": volume_list}

         if not xos.frontend_only:
             for c in ServiceController.objects.all():
                 if self.check_controller_unready(c):
                     logger.warning("Controller %s has unready resources" % str(c))
                     continue

                 if c.service_controller_resources.filter(kind="synchronizer").exists():
                     if c.synchronizer_run and c.synchronizer_config:
                         command = 'bash -c "sleep 120; cd /opt/xos/synchronizers/%s; python ./%s -C %s"' % (c.name, c.synchronizer_run, c.synchronizer_config)
                     else:
                         command = 'bash -c "sleep 120; cd /opt/xos/synchronizers/%s; bash ./run.sh"' % c.name

                     containers["xos_synchronizer_%s" % c.name] = \
                                    {"image": "xosproject/xos-synchronizer-%s" % c.name,
                                     "command": command,
                                     "external_links": ["%s:%s" % (xos.db_container_name, "xos_db")],
                                     #"links": ["xos_db"],
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



