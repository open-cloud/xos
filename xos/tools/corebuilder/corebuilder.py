
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


#!/usr/bin/python

from stat import *

""" CoreBuilder

    Read XOS Tosca Onboarding Recipes and generate a BUILD directory.

    Arguments:
        A list of onboarding recipes. Except this list to originate from
        platform-install's service inventory in the profile manifest.

    Output:
        /opt/xos_corebuilder/BUILD, populated with files from services

    Example:
        # for testing, run from inside a UI container
        python ./corebuilder.py \
            /opt/xos_services/olt-service/xos/volt-onboard.yaml \
            /opt/xos_services/vtn-service/xos/vtn-onboard.yaml \
            /opt/xos_services/openstack/xos/openstack-onboard.yaml \
            /opt/xos_services/onos-service/xos/onos-onboard.yaml \
            /opt/xos_services/vrouter/xos/vrouter-onboard.yaml \
            /opt/xos_services/vsg/xos/vsg-onboard.yaml \
            /opt/xos_services/vtr/xos/vtr-onboard.yaml \
            /opt/xos_services/fabric/xos/fabric-onboard.yaml \
            /opt/xos_services/exampleservice/xos/exampleservice-onboard.yaml \
            /opt/xos_services/monitoring/xos/monitoring-onboard.yaml \
            /opt/xos_libraries/ng-xos-lib/ng-xos-lib-onboard.yaml

        # (hypothetical) run from build container
        python ./corebuilder.py \
            /opt/cord/orchestration/xos_services/olt-service/xos/volt-onboard.yaml \
            /opt/cord/orchestration/xos_services/vtn-service/xos/vtn-onboard.yaml \
            /opt/cord/orchestration/xos_services/openstack/xos/openstack-onboard.yaml \
            /opt/cord/orchestration/xos_services/onos-service/xos/onos-onboard.yaml \
            /opt/cord/orchestration/xos_services/vrouter/xos/vrouter-onboard.yaml \
            /opt/cord/orchestration/xos_services/vsg/xos/vsg-onboard.yaml \
            /opt/cord/orchestration/xos_services/vtr/xos/vtr-onboard.yaml \
            /opt/cord/orchestration/xos_services/fabric/xos/fabric-onboard.yaml \
            /opt/cord/orchestration/xos_services/exampleservice/xos/exampleservice-onboard.yaml \
            /opt/cord/orchestration/xos_services/monitoring/xos/monitoring-onboard.yaml \
            /opt/cord/orchestration/xos_libraries/ng-xos-lib/ng-xos-lib-onboard.yaml
"""

import argparse
import os
import pdb
import shutil
import sys
import tempfile
import traceback
import urlparse
from xosgenx.generator import XOSGenerator

from toscaparser.tosca_template import ToscaTemplate

BUILD_DIR = "/opt/xos_corebuilder/BUILD"

def makedirs_if_noexist(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)

class CoreBuilderException(Exception):
    pass

class CoreBuilderMissingRecipeException(CoreBuilderException):
    pass

class CoreBuilderMalformedValueException(CoreBuilderException):
    pass

class CoreBuilderMalformedUrlException(CoreBuilderException):
    pass

class CoreBuilderMissingResourceException(CoreBuilderException):
    pass

class CoreBuilderUnknownResourceException(CoreBuilderException):
    pass

class XOSCoreBuilder(object):
    def __init__(self, recipe_list, parent_dir=None):
        # TOSCA will look for imports using a relative path from where the
        # template file is located, so we have to put the template file
        # in a specific place.
        if not parent_dir:
            parent_dir = os.getcwd()

        self.parent_dir = parent_dir

        # list of resources in the form (src_fn, dest_fn)
        self.resources = []

        # list of __init__.py files that should be ensured
        self.inits = []

        self.app_names = []

        for recipe in recipe_list:
            if not os.path.exists(recipe):
                raise CoreBuilderMissingRecipeException("Onboarding Recipe %s does not exist" % recipe)
            tosca_yaml = open(recipe).read()
            self.execute_recipe(tosca_yaml)

    def get_property_default(self, nodetemplate, name, default=None):
        props = nodetemplate.get_properties()
        if props and name in props.keys():
            return props[name].value
        return default

    def get_dest_dir(self, kind, service_name):
        xos_base = "opt/xos"
        if service_name!='core':
            service_subdir = 'services'
        else:
            service_subdir = ''

        base_dirs = {"models": "%s/services/%s/" % (xos_base, service_name),
                     "xproto": "%s/%s/%s/" % (xos_base, service_subdir, service_name),
                     "admin": "%s/services/%s/" % (xos_base, service_name),
                     "admin_template": "%s/services/%s/templates/" % (xos_base, service_name),
                     "django_library": "%s/services/%s/" % (xos_base, service_name),
                     "synchronizer": "%s/synchronizers/%s/" % (xos_base, service_name),
                     "tosca_custom_types": "%s/tosca/custom_types/" % (xos_base),
                     "tosca_resource": "%s/tosca/resources/" % (xos_base),
                     "rest_service": "%s/api/service/" % (xos_base),
                     "rest_tenant": "%s/api/tenant/" % (xos_base),
                     "private_key": "%s/services/%s/keys/" % (xos_base, service_name),
                     "public_key": "%s/services/%s/keys/" % (xos_base, service_name),
                     "vendor_js": "%s/core/xoslib/static/vendor/" % (xos_base)}

        dest_dir = base_dirs[kind]

        return dest_dir

    def fixup_path(self, fn):
        """ This is to maintain compatibility with the legacy Onboarding
            synchronizer and recipes, which has some oddly-named directories
        """

