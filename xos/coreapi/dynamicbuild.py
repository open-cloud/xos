# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import hashlib
import os
import shutil
import tempfile
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))

DEFAULT_BASE_DIR = "/opt/xos"


class DynamicBuilder(object):
    NOTHING_TO_DO = 0
    SOMETHING_CHANGED = 1

    def __init__(self, base_dir=DEFAULT_BASE_DIR):
        self.services_dir = os.path.join(base_dir, "dynamic_services")
        self.manifest_dir = os.path.join(base_dir, "dynamic_services/manifests")
        self.services_dest_dir = os.path.join(base_dir, "services")
        self.coreapi_dir = os.path.join(base_dir, "coreapi")
        self.protos_dir = os.path.join(base_dir, "coreapi/protos")
        self.app_metadata_dir = os.path.join(base_dir, "xos")
        self.convenience_methods_dir = os.path.join(
            base_dir, "xos_client/xosapi/convenience"
        )

    def pre_validate_file(self, item):
        # someone might be trying to trick us into writing files outside the designated directory
        if "/" in item.filename:
            raise Exception("illegal character in filename %s" % item.filename)

    def pre_validate_python(self, item):
        (handle, fn) = tempfile.mkstemp()
        try:
            os.write(handle, item.contents)
            os.close(handle)
            if os.system("python -m py_compile %s" % fn) != 0:
                raise Exception("python file %s failed compile test" % item.filename)
        finally:
            os.remove(fn)

    def pre_validate_models(self, request):
        # do whatever validation we can before saving the files
        for item in request.xprotos:
            self.pre_validate_file(item)

        for item in request.decls:
            self.pre_validate_file(item)

        for item in request.attics:
            self.pre_validate_file(item)

        for item in request.convenience_methods:
            self.pre_validate_file(item)
            self.pre_validate_python(item)

    def get_manifests(self):
        if not os.path.exists(self.manifest_dir):
            return []

        manifests = []
        for fn in os.listdir(self.manifest_dir):
            if fn.endswith(".json"):
                manifest_fn = os.path.join(self.manifest_dir, fn)
                try:
                    manifest = json.loads(open(manifest_fn).read())
                    manifests.append(manifest)
                except BaseException:
                    log.exception("Error loading manifest", filename=manifest_fn)
        return manifests

    def load_manifest_from_request(self, request):
        manifest_fn = os.path.join(self.manifest_dir, request.name + ".json")
        if os.path.exists(manifest_fn):
            try:
                manifest = json.loads(open(manifest_fn).read())
            except BaseException:
                log.exception("Error loading old manifest", filename=manifest_fn)
                manifest = {}
        else:
            manifest = {}

        return (manifest, manifest_fn)

    def handle_loadmodels_request(self, request):
        (manifest, manifest_fn) = self.load_manifest_from_request(request)

        # TODO: Check version number to make sure this is not a downgrade ?

        hash = self.generate_request_hash(request, state="load")
        if hash == manifest.get("hash"):
            # The hash of the incoming request is identical to the manifest that we have saved, so this request is a
            # no-op.
            log.info(
                "Models are already up-to-date; skipping dynamic load.",
                name=request.name,
            )
            return self.NOTHING_TO_DO

        self.pre_validate_models(request)

        manifest = self.save_models(request, state="load", hash=hash)

        self.run_xosgenx_service(manifest)

        log.debug("Saving service manifest", name=request.name)
        file(manifest_fn, "w").write(json.dumps(manifest))

        log.info("Finished LoadModels request", name=request.name)

        return self.SOMETHING_CHANGED

    def handle_unloadmodels_request(self, request):
        (manifest, manifest_fn) = self.load_manifest_from_request(request)

        # TODO: Check version number to make sure this is not a downgrade ?

        hash = self.generate_request_hash(request, state="unload")
        if hash == manifest.get("hash"):
            # The hash of the incoming request is identical to the manifest that we have saved, so this request is a
            # no-op.
            log.info(
                "Models are already up-to-date; skipping dynamic unload.",
                name=request.name,
            )
            return self.NOTHING_TO_DO

        manifest = self.save_models(request, state="unload", hash=hash)

        self.remove_service(manifest)

        log.debug("Saving service manifest", name=request.name)
        file(manifest_fn, "w").write(json.dumps(manifest))

        log.info("Finished UnloadModels request", name=request.name)

        return self.SOMETHING_CHANGED

    def generate_request_hash(self, request, state):
        # TODO: could we hash the request rather than individually hashing the subcomponents of the request?
        m = hashlib.sha1()
        m.update(request.name)
        m.update(request.version)
        if state == "load":
            for item in request.xprotos:
                m.update(item.filename)
                m.update(item.contents)
            for item in request.decls:
                m.update(item.filename)
                m.update(item.contents)
            for item in request.decls:
                m.update(item.filename)
                m.update(item.contents)
        return m.hexdigest()

    def save_models(self, request, state, hash=None):
        if not hash:
            hash = self.generate_request_hash(request, state)

        service_dir = os.path.join(self.services_dir, request.name)
        if not os.path.exists(service_dir):
            os.makedirs(service_dir)

        if not os.path.exists(self.manifest_dir):
            os.makedirs(self.manifest_dir)

        manifest_fn = os.path.join(self.manifest_dir, request.name + ".json")

        # Invariant is that if a manifest file exists, then it accurately reflects that has been stored to disk. Since
        # we're about to potentially overwrite files, destroy the old manifest.
        if os.path.exists(manifest_fn):
            os.remove(manifest_fn)

        # convert the request to a manifest, so we can save it
        service_manifest = {
            "name": request.name,
            "version": request.version,
            "hash": hash,
            "state": state,
            "dir": service_dir,
            "manifest_fn": manifest_fn,
            "dest_dir": os.path.join(self.services_dest_dir, request.name),
            "xprotos": [],
            "decls": [],
            "attics": [],
            "convenience_methods": [],
        }

        if state == "load":
            for item in request.xprotos:
                file(os.path.join(service_dir, item.filename), "w").write(item.contents)
                service_manifest["xprotos"].append({"filename": item.filename})

            for item in request.decls:
                file(os.path.join(service_dir, item.filename), "w").write(item.contents)
                service_manifest["decls"].append({"filename": item.filename})

            if request.attics:
                attic_dir = os.path.join(service_dir, "attic")
                service_manifest["attic_dir"] = attic_dir
                if not os.path.exists(attic_dir):
                    os.makedirs(attic_dir)
                for item in request.attics:
                    file(os.path.join(attic_dir, item.filename), "w").write(
                        item.contents
                    )
                    service_manifest["attics"].append({"filename": item.filename})

            for item in request.convenience_methods:
                save_path = os.path.join(self.convenience_methods_dir, item.filename)
                file(save_path, "w").write(item.contents)
                service_manifest["convenience_methods"].append(
                    {"filename": item.filename, "path": save_path}
                )

        return service_manifest

    def run_xosgenx_service(self, manifest):
        if not os.path.exists(manifest["dest_dir"]):
            os.makedirs(manifest["dest_dir"])

        xproto_filenames = [
            os.path.join(manifest["dir"], x["filename"]) for x in manifest["xprotos"]
        ]

        # Generate models
        is_service = manifest["name"] != "core"

        args = XOSProcessorArgs(
            output=manifest["dest_dir"],
            attic=os.path.join(manifest["dir"], "attic"),
            files=xproto_filenames,
        )

        if is_service:
            args.target = "service.xtarget"
            args.write_to_file = "target"
        else:
            args.target = "django.xtarget"
            args.dest_extension = "py"
            args.write_to_file = "model"

        XOSProcessor.process(args)

        # Generate security checks
        security_args = XOSProcessorArgs(
            output=manifest["dest_dir"],
            target="django-security.xtarget",
            dest_file="security.py",
            write_to_file="single",
            files=xproto_filenames,
        )

        XOSProcessor.process(security_args)

        # Generate __init__.py
        if manifest["name"] == "core":

            class InitArgs:
                output = manifest["dest_dir"]
                target = "init.xtarget"
                dest_file = "__init__.py"
                write_to_file = "single"
                files = xproto_filenames

            XOSProcessor.process(InitArgs())

        else:
            init_py_filename = os.path.join(manifest["dest_dir"], "__init__.py")
            if not os.path.exists(init_py_filename):
                open(init_py_filename, "w").write("# created by dynamicbuild")

        # the xosgenx templates don't handle copying the models.py file for us, so do it here.
        for item in manifest["decls"]:
            src_fn = os.path.join(manifest["dir"], item["filename"])
            dest_fn = os.path.join(manifest["dest_dir"], item["filename"])
            shutil.copyfile(src_fn, dest_fn)

        # If the attic has a header.py, make sure it is copied to the right place
        attic_header_py_src = os.path.join(manifest["dir"], "attic", "header.py")
        service_header_py_dest = os.path.join(manifest["dest_dir"], "header.py")
        if os.path.exists(attic_header_py_src):
            shutil.copyfile(attic_header_py_src, service_header_py_dest)
        elif os.path.exists(service_header_py_dest):
            os.remove(service_header_py_dest)

    def remove_service(self, manifest):
        # remove any xproto files, otherwise "make rebuild_protos" will pick them up
        if os.path.exists(manifest["dir"]):
            for fn in os.listdir(manifest["dir"]):
                fn = os.path.join(manifest["dir"], fn)
                if fn.endswith(".xproto"):
                    os.remove(fn)

        # Rather than trying to unmigrate while the core is running, let's handle unmigrating the service while we're
        # outside of the core process. We're going to save the manifest file, and the manifest file will have
        # {"state": "unload"} in it. That can be our external signal to unmigrate.

        # This is what unmigrate will do, external to this process:
        #     1) remove the models (./manage.py migrate my_app_name zero)
        #     2) remove the contenttypes
        #            # does step 1 already do this?
        #            from django.contrib.contenttypes.models import ContentType
        #            for c in ContentType.objects.all():
        #                if not c.model_class():
        #                    print "deleting %s" % c
        #                    c.delete()
        #     3) Remove the service files
