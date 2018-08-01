
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

    def test_xproto_required_to_django(self):
        field = {
            'name': 'foo',
            'options': {
                'modifier': 'required'
            }
        }

        res = map_xproto_to_django(field)
        self.assertEqual(res, {'blank': False, 'null': False})

    def test_xproto_optional_to_django(self):
        field = {
            'name': 'foo',
            'options': {
                'modifier': 'optional'
            }
        }

        res = map_xproto_to_django(field)
        self.assertEqual(res, {'blank': True, 'null': True})


    def test_map_xproto_to_django(self):

        options = {
            'help_text': 'bar',
            'default': 'default_value',
            'null':  True,
            'db_index': False,
            'blank': False,
            'min_value': 16,
            'max_value': 16
        }

        field = {
            'name': 'foo',
            'options': options
        }

        res = map_xproto_to_django(field)
        self.assertEqual(res, options)

    def test_format_options_string(self):

        options = {
            'null':  True,
            'min_value': 16,
            'max_value': 16
        }

        res = format_options_string(options)
        self.assertEqual(res, "null = True, validators=[MaxValueValidator(16), MinValueValidator(16)]")

        options = {
            'min_value': 16,
            'max_value': 16
        }

        res = format_options_string(options)
        self.assertEqual(res, "validators=[MaxValueValidator(16), MinValueValidator(16)]")

        options = {
            'null': True,
        }

        res = format_options_string(options)
        self.assertEqual(res, "null = True")

if __name__ == '__main__':
    unittest.main()


