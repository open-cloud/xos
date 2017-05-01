import unittest
import sys
import os
import inspect
import json
sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import xos.exceptions
from xos.exceptions import *

class TestXosExceptions(unittest.TestCase):
    """
    Test the conversion from excenption to json
    """
    def test_get_json_error_details(self):
        res = xos.exceptions._get_json_error_details({'foo': 'bar'})
        assert res == json.dumps({"foo":"bar"})

    def test_exceptions(self):
        """
        This test iterate over all the classes in exceptions.py and if they start with XOS
         validate the json_detail output
        """
        for name, item in inspect.getmembers(xos.exceptions):
            if inspect.isclass(item) and name.startswith('XOS'):
                e = item('test error', {'foo': 'bar'})
                res = e.json_detail
                assert res == json.dumps(
                    {"fields": {"foo": "bar"}, "specific_error": "test error", "error": name})

if __name__ == '__main__':
    unittest.main()