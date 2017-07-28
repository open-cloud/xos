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

import os
import yaml
from django.db import models, migrations
from django.contrib.auth.hashers import make_password

FIXTURES = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/initial_data.yaml')

def load_data_from_yaml():
    file = open(FIXTURES, 'r').read()
    try:
        data = yaml.load(file)
        return data
    except Exception, e:
        raise Exception("Cannot load inital data file: %s" % e.message)


def persist_data(apps, schema_editor):

    data = load_data_from_yaml()

    # iterate over the data
    for entry in data:

        # retrieve the class for that model
        [app, model_name] = entry['model'].split('.')
        model_class = apps.get_model(app, model_name)

        # create a new instance for that model
        i = model_class(**entry['fields'])

        # if model is user hash the password
        if model_name == "User":
            i.password = make_password(entry['fields']['password'])

        # check relations
        if 'relations' in entry:
            for (r_name, r) in entry['relations'].items():
                # retrieve the related model
                [r_app, r_model_name] = r['model'].split('.')
                related_model_class = apps.get_model(r_app, r_model_name)
                r_model = related_model_class.objects.get(**r['fields'])

                # assign relation
                setattr(i, r_name, r_model)

        # save the instance
        i.save()
        print "Created %s: %s" % (model_name, entry['fields'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(persist_data)
    ]