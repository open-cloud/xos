#!/usr/bin/python

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

# TO RUN
# source scripts/setup_venv.sh
# xos-migrate [-s <service-name>] [-r ~/cord]
# eg: xos-migrate -r ~/Sites/cord -s core -s fabric

# TODO
# - add support to specify a name to be given to the generated migration (--name parameter in django makemigrations)
# - add support to generate empty migrations (needed for data-only migrations)

import os
import sys
import argparse
import yaml
import shutil
from xosgenx.generator import XOSProcessor, XOSProcessorArgs
from xosconfig import Config
from multistructlog import create_logger

REPO_ROOT = "~/cord"


def get_abs_path(dir_):
    """ Convert a path specified by the user, which might be relative or based on
        home directory location, into an absolute path.
    """
    if os.path.isabs(dir_):
        return os.path.realpath(dir_)
    if dir_[0] == "~" and not os.path.exists(dir_):
        dir_ = os.path.expanduser(dir_)
        return os.path.abspath(dir_)
    return os.path.abspath(os.path.join(os.getcwd(), dir_))


def get_migration_library_path(dir_):
    """ Return a directory relative to the location of the migration library """
    return os.path.dirname(os.path.realpath(__file__)) + "/" + dir_


def print_banner(root):
    log.info(r"---------------------------------------------------------------")
    log.info(r"                                    _                  __      ")
    log.info(r"   _  ______  _____      ____ ___  (_)___ __________ _/ /____  ")
    log.info(r"  | |/_/ __ \/ ___/_____/ __ `__ \/ / __ `/ ___/ __ `/ __/ _ \ ")
    log.info(r" _>  </ /_/ (__  )_____/ / / / / / / /_/ / /  / /_/ / /_/  __/ ")
    log.info(r"/_/|_|\____/____/     /_/ /_/ /_/_/\__, /_/   \__,_/\__/\___/  ")
    log.info(r"                                  /____/                       ")
    log.info(r"---------------------------------------------------------------")
    log.debug("CORD repo root", root=root)
    log.debug("Storing logs in: %s" % os.environ["LOG_FILE"])
    log.debug(r"---------------------------------------------------------------")


def generate_core_models(core_dir):
    core_xproto = os.path.join(core_dir, "core.xproto")

    args = XOSProcessorArgs(
        output=core_dir,
        target="django.xtarget",
        dest_extension="py",
        write_to_file="model",
        files=[core_xproto],
    )
    XOSProcessor.process(args)

    security_args = XOSProcessorArgs(
        output=core_dir,
        target="django-security.xtarget",
        dest_file="security.py",
        write_to_file="single",
        files=[core_xproto],
    )

    XOSProcessor.process(security_args)

    init_args = XOSProcessorArgs(
        output=core_dir,
        target="init.xtarget",
        dest_file="__init__.py",
        write_to_file="single",
        files=[core_xproto],
    )
    XOSProcessor.process(init_args)


def find_xproto_in_folder(path):
    """
    Recursively iterate a folder tree to look for any xProto file.
    We use this function in case that the name of the xProto is different from the name of the folder (eg: olt-service)
    :param path: the root folder to start the search
    :return: [string]
    """
    xprotos = []
    for fn in os.listdir(path):
        # skip hidden files and folders
        if fn.startswith("."):
            continue
        full_path = os.path.join(path, fn)
        if fn.endswith(".xproto"):
            xprotos.append(full_path)
        elif os.path.isdir(full_path):
            xprotos = xprotos + find_xproto_in_folder(full_path)
    return xprotos


def find_decls_models(path):
    """
    Recursively iterate a folder tree to look for any models.py file.
    This files contain the base model for _decl generated models.
    :param path: the root folder to start the search
    :return: [string]
    """
    decls = []
    for fn in os.listdir(path):
        # skip hidden files and folders
        if fn.startswith("."):
            continue
        full_path = os.path.join(path, fn)
        if fn == "models.py":
            decls.append(full_path)
        elif os.path.isdir(full_path):
            decls = decls + find_decls_models(full_path)
    return decls


def get_service_name_from_config(path):
    """
    Given a service folder look for the config.yaml file and find the name
    :param path: the root folder to start the search
    :return: string
    """
    config = os.path.join(path, "xos/synchronizer/config.yaml")
    if not os.path.isfile(config):
        raise Exception("Config file not found at: %s" % config)

    cfg_file = open(config)
    cfg = yaml.safe_load(cfg_file)
    return cfg["name"]


