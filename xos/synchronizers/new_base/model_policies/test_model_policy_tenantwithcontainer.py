import unittest
from mock import patch
import mock

import os, sys
sys.path.append("../../..")
sys.path.append("../../new_base/model_policies")
config = basic_conf = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml")
from xosconfig import Config
Config.init(config, 'synchronizer-config-schema.yaml')

import synchronizers.new_base.modelaccessor

from model_policy_tenantwithcontainer import TenantWithContainerPolicy

class MockTenant:
    provider_service = None
    deleted = False
    instance = None
    service_specific_attribute = {}

class TestModelPolicyVsgTenant(unittest.TestCase):
    def setUp(self):
        self.policy = TenantWithContainerPolicy()
        self.tenant = MockTenant()
        
    @patch.object(MockTenant, "provider_service")
    def test_manage_container_no_slices(self, provider_service):
        provider_service.slices.count.return_value = 0
        with self.assertRaises(Exception) as e:
            self.policy.manage_container(self.tenant)
        self.assertEqual(e.exception.message, "The service has no slices")

if __name__ == '__main__':
    unittest.main()
