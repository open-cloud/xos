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


from __future__ import absolute_import

import os
import sys

import pykwalify
import yaml
from pykwalify.core import Core as PyKwalify

from . import default

pykwalify.init_logging(1)

DEFAULT_CONFIG_FILE = "/opt/xos/xos_config.yaml"
DEFAULT_CONFIG_SCHEMA = "xos-config-schema.yaml"
INITIALIZED = False
CONFIG_FILE = None
CONFIG = {}

OVERRIDE_CONFIG = {}


class Config:
    """
    XOS Configuration APIs
    """

    @staticmethod
    def init(
        config_file=DEFAULT_CONFIG_FILE,
        config_schema=DEFAULT_CONFIG_SCHEMA,
        override_config_file=None,
    ):

        # make schema relative to this directory
        # TODO give the possibility to specify an absolute path
        config_schema = Config.get_abs_path(config_schema)

        global INITIALIZED
        global CONFIG
        global CONFIG_FILE

        global OVERRIDE_CONFIG
        global OVERRIDE_CONFIG_FILE
        global OVERRIDE_CONFIG_SCHEMA

        # Use same schema for both provided and global config by default
        OVERRIDE_CONFIG_SCHEMA = config_schema
        OVERRIDE_CONFIG_FILE = override_config_file

        # the config module can be initialized only one
        if INITIALIZED:
            raise Exception("[XOS-Config] Module already initialized")
        INITIALIZED = True

        # if XOS_CONFIG_FILE is defined override the config_file
        # FIXME shouldn't this stay in whatever module call this one? and then just pass the file to the init method
        if os.environ.get("XOS_CONFIG_FILE"):
            config_file = os.environ["XOS_CONFIG_FILE"]

        # if XOS_CONFIG_SCHEMA is defined override the config_schema
        # FIXME shouldn't this stay in whatever module call this one? and then just pass the file to the init method
        if os.environ.get("XOS_CONFIG_SCHEMA"):
            config_schema = Config.get_abs_path(os.environ["XOS_CONFIG_SCHEMA"])

        # allow OVERRIDE_CONFIG_* to be overridden  by env vars
        if os.environ.get("XOS_OVERRIDE_CONFIG_FILE"):
            OVERRIDE_CONFIG_FILE = os.environ["XOS_OVERRIDE_CONFIG_FILE"]
        if os.environ.get("XOS_OVERRIDE_CONFIG_SCHEMA"):
            OVERRIDE_CONFIG_SCHEMA = Config.get_abs_path(
                os.environ["XOS_OVERRIDE_CONFIG_SCHEMA"]
            )

        # if a -C parameter is set in the cli override the config_file
        # FIXME shouldn't this stay in whatever module call this one? and then just pass the file to the init method
        if Config.get_cli_param(sys.argv):
            config_schema = Config.get_cli_param(sys.argv)

        CONFIG_FILE = config_file
        CONFIG = Config.read_config(config_file, config_schema)

        # if an override is set
        if OVERRIDE_CONFIG_FILE is not None:
            OVERRIDE_CONFIG = Config.read_config(
                OVERRIDE_CONFIG_FILE, OVERRIDE_CONFIG_SCHEMA, True
            )

    @staticmethod
    def get_config_file():
        return CONFIG_FILE

    @staticmethod
    def clear():
        global INITIALIZED
        INITIALIZED = False

    @staticmethod
    def get_abs_path(path):
        if os.path.isabs(path):
            return path
        return os.path.dirname(os.path.realpath(__file__)) + "/" + path

    @staticmethod
    def validate_config_format(config_file, config_schema):
        schema = os.path.abspath(config_schema)
        c = PyKwalify(source_file=config_file, schema_files=[schema])
        c.validate(raise_exception=True)

    @staticmethod
    def get_cli_param(args):
        last = None
        for arg in args:
            if last == "-C":
                return arg
            last = arg

    @staticmethod
    def read_config(config_file, config_schema, ignore_if_not_found=False):
        """
        Read the configuration file and return a dictionary
        :param config_file: string
        :return: dict
        """

        if not os.path.exists(config_file) and ignore_if_not_found:
            return {}

        if not os.path.exists(config_file):
            raise Exception("[XOS-Config] Config file not found at: %s" % config_file)

        if not os.path.exists(config_schema):
            raise Exception(
                "[XOS-Config] Config schema not found at: %s" % config_schema
            )

        try:
            Config.validate_config_format(config_file, config_schema)
        except Exception as e:
            try:
                error_msg = e.msg
            except AttributeError:
                error_msg = str(e)
            raise Exception("[XOS-Config] The config format is wrong: %s" % error_msg)

        with open(config_file, "r") as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def get(query):
        """
        Read a parameter from the config
        :param query: a dot separated selector for configuration options (eg: database.username)
        :return: the requested parameter in any format the parameter is specified
        """
        global INITIALIZED
        global CONFIG
        global OVERRIDE_CONFIG
        global OVERRIDE_CONFIG_FILE

        if not INITIALIZED:
            raise Exception("[XOS-Config] Module has not been initialized")

        val = Config.get_param(query, CONFIG)
        if OVERRIDE_CONFIG_FILE or not val:
            # if we specified an override configuration, we should override the value
            # we also look for the value in case it's missing
            over_val = Config.get_param(query, OVERRIDE_CONFIG)
            if over_val is not None:
                val = over_val
        if not val:
            val = Config.get_param(query, default.DEFAULT_VALUES)
        if not val:
            # TODO if no val return none
            # raise Exception('[XOS-Config] Config does not have a value (or a default) parameter %s' % query)
            return None
        return val

    @staticmethod
    def get_param(query, config):
        """
        Search for a parameter in config's first level, other call get_nested_param
        :param query: a dot separated selector for configuration options (eg: database.username)
        :param config: the config source to read from (can be the config file or the defaults)
        :return: the requested parameter in any format the parameter is specified
        """
        keys = query.split(".")
        if len(keys) == 1:
            key = keys[0]
            if key not in config:
                return None
            return config[key]
        else:
            return Config.get_nested_param(keys, config)

    @staticmethod
    def get_nested_param(keys, config):
        """

        :param keys: a list of descending selector
        :param config: the config source to read from (can be the config file or the defaults)
        :return: the requested parameter in any format the parameter is specified
        """
        param = config
        for k in keys:
            if k not in param:
                return None
            param = param[k]
        return param


if __name__ == "__main__":
    Config.init()