def generate_service_models(service_dir, service_dest_dir, service_name):
    """
    Generate the django code starting from xProto for a given service.
    :param service_dir: string (path to the folder)
    :param service_name: string (name of the service)
    :return: void
    """
    sync_dir = os.path.join(service_dir, "xos/synchronizer/models")
    xprotos = find_xproto_in_folder(sync_dir)
    decls = find_decls_models(sync_dir)
    log.debug("Generating models for %s from files %s" % (service_name, ", ".join(xprotos)))
    out_dir = os.path.join(service_dest_dir, service_name)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    args = XOSProcessorArgs(
        output=out_dir,
        files=xprotos,
        target="service.xtarget",
        write_to_file="target",
    )
    XOSProcessor.process(args)

    security_args = XOSProcessorArgs(
        output=out_dir,
        target="django-security.xtarget",
        dest_file="security.py",
        write_to_file="single",
        files=xprotos,
    )

    XOSProcessor.process(security_args)

    init_py_filename = os.path.join(out_dir, "__init__.py")
    if not os.path.exists(init_py_filename):
        open(init_py_filename, "w").write("# created by dynamicbuild")

    # copy over models.py files from the service
    if len(decls) > 0:
        for file in decls:
            fn = os.path.basename(file)
            src_fn = file
            dest_fn = os.path.join(out_dir, fn)
            log.debug("Copying models.py from %s to %s" % (src_fn, dest_fn))
            shutil.copyfile(src_fn, dest_fn)

    # copy existing migrations from the service, otherwise they won't be incremental
    src_dir = os.path.join(service_dir, "xos", "synchronizer", "migrations")
    if os.path.isdir(src_dir):
        dest_dir = os.path.join(out_dir, "migrations")
        if os.path.isdir(dest_dir):
            shutil.rmtree(dest_dir)  # empty the folder, we'll copy everything again
        shutil.copytree(src_dir, dest_dir)


def copy_service_migrations(service_dir, service_dest_dir, service_name):
    """
    Once the migrations are generated, copy them in the correct location
    :param service_dir: string (path to the folder)
    :param service_name: string (name of the service)
    :return: void
    """
    log.debug("Copying %s migrations to %s" % (service_name, service_dir))
    migration_dir = os.path.join(service_dest_dir, service_name, "migrations")
    dest_dir = os.path.join(service_dir, "xos", "synchronizer", "migrations")
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)  # empty the folder, we'll copy everything again
    shutil.copytree(migration_dir, dest_dir)
    # clean after the tool, generated migrations has been moved in the service repo
    shutil.rmtree(get_abs_path(os.path.join(migration_dir, "../")))


def monkey_patch_migration_template():
    import django
    django.setup()

    import django.db.migrations.writer as dj
    dj.MIGRATION_TEMPLATE = """\
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

# -*- coding: utf-8 -*-
# Generated by Django %(version)s on %(timestamp)s
from __future__ import unicode_literals

%(imports)s

class Migration(migrations.Migration):
%(replaces_str)s%(initial_str)s
    dependencies = [
%(dependencies)s\
    ]

    operations = [
%(operations)s\
    ]
"""


def configure_logging(verbose):
    global log
    # INITIALIZING LOGGER
    Config.init()

    cfg = Config().get("logging")
    if verbose:
        cfg["handlers"]["console"]["level"] = "DEBUG"

    log = create_logger(cfg)


# SETTING ENV
os.environ["LOG_FILE"] = get_migration_library_path("django.log")
os.environ["XOS_CONFIG_SCHEMA"] = get_migration_library_path("migration_cfg_schema.yaml")
os.environ["XOS_CONFIG_FILE"] = get_migration_library_path("migration_cfg.yaml")
os.environ["MIGRATIONS"] = "true"
# this is populated in case we generate migrations for services and it's used in settings.py
os.environ["INSTALLED_APPS"] = ""

# PARAMS
parser = argparse.ArgumentParser(description="XOS Migrations")
required = parser.add_argument_group("required arguments")

required.add_argument(
    "-s",
    "--service",
    action="append",
    required=True,
    dest="service_names",
    help="The name of the folder containing the service in cord/orchestration/xos-services"
)

parser.add_argument(
    "-r",
    "--repo",
    default=REPO_ROOT,
    dest="repo_root",
    help="Path to the CORD repo root (defaults to '../..'). Mutually exclusive with '--xos'."
)