#        if fn.startswith("/opt/xos/key_import"):
#            fn = "/opt/cord_profile/key_import" + fn[19:]

        fixups = ( ("/opt/xos_services/", "/opt/cord/orchestration/xos_services/"),
                   ("/opt/xos/core/", "/opt/cord/orchestration/xos/xos/core/"),
                   ("/opt/xos_libraries/", "/opt/cord/orchestration/xos_libraries/") )

        for (pattern, replace) in fixups:
            if fn.startswith(pattern):
                fn = replace + fn[len(pattern):]

        return fn

    def execute_recipe(self, tosca_yaml):
        tmp_pathname = None
        try:
            (tmp_handle, tmp_pathname) = tempfile.mkstemp(dir=self.parent_dir, suffix=".yaml")
            os.write(tmp_handle, tosca_yaml)
            os.close(tmp_handle)

            template = ToscaTemplate(tmp_pathname)
        except:
            traceback.print_exc()
            raise
        finally:
            if tmp_pathname:
                os.remove(tmp_pathname)

        # Only one model (ServiceController aka Library), so no need to sort
        # dependencies...

        for nodetemplate in template.nodetemplates:
            self.execute_nodetemplate(nodetemplate)

    def execute_nodetemplate(self, nodetemplate):
        if nodetemplate.type == "tosca.nodes.ServiceController":
            self.execute_servicecontroller(nodetemplate)
        elif nodetemplate.type == "tosca.nodes.Library":
            # Library works just like ServiceController
            self.execute_servicecontroller(nodetemplate)
        else:
            raise CoreBuilderUnknownResourceException("Nodetemplate %s's type %s is not a known resource" % (nodetemplate.name, nodetemplate.type))

    def execute_servicecontroller(self, nodetemplate):
        service_name = nodetemplate.name
        if "#" in service_name:
            service_name = service_name.split("#")[1]

        base = self.get_property_default(nodetemplate, "base_url", None)

        copyin_resources = ("xproto", "models", "admin", "admin_template", "django_library", "tosca_custom_types", "tosca_resource",
                            "rest_service", "rest_tenant", "private_key", "public_key", "vendor_js")

        for k in copyin_resources:
            v = self.get_property_default(nodetemplate, k, None)
            if not v:
                continue

            # Private keys should not be installed to core, only synchronizers
            if (k=="private_key"):
                continue

            # Public keys should be volume mounted in /opt/cord_profile
            if (k=="public_key"):
                continue

            # If the ServiceController has models, then add it to the list of
            # django apps.
            if (k in ["models","xproto"] and service_name!="core"):
                self.app_names.append(service_name)

            # filenames can be comma-separated
            for src_fn in v.split(","):
                src_fn = src_fn.strip()

                # parse the "subdirectory:name" syntax
                subdirectory = ""
                if (" " in src_fn):
                    parts=src_fn.split()
                    for part in parts[:-1]:
                       if ":" in part:
                           (lhs, rhs) = part.split(":", 1)
                           if lhs=="subdirectory":
                               subdirectory=rhs
                           else:
                               raise CoreBuilderMalformedValueException("Malformed value %s in resource %s of recipe %s" % (v, k, nodetemplate.name))
                       else:
                           raise CoreBuilderMalformedValueException("Malformed value %s in resource %s of recipe %s" % (v, k, nodetemplate.name))
                    src_fn = parts[-1]

                # apply base_url to src_fn
                if base:
                    src_fn = urlparse.urljoin(base, src_fn)

                # ensure that it's a file:// url
                if not src_fn.startswith("file://"):
                    raise CoreBuilderMalformedUrlException("Resource `%s: %s` of recipe %s does not start with file://" % (k, src_fn, nodetemplate.name))
                src_fn = src_fn[7:]

                src_fn = self.fixup_path(src_fn)

                if not os.path.exists(src_fn):
                    raise CoreBuilderMissingResourceException("Resource '%s: %s' of recipe %s does not exist" % (k, src_fn, nodetemplate.name))

                dest_dir = self.get_dest_dir(k, service_name)
                dest_fn = os.path.join(dest_dir, subdirectory, os.path.basename(src_fn))

                self.resources.append( (k, src_fn, dest_fn, service_name) )

                # Add __init__.py files anywhere that we created a new
                # directory.
                # NOTE: omitting core, out of concern it could interfere with
                #       core's __init__.py file.

                if ((k in ["admin", "models", "rest_service", "rest_tenant", "xproto"]) and (service_name!="core")):
                    if dest_dir not in self.inits:
                        self.inits.append(dest_dir)

                    if subdirectory:
                        dir = dest_dir
                        for part in subdirectory.split("/"):
                            dir = os.path.join(dir, part)
                            if dir not in self.inits:
                                self.inits.append(dir)

    def build(self):
        # Destroy anything in the old build directory
        if os.path.exists(BUILD_DIR):
            for dir in os.listdir(BUILD_DIR):
                shutil.rmtree(os.path.join(BUILD_DIR, dir))

        # Copy all of the resources into the build directory
        for (kind, src_fn, dest_fn, service_name) in self.resources:

            build_dest_fn = os.path.join(BUILD_DIR, dest_fn)
            makedirs_if_noexist(os.path.dirname(build_dest_fn))

            if (os.path.isdir(src_fn)):
                if (not os.path.isdir(build_dest_fn)):
                    shutil.copytree(src_fn, build_dest_fn, symlinks=True)
                else:
                    os.system(
                        'cp -R %(src_fn)s/*.xproto %(src_fn)s/attic %(src_fn)s/models.py %(src_fn)s/*header.py %(build_dst_fn)s 2> /dev/null || :' % {
                            'src_fn': src_fn, 'build_dst_fn': build_dest_fn})
            else:
                shutil.copyfile(src_fn, build_dest_fn)

            if (kind == 'xproto'):
                xprotos =  [f for f in os.listdir(src_fn) if f.endswith('xproto')]

                file_list = []
                for x in xprotos:
                    file_list.append(os.path.join(src_fn, x))

                try:
                    class Args:
                        pass
                    # Generate models
                    is_service = service_name != 'core'

                    args = Args()
                    args.output = build_dest_fn
                    args.attic = src_fn + '/attic'
                    args.files = file_list

                    if is_service:
                        args.target = 'service.xtarget'
                        args.write_to_file = 'target'
                    else:
                        args.target = 'django.xtarget'
                        args.dest_extension = 'py'
                        args.write_to_file = 'model'

                    XOSGenerator.generate(args)

                    # Generate security checks
                    class SecurityArgs:
                        output = build_dest_fn
                        target = 'django-security.xtarget'
                        dest_file = 'security.py'
                        write_to_file = 'single'
                        files = file_list

                    XOSGenerator.generate(SecurityArgs())

                    # Generate __init__.py
                    if service_name == "core":
                        class InitArgs:
                            output = build_dest_fn
                            target = 'init.xtarget'
                            dest_file = '__init__.py'
                            write_to_file = 'single'
                            files = file_list

                        XOSGenerator.generate(InitArgs())

                except Exception, e:
                    print 'xproto build failed.'
                    raise e


        # Create the __init__.py files
        for fn in self.inits:
            build_dest_fn = os.path.join(BUILD_DIR, fn, "__init__.py")
            makedirs_if_noexist(os.path.dirname(build_dest_fn))
            file(build_dest_fn, "w").write("")

        # Generate the migration list
        mig_list_fn = os.path.join(BUILD_DIR, "opt/xos/xos", "xosbuilder_migration_list")
        makedirs_if_noexist(os.path.dirname(mig_list_fn))
        file(mig_list_fn, "w").write("\n".join(self.app_names)+"\n")

        # Generate the app list
        app_list_fn = os.path.join(BUILD_DIR, "opt/xos/xos", "xosbuilder_app_list")
        makedirs_if_noexist(os.path.dirname(app_list_fn))
        file(app_list_fn, "w").write("\n".join(["services.%s" % x for x in self.app_names])+"\n")

def parse_args():
    parser = argparse.ArgumentParser()

    _help = 'enable verbose logging'
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help=_help)

    _help = 'list of onboarding recipe filenames'
    parser.add_argument('recipe_names',
                        metavar="RECIPE",
                        nargs='+',
                        help=_help)

    args = parser.parse_args()

    return args

def main():
   global options

   options = parse_args()

   try:
       builder = XOSCoreBuilder(options.recipe_names)
       builder.build()
   except CoreBuilderException, e:
       if options.verbose:
           traceback.print_exc()
       else:
           print >> sys.stderr, "Error:", str(e)
       sys.exit(-1)

if __name__ == "__main__":
    main()

