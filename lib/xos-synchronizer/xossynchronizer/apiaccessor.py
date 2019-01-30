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

import datetime

from .modelaccessor import ModelAccessor


class CoreApiModelAccessor(ModelAccessor):
    def __init__(self, orm):
        self.orm = orm
        super(CoreApiModelAccessor, self).__init__()

    def get_all_model_classes(self):
        all_model_classes = {}
        for k in self.orm.all_model_names:
            all_model_classes[k] = getattr(self.orm, k)
        return all_model_classes

    def fetch_pending(self, main_objs, deletion=False):
        if not isinstance(main_objs, list):
            main_objs = [main_objs]

        objs = []
        for main_obj in main_objs:
            if not deletion:
                lobjs = main_obj.objects.filter_special(
                    main_obj.objects.SYNCHRONIZER_DIRTY_OBJECTS
                )
            else:
                lobjs = main_obj.objects.filter_special(
                    main_obj.objects.SYNCHRONIZER_DELETED_OBJECTS
                )
            objs.extend(lobjs)

        return objs

    def fetch_policies(self, main_objs, deletion=False):
        if not isinstance(main_objs, list):
            main_objs = [main_objs]

        objs = []
        for main_obj in main_objs:
            if not deletion:
                lobjs = main_obj.objects.filter_special(
                    main_obj.objects.SYNCHRONIZER_DIRTY_POLICIES
                )
            else:
                lobjs = main_obj.objects.filter_special(
                    main_obj.objects.SYNCHRONIZER_DELETED_POLICIES
                )
            objs.extend(lobjs)

        return objs

    def obj_exists(self, o):
        # gRPC will default id to '0' for uninitialized objects
        return (o.id is not None) and (o.id != 0)

    def obj_in_list(self, o, olist):
        ids = [x.id for x in olist]
        return o.id in ids

    def now(self):
        """ Return the current time for timestamping purposes """
        return (
            datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(0)
        ).total_seconds()

    def is_type(self, obj, name):
        return obj._wrapped_class.__class__.__name__ == name

    def is_instance(self, obj, name):
        return name in obj.class_names.split(",")

    def get_content_type_id(self, obj):
        return obj.self_content_type_id

    def create_obj(self, cls, **kwargs):
        return cls.objects.new(**kwargs)
