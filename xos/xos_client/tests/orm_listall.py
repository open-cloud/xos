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

from __future__ import print_function
from xosapi import xos_grpc_client
import sys
import traceback

sys.path.append("..")


def test_callback():
    print("TEST: orm_listall_crud")

    c = xos_grpc_client.coreclient

    for model_name in c.xos_orm.all_model_names:
        model_class = getattr(c.xos_orm, model_name)

        try:
            print("   list all %s ..." % model_name, end=" ")

            objs = model_class.objects.all()

            print("[%d] okay" % len(objs))
        except BaseException:
            print("   fail!")
            traceback.print_exc()

    print("    done")


xos_grpc_client.start_api_parseargs(test_callback)
