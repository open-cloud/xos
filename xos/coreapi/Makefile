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

# Allow MODEL_STATUS and MODEL_OUTPUT to be passed from command line
# when using "make start"

START_OPTIONS ?=
ifdef MODEL_STATUS
  START_OPTIONS += --model_status $(MODEL_STATUS)
endif
ifdef MODEL_OUTPUT
  START_OPTIONS += --model_output $(MODEL_OUTPUT)
endif

all:
	echo "please use \"make start\" or \"make prep\""

start:
	bash -c "source env.sh && python ./core_main.py $(START_OPTIONS)"

prep: unload_unwanted app_lists rebuild_protos compile_protos try_models wait_for_db makemigrations migrate

unload_unwanted:
	python unload_unwanted_apps.py

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

wait_for_db:
	python ./wait_for_db.py