parser.add_argument(
    "-x",
    "--xos-dir",
    default=None,
    dest="xos_root",
    help="Path to directory of the XOS repo. Incompatible with '--repo'."
)

parser.add_argument(
    "--services-dir",
    default=None,
    dest="services_root",
    help="Path to directory of the XOS services root. Incompatible with '--repo'." +
         "Note that all the services repo needs to be siblings"
)

parser.add_argument(
    "--check",
    default=False,
    action="store_true",
    dest="check",
    help="Check if the migrations are generated for a given service. Does not apply any change."
)

parser.add_argument(
    "-v",
    "--verbose",
    help="increase log verbosity",
    dest="verbose",
    action="store_true"
)


def run():
    service_base_dir = None

    # cleaning up from possible incorrect states
    if "INSTALLED_APPS" in os.environ:
        del os.environ["INSTALLED_APPS"]

    args = parser.parse_args()

    configure_logging(args.verbose)

    print_banner(args.repo_root)

    # validating args, the solution is hacky but it does not fit `add_mutually_exclusive_group`
    # and it's not complex enough for the solution proposed here:
    # https://stackoverflow.com/questions/17909294/python-argparse-mutual-exclusive-group
    if args.service_names != ["core"] and \
            ((args.xos_root and not args.services_root) or (args.services_root and not args.xos_root)):
        # if we're only generating migrations for the core,
        # the --xos-dir is the only think we need
        log.error("You need to set both --xos-dir and \
                --services-dir parameters when generating migrations for a service")
        sys.exit(1)

    if (args.xos_root or args.services_root) and (args.repo_root != REPO_ROOT):
        log.error("The --xos-dir or --services-dir parameters are not compatible with the --repo parameter")
        sys.exit(1)

    # find absolute path to the code
    if args.xos_root or args.services_root:
        xos_path = get_abs_path(os.path.join(args.xos_root, "xos"))
        if args.services_root:
            # NOTE this params is optional (we may be generating migrations for the core only
            service_base_dir = get_abs_path(args.services_root)
    else:
        xos_path = get_abs_path(os.path.join(args.repo_root, "orchestration/xos/xos/"))
        service_base_dir = get_abs_path(os.path.join(xos_path, "../../xos-services/"))

    log.debug("XOS Path: %s" % xos_path)
    log.debug("Service Base Dir: %s" % service_base_dir)

    service_dest_dir = get_abs_path(os.path.join(xos_path, "services/"))
    core_dir = get_abs_path(os.path.join(xos_path, "core/models/"))

    # we need to append the xos folder to sys.path
    original_sys_path = sys.path
    sys.path.append(xos_path)

    log.info("Services: %s" % ", ".join(args.service_names))

    django_cli_args = ['xos-migrate.py', "makemigrations"]

    # generate the code for each service and create a list of parameters to pass to django
    app_list = []
    for service in args.service_names:
        # NOTE we need core models to be there as all the services depend on them
        generate_core_models(core_dir)
        if service == "core":
            django_cli_args.append("core")
        else:
            service_dir = os.path.join(service_base_dir, service)
            service_name = get_service_name_from_config(service_dir)
            generate_service_models(service_dir, service_dest_dir, service_name)
            app_list.append("services.%s" % service_name)

            django_cli_args.append(service_name)

    if len(app_list) > 0:
        os.environ["INSTALLED_APPS"] = ",".join(app_list)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

    monkey_patch_migration_template()

    if args.check:
        django_cli_args.append("--check")
        django_cli_args.append("--dry-run")

    from django.core.management import execute_from_command_line

    try:
        log.debug("Django CLI Args", args=django_cli_args)
        execute_from_command_line(django_cli_args)
        returncode = 0
    except SystemExit as e:
        returncode = e.message

    if returncode != 0:
        if args.check:
            log.error("Migrations are not up to date with the service changes!")
        else:
            log.error("An error occurred")
        sys.exit(returncode)

    # copying migrations back to the service
    for service in args.service_names:
        if service == "core":
            # we don't need to copy migrations for the core
            continue
        else:
            service_dir = os.path.join(service_base_dir, service)
            service_name = get_service_name_from_config(service_dir)
            copy_service_migrations(service_dir, service_dest_dir, service_name)

    # restore orginal sys.path
    sys.path = original_sys_path
