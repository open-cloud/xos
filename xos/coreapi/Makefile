#
# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

all: prep start

start:
	bash -c "source env.sh && python ./core_main.py"

prep: app_lists rebuild_protos compile_protos try_models makemigrations migrate

app_lists:
	python app_list_builder.py

makemigrations:
	bash /opt/xos/tools/xos-manage makemigrations

migrate:
	python /opt/xos/manage.py migrate

rebuild_protos:
	cd protos && make rebuild-protos

compile_protos:
	cd protos && make

try_models:
	python ./try_models.py
