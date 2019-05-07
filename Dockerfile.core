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

# xosproject/xos-core
FROM xosproject/alpine-grpc-base:0.9.1

# Install libraries and python requirements
COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache bash postgresql-dev postgresql-client \
 && pip install -r /tmp/requirements.txt \
 && pip freeze > /var/xos/pip_freeze_xos-core_`date -u +%Y%m%dT%H%M%S` \
 && mkdir -p /opt/xos

# Install XOS
COPY VERSION /opt/xos
COPY xos /opt/xos
COPY lib /opt/xos/lib

# Install XOS libraries
RUN pip install -e /opt/xos/lib/xos-config \
 && pip install -e /opt/xos/lib/xos-genx \
 && pip install -e /opt/xos/lib/xos-kafka \
 && pip freeze > /var/xos/pip_freeze_xos-core_libs_`date -u +%Y%m%dT%H%M%S` \
 && mkdir -p /opt/cord_profile /opt/xos-services /opt/xos_libraries \
 && xosgenx --output /opt/xos/core/models --target django.xtarget --dest-extension py \
      --write-to-file model /opt/xos/core/models/core.xproto \
 && xosgenx --output /opt/xos/core/models --target django-security.xtarget --dest-file security.py \
      --write-to-file single /opt/xos/core/models/core.xproto \
 && xosgenx --output /opt/xos/core/models --target init.xtarget --dest-file __init__.py \
      --write-to-file single /opt/xos/core/models/core.xproto

# Set environment variables
ENV HOME /root

# Define working directory
WORKDIR /opt/xos

# Label image
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown

# Record git build information
RUN echo $org_label_schema_vcs_ref > /opt/xos/COMMIT

LABEL org.label-schema.schema-version=1.0 \
      org.label-schema.name=xos-core \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date
