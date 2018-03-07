
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
from xosgenx.jinja2_extensions.django import *

class Jinja2BaseTests(unittest.TestCase):
    def test_xproto_optioned_fields_to_list(self):

        fields = [
            {
                'name': 'has_feedback_1',
                'options': {
                    'feedback_state': 'True',
                }
            },
            {
                'name': 'has_feedback_2',
                'options': {
                    'feedback_state': 'True',
                }
            },
            {
                'name': 'no_feedback',
                'options': {
                    'feedback_state': 'False',
                }
            }
        ]

        res = xproto_optioned_fields_to_list(fields, 'feedback_state', 'True')
        self.assertEqual(res, ["has_feedback_1", "has_feedback_2"])

if __name__ == '__main__':
    unittest.main()


