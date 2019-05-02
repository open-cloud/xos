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

# xosproject/xos-client
FROM xosproject/alpine-grpc-base:0.9.1

# Add libraries
RUN mkdir -p /opt/xos
COPY lib /opt/xos/lib
COPY VERSION /opt/xos

# Install python using pip so their dependencies are installed
RUN pip install -e /opt/xos/lib/xos-util \
 && pip install -e /opt/xos/lib/xos-config \
 && pip install -e /opt/xos/lib/xos-genx \
 && pip install -e /opt/xos/lib/xos-api \
 && pip freeze > /var/xos/pip_freeze_xos-client_`date -u +%Y%m%dT%H%M%S`

# Label image
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown

LABEL org.label-schema.schema-version=1.0 \
      org.label-schema.name=xos-client \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date

CMD ["xossh"]
