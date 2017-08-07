
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


import unittest
from mock import patch
import os
from xosconfig import Config
from xosconfig import Config as Config2

basic_conf = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/confs/basic_conf.yaml")
yaml_not_valid = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/confs/yaml_not_valid.yaml")
invalid_format = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/confs/invalid_format.yaml")
sample_conf = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/confs/sample_conf.yaml")

small_schema = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/schemas/small_schema.yaml")

services_list = {
  "xos-ws": [],
  "xos-db": [],
}

db_service = [
          {
            "ModifyIndex": 6,
            "CreateIndex": 6,
            "Node": "0152982c3159",
            "Address": "172.19.0.2",
            "ServiceID": "0d53ce210785:frontend_xos_db_1:5432",
            "ServiceName": "xos-db",
            "ServiceTags": [],
            "ServiceAddress": "172.18.0.4",
            "ServicePort": 5432,
            "ServiceEnableTagOverride": "false"
          }
        ]

class XOSConfigTest(unittest.TestCase):
    """
    Testing the XOS Config Module
    """

    def tearDown(self):
        # NOTE clear the config after each test
        Config.clear()

    def test_initialize_only_once(self):
        """
        [XOS-Config] Raise if initialized twice
        """
        with self.assertRaises(Exception) as e:
            Config.init(sample_conf)
            Config2.init(sample_conf)
        self.assertEqual(e.exception.message, "[XOS-Config] Module already initialized")

    def test_config_not_initialized(self):
        """
        [XOS-Config] Raise if accessing properties without initialization
        """
        with self.assertRaises(Exception) as e:
            Config.get("database")
        self.assertEqual(e.exception.message, "[XOS-Config] Module has not been initialized")

    def test_missing_file_exception(self):
        """
        [XOS-Config] Raise if file not found 
        """
        with self.assertRaises(Exception) as e:
            Config.init("missing_conf")
        self.assertEqual(e.exception.message, "[XOS-Config] Config file not found at: missing_conf")

    def test_yaml_not_valid(self):
        """
        [XOS-Config] Raise if yaml is not valid
        """
        with self.assertRaises(Exception) as e:
            Config.init(yaml_not_valid)
        self.assertEqual(e.exception.message, "[XOS-Config] The config format is wrong: Unable to load any data from source yaml file")

    def test_invalid_format(self):
        """
        [XOS-Config] Raise if format is not valid (we expect a dictionary)
        """
        with self.assertRaises(Exception) as e:
            Config.init(invalid_format)
        self.assertEqual(e.exception.message, "[XOS-Config] The config format is wrong: Schema validation failed:\n - Value '['I am', 'a yaml', 'but the', 'format is not', 'correct']' is not a dict. Value path: ''.")

    def test_env_override(self):
        """
        [XOS-Config] the XOS_CONFIG_FILE environment variable should override the config_file
        """
        os.environ["XOS_CONFIG_FILE"] = "env.yaml"
        with self.assertRaises(Exception) as e:
            Config.init("missing_conf")
        self.assertEqual(e.exception.message, "[XOS-Config] Config file not found at: env.yaml")
        del os.environ["XOS_CONFIG_FILE"]

    def test_schema_override(self):
        """
        [XOS-Config] the XOS_CONFIG_SCHEMA environment variable should override the config_schema
        """
        os.environ["XOS_CONFIG_SCHEMA"] = "env-schema.yaml"
        with self.assertRaises(Exception) as e:
            Config.init(basic_conf)
        self.assertRegexpMatches(e.exception.message, '\[XOS\-Config\] Config schema not found at: (.+)env-schema\.yaml')
        # self.assertEqual(e.exception.message, "[XOS-Config] Config schema not found at: env-schema.yaml")
        del os.environ["XOS_CONFIG_SCHEMA"]

    def test_schema_override_usage(self):
        """
        [XOS-Config] the XOS_CONFIG_SCHEMA should be used to validate a config
        """
        os.environ["XOS_CONFIG_SCHEMA"] = small_schema
        with self.assertRaises(Exception) as e:
            Config.init(basic_conf)
        self.assertEqual(e.exception.message, "[XOS-Config] The config format is wrong: Schema validation failed:\n - Key 'database' was not defined. Path: ''.")
        del os.environ["XOS_CONFIG_SCHEMA"]

    def test_get_cli_param(self):
        """
        [XOS-Config] Should read CLI -C param
        """
        args = ["-A", "Foo", "-c", "Bar", "-C", "config.yaml"]
        res = Config.get_cli_param(args)
        self.assertEqual(res, "config.yaml")

    def test_get_default_val_for_missing_param(self):
        """
        [XOS-Config] Should get the default value if nothing is specified
        """
        Config.init(basic_conf)
        log = Config.get("logging")
        self.assertEqual(log, {
            "level": "info",
            "channels": ["file", "console"],
            "logstash_hostport": "cordloghost:5617",
            "file":  "/var/log/xos.log",
        })

    def test_get_config_file(self):
        """
        [XOS-Config] Should return the config file in use
        """
        Config.init(sample_conf)
        res = Config.get_config_file()
        self.assertEqual(res, sample_conf)

    def test_get_missing_param(self):
        """
        [XOS-Config] Should raise reading a missing param
        """
        Config.init(sample_conf)
        res = Config.get("foo")
        self.assertEqual(res, None)

    def test_get_first_level(self):
        """
        [XOS-Config] Should return a first level param
        """
        Config.init(sample_conf)
        # NOTE we are using Config2 here to be sure that the configuration is readable from any import,
        # not only from the one that has been used to initialize it
        res = Config2.get("database")
        self.assertEqual(res, {
            "name": "xos",
            "username": "test",
            "password": "safe"
        })

    def _test_get_child_level(self):
        """
        [XOS-Config] Should return a child level param
        """
        Config.init(sample_conf)
        res = Config.get("nested.parameter.for")
        self.assertEqual(res, "testing")

    def test_get_service_list(self):
        """
        [XOS-Config] Should query registrator and return a list of services
        """
        with patch("xosconfig.config.requests.get") as mock_get:
            mock_get.return_value.json.return_value = services_list
            res = Config.get_service_list()
            self.assertEqual(res, [
                "xos-ws",
                "xos-db",
            ])

    def test_get_service_info(self):
        """
        [XOS-Config] Should query registrator and return service info
        """
        with patch("xosconfig.config.requests.get") as mock_get:
            mock_get.return_value.json.return_value = db_service
            info = Config.get_service_info("xos-db")
            self.assertEqual(info, {
                "name": "xos-db",
                "url": "172.18.0.4",
                "port": 5432
            })

    def test_fail_get_service_info(self):
        """
        [XOS-Config] Should query registrator and return an exception if it"s down
        """
        with patch("xosconfig.config.requests.get") as mock_get:
            mock_get.return_value.ok = False
            with self.assertRaises(Exception) as e:
                Config.get_service_info("missing-service")
            self.assertEqual(e.exception.message, "[XOS-Config] Registrator is down")

    def test_missing_get_service_info(self):
        """
        [XOS-Config] Should query registrator and return an exception if service is not there
        """
        with patch("xosconfig.config.requests.get") as mock_get:
            mock_get.return_value.json.return_value = []
            with self.assertRaises(Exception) as e:
                Config.get_service_info("missing-service")
            self.assertEqual(e.exception.message, "[XOS-Config] The service missing-service looking for does not exist")


    def test_get_service_endpoint(self):
        """
        [XOS-Config] Should query registrator and return service endpoint
        """
        with patch("xosconfig.config.requests.get") as mock_get:
            mock_get.return_value.json.return_value = db_service
            endpoint = Config.get_service_endpoint("xos-db")
            self.assertEqual(endpoint, "http://172.18.0.4:5432")


if __name__ == '__main__':
    unittest.main()