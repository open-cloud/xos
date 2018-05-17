#!/usr/bin/env bash

# Copyright 2018-present Open Networking Foundation
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

# service_scaffold.sh
# creates directories and scaffolding for a service

set -e -o pipefail

LICENSE_TEXT=$(cat <<EOF
# Copyright $(date +%Y)-present Open Networking Foundation
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
EOF
)

TPL_LICENSE_TEXT=$(cat <<EOF
{{/*
Copyright $(date +%Y)-present Open Networking Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}
EOF
)

if [ -z "${SERVICE_NAME}" ];
then
  SERVICE_NAME=$(basename "${PWD}")
  echo "SERVICE_NAME undefined, using parent directory name: ${SERVICE_NAME}"
fi

if [ -z "${SERVICE_VERSION}" ];
then
  SERVICE_VERSION="0.0.1"
  echo "SERVICE_VERSION undefined, using default: ${SERVICE_VERSION}"
fi

echo "Creating service named: ${SERVICE_NAME}, version: ${SERVICE_VERSION}"

echo "${SERVICE_VERSION}" > VERSION

# create uppercase version of SERVICE_NAME in a naive fashion
UC_SERVICE_NAME=$(echo "${SERVICE_NAME}" | cut -c1 | tr '[:lower:]' '[:upper:]')$(echo "${SERVICE_NAME}" | cut -c2-)

echo "Uppercase service name: ${UC_SERVICE_NAME}"

echo "Creating README.md"
echo "# ${UC_SERVICE_NAME} Service" > README.md

echo "Creating directories"
mkdir -p xos/synchronizer/model_policies/
mkdir -p xos/synchronizer/models/
mkdir -p xos/synchronizer/pull_steps/
mkdir -p xos/synchronizer/steps/
mkdir -p xos/synchronizer/tests/
mkdir -p "helm-charts/${SERVICE_NAME}/templates"

echo "Creating empty model-deps"
echo "{}" > xos/synchronizer/model-deps

echo "Creating xproto scaffold"
cat << EOF > "xos/synchronizer/models/${SERVICE_NAME}.xproto"
option app_label = "${SERVICE_NAME}";
option name = "${SERVICE_NAME}";

message ${UC_SERVICE_NAME}Service (Service){
  option verbose_name = "${UC_SERVICE_NAME} Service";
}

message ${UC_SERVICE_NAME}ServiceInstance (ServiceInstance){
  option owner_class_name = "${UC_SERVICE_NAME}Service";
  option verbose_name = "${UC_SERVICE_NAME} Service Instance";
}
EOF

echo "Creating unittest.cfg"
cat << EOF > "xos/unittest.cfg"
[unittest]
plugins=nose2.plugins.junitxml
code-directories=synchronizer
                 model_policies
                 steps
                 pull_steps
                 event_steps
EOF

echo "Creating service config.yaml"
cat << EOF > "xos/synchronizer/config.yaml"
${LICENSE_TEXT}

name: ${SERVICE_NAME}
required_models:
  - ${UC_SERVICE_NAME}Service
  - ${UC_SERVICE_NAME}ServiceInstance
dependency_graph: "/opt/xos/synchronizers/${SERVICE_NAME}/model-deps"
model_policies_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/model_policies"
models_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/models"
pull_steps_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/pull_steps"
steps_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/steps"
sys_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/sys"
EOF

echo "Creating test_config.yaml"
cat << EOF > "xos/synchronizer/test_config.yaml"
${LICENSE_TEXT}

name: ${SERVICE_NAME}-testconfig
accessor:
  username: xosadmin@opencord.org
  password: "sample"
  kind: "testframework"
logging:
  version: 1
  handlers:
    console:
      class: logging.StreamHandler
  loggers:
    'multistructlog':
      handlers:
          - console
EOF

echo "Creating synchronizer.py"
cat << EOF > "xos/synchronizer/${SERVICE_NAME}-synchronizer.py"
#!/usr/bin/env python

${LICENSE_TEXT}

"""
${SERVICE_NAME}-synchronizer.py
This is the main entrypoint for the synchronizer. It loads the config file, and
then starts the synchronizer.
"""

import importlib
import os
import sys
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/config.yaml')

base_config_file = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/config.yaml')
mounted_config_file = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/mounted_config.yaml')

if os.path.isfile(mounted_config_file):
    Config.init(base_config_file, 'synchronizer-config-schema.yaml',
                mounted_config_file)
else:
    Config.init(base_config_file, 'synchronizer-config-schema.yaml')

synchronizer_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../synchronizers/new_base")

sys.path.append(synchronizer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()
EOF

chmod +x "xos/synchronizer/${SERVICE_NAME}-synchronizer.py"

echo "Creating synchronizer Dockerfile"
cat << EOF > Dockerfile.synchronizer
${LICENSE_TEXT}

# xosproject/${SERVICE_NAME}

FROM xosproject/xos-synchronizer-base:2.0.0

COPY xos/synchronizer /opt/xos/synchronizers/${SERVICE_NAME}
COPY VERSION /opt/xos/synchronizers/${SERVICE_NAME}/

ENTRYPOINT []

WORKDIR "/opt/xos/synchronizers/${SERVICE_NAME}"

# Label image
ARG org_label_schema_schema_version=1.0
ARG org_label_schema_name=${SERVICE_NAME}
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown
ARG org_opencord_component_chameleon_version=unknown
ARG org_opencord_component_chameleon_vcs_url=unknown
ARG org_opencord_component_chameleon_vcs_ref=unknown
ARG org_opencord_component_xos_version=unknown
ARG org_opencord_component_xos_vcs_url=unknown
ARG org_opencord_component_xos_vcs_ref=unknown

LABEL org.label-schema.schema-version=\$org_label_schema_schema_version \\
      org.label-schema.name=\$org_label_schema_name \\
      org.label-schema.version=\$org_label_schema_version \\
      org.label-schema.vcs-url=\$org_label_schema_vcs_url \\
      org.label-schema.vcs-ref=\$org_label_schema_vcs_ref \\
      org.label-schema.build-date=\$org_label_schema_build_date \\
      org.opencord.vcs-commit-date=\$org_opencord_vcs_commit_date \\
      org.opencord.component.chameleon.version=\$org_opencord_component_chameleon_version \\
      org.opencord.component.chameleon.vcs-url=\$org_opencord_component_chameleon_vcs_url \\
      org.opencord.component.chameleon.vcs-ref=\$org_opencord_component_chameleon_vcs_ref \\
      org.opencord.component.xos.version=\$org_opencord_component_xos_version \\
      org.opencord.component.xos.vcs-url=\$org_opencord_component_xos_vcs_url \\
      org.opencord.component.xos.vcs-ref=\$org_opencord_component_xos_vcs_ref

CMD ["/usr/bin/python", "/opt/xos/synchronizers/${SERVICE_NAME}/${SERVICE_NAME}-synchronizer.py"]
EOF

echo "Creating sync step"
cat << EOF > "xos/synchronizer/steps/sync_${SERVICE_NAME}_serviceinstance.py"
${LICENSE_TEXT}

from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import ${UC_SERVICE_NAME}ServiceInstance

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


class Sync${UC_SERVICE_NAME}ServiceInstance(SyncStep):
    """
    Sync${UC_SERVICE_NAME}ServiceInstance
    Implements sync step for syncing ${UC_SERVICE_NAME} Services
    """

    provides = [${UC_SERVICE_NAME}ServiceInstance]
    observes = [${UC_SERVICE_NAME}ServiceInstance]
    requested_interval = 0

    def sync_record(self, model):
        log.info("Synchronizing ${UC_SERVICE_NAME}ServiceInstance",
                 object=str(model))
        # TODO: Implement sync step

        # Verify that the name is not empty, used in tests
        if model.name != "":
            model.save()
        else:
            raise Exception("Empty names aren't allowed")

    def delete_record(self, model):
        log.info("Deleting ${UC_SERVICE_NAME}ServiceInstance",
                 object=str(model))
        # TODO: Implement delete step
EOF

echo "Creating test for synchronizer of service instance"
cat << EOF > "xos/synchronizer/steps/test_sync_${SERVICE_NAME}_serviceinstance.py"
${LICENSE_TEXT}

import os
import sys
import unittest
from mock import Mock

# Hack to load synchronizer framework
test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

xos_dir = os.path.join(test_path, "../../..")

if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir = os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")

sys.path.append(xos_dir)
sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
# END Hack to load synchronizer framework


# generate model from xproto
def get_models_fn(service_name, xproto_name):
    name = os.path.join(service_name, "xos", xproto_name)
    if os.path.exists(os.path.join(services_dir, name)):
        return name
    else:
        name = os.path.join(service_name, "xos", "synchronizer", "models", xproto_name)
        if os.path.exists(os.path.join(services_dir, name)):
            return name
    raise Exception("Unable to find service=%s xproto=%s" % (service_name, xproto_name))
# END generate model from xproto


class TestSync${UC_SERVICE_NAME}ServiceInstance(unittest.TestCase):

    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))

        # Setting up the config module
        from xosconfig import Config
        config = os.path.join(test_path, "../test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor
        build_mock_modelaccessor(xos_dir, services_dir, [
            get_models_fn("${SERVICE_NAME}", "${SERVICE_NAME}.xproto"),
        ])

        from synchronizers.new_base.modelaccessor import model_accessor
        from sync_${SERVICE_NAME}_serviceinstance import Sync${UC_SERVICE_NAME}ServiceInstance
        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        self.sync_step = Sync${UC_SERVICE_NAME}ServiceInstance

        # create a mock instance instance
        self.model = Mock()
        self.model.name = "Example"

    def tearDown(self):
        self.model = None
        sys.path = self.sys_path_save

    # TODO - The following two tests are very simple, replace with more meaningful ones

    def test_save(self):
        # Tests that the model can be saved

        self.model.name = "${SERVICE_NAME}_test"
        self.sync_step().sync_record(self.model)
        self.model.save.assert_called()

    def test_sync_rejected(self):
        # Tests that an empty name raises an exception

        self.model.name = ""
        with self.assertRaises(Exception):
            self.sync_step().sync_record(self.model)


if __name__ == '__main__':
    unittest.main()
EOF

echo "Creating model policy for instance"
cat << EOF > "xos/synchronizer/model_policies/model_policy_${SERVICE_NAME}_serviceinstance.py"
${LICENSE_TEXT}

from synchronizers.new_base.policy import Policy


class ${UC_SERVICE_NAME}ServiceInstancePolicy(Policy):
    """
    ${UC_SERVICE_NAME}ServiceInstancePolicy
    Implements model policy for ${UC_SERVICE_NAME}Instance
    """

    model_name = "${UC_SERVICE_NAME}ServiceInstance"

    def handle_create(self, si):
        self.logger.debug(
            "MODEL_POLICY: enter handle_create for ${UC_SERVICE_NAME}ServiceInstance %s" %
            si.id)
        self.handle_update(si)
        # TODO: Implement creation policy, if it differs from update policy

    def handle_update(self, si):
        self.logger.debug(
            "MODEL_POLICY: enter handle_update for ${UC_SERVICE_NAME}ServiceInstance %s, valid=%s" %
            (si.id, si.valid))

        if (si.backend_code != 1):
            raise Exception(
                "MODEL_POLICY: ${UC_SERVICE_NAME}ServiceInstance %s has not been synced yet" %
                si.id)

        # TODO: Implement update policy

    def handle_delete(self, si):
        self.logger.debug(
            "MODEL_POLICY: enter handle_delete for ${UC_SERVICE_NAME}ServiceInstance %s" %
            si.id)
        # TODO: Implement delete policy
EOF

echo "Creating test for model policy of service instance"
cat << EOF > "xos/synchronizer/model_policies/test_model_policy_${SERVICE_NAME}_serviceinstance.py"
${LICENSE_TEXT}

import os
import sys
import unittest
from mock import Mock

# Hack to load synchronizer framework
test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

xos_dir = os.path.join(test_path, "../../..")

if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir = os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")

sys.path.append(xos_dir)
sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
# END Hack to load synchronizer framework


# generate model from xproto
def get_models_fn(service_name, xproto_name):
    name = os.path.join(service_name, "xos", xproto_name)
    if os.path.exists(os.path.join(services_dir, name)):
        return name
    else:
        name = os.path.join(service_name, "xos", "synchronizer", "models", xproto_name)
        if os.path.exists(os.path.join(services_dir, name)):
            return name
    raise Exception("Unable to find service=%s xproto=%s" % (service_name, xproto_name))
# END generate model from xproto


class TestModelPolicy${UC_SERVICE_NAME}ServiceInstance(unittest.TestCase):

    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))

        # Setting up the config module
        from xosconfig import Config
        config = os.path.join(test_path, "../test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor
        build_mock_modelaccessor(xos_dir, services_dir, [
            get_models_fn("${SERVICE_NAME}", "${SERVICE_NAME}.xproto"),
        ])

        from synchronizers.new_base.modelaccessor import model_accessor
        from model_policy_${SERVICE_NAME}_serviceinstance import ${UC_SERVICE_NAME}ServiceInstancePolicy
        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        # Some of the functions we call have side-effects, reset the world.
        model_accessor.reset_all_object_stores()

        self.policy = ${UC_SERVICE_NAME}ServiceInstancePolicy()
        self.si = Mock()

    def tearDown(self):
        sys.path = self.sys_path_save
        self.si = None

    def test_not_synced(self):
        self.si.valid = "awaiting"
        self.si.backend_code = 0

        with self.assertRaises(Exception) as e:
            self.policy.handle_update(self.si)

        self.assertIn("has not been synced yet", e.exception.message)

    def test_skip_update(self):
        self.si.valid = "awaiting"
        self.si.backend_code = 1

        self.policy.handle_update(self.si)


if __name__ == '__main__':
    unittest.main()
EOF


echo "Creating helm chart for service"
cat << EOF > "helm-charts/${SERVICE_NAME}/Chart.yaml"
---
${LICENSE_TEXT}

name: ${SERVICE_NAME}
version: ${SERVICE_VERSION}
EOF

cat << EOF > "helm-charts/${SERVICE_NAME}/values.yaml"
---
${LICENSE_TEXT}

nameOverride: ""
fullnameOverride: ""

${SERVICE_NAME}_synchronizerImage: "xosproject/${SERVICE_NAME}-synchronizer:{{ .Chart.Version }}"

imagePullPolicy: 'IfNotPresent'

xosAdminUser: "admin@opencord.org"
xosAdminPassword: "letmein"

affinity: {}
nodeSelector: {}
replicaCount: 1
resources: {}
tolerations: []
EOF

cat << EOF > "helm-charts/${SERVICE_NAME}/templates/_helpers.tpl"
{{/* vim: set filetype=mustache: */}}
${TPL_LICENSE_TEXT}
{{/*
Expand the name of the chart.
*/}}
{{- define "${SERVICE_NAME}.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "${SERVICE_NAME}.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- \$name := default .Chart.Name .Values.nameOverride -}}
{{- if contains \$name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name \$name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "${SERVICE_NAME}.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "${SERVICE_NAME}.serviceConfig" -}}
name: ${SERVICE_NAME}
accessor:
  username: {{ .Values.xosAdminUser | quote }}
  password: {{ .Values.xosAdminPassword | quote }}
  endpoint: xos-core:50051
required_models:
  - ${UC_SERVICE_NAME}Service
  - ${UC_SERVICE_NAME}ServiceInstance
dependency_graph: "/opt/xos/synchronizers/${SERVICE_NAME}/model-deps"
model_policies_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/model_policies"
models_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/models"
steps_dir: "/opt/xos/synchronizers/${SERVICE_NAME}/steps"
logging:
  version: 1
  handlers:
    console:
      class: logging.StreamHandler
    file:
      class: logging.handlers.RotatingFileHandler
      filename: /var/log/xos.log
      maxBytes: 10485760
      backupCount: 5
  loggers:
    'multistructlog':
      handlers:
          - console
          - file
      level: DEBUG
{{- end -}}
EOF

cat << EOF > "helm-charts/${SERVICE_NAME}/templates/_tosca.tpl"
{{/* vim: set filetype=mustache: */}}
${TPL_LICENSE_TEXT}
{{- define "${SERVICE_NAME}.serviceTosca" -}}
tosca_definitions_version: tosca_simple_yaml_1_0
description: Set up ${SERVICE_NAME} service
imports:
  - custom_types/${SERVICE_NAME}service.yaml

topology_template:
  node_templates:
    service#${SERVICE_NAME}:
      type: tosca.nodes.${UC_SERVICE_NAME}Service
      properties:
        name: ${SERVICE_NAME}
        kind: ${UC_SERVICE_NAME}
{{- end -}}
EOF

cat << EOF > "helm-charts/${SERVICE_NAME}/templates/configmap.yaml"
---
${LICENSE_TEXT}

apiVersion: v1
kind: ConfigMap
metadata:
  name: ${SERVICE_NAME}
data:
  serviceConfig: |
{{ include "${SERVICE_NAME}.serviceConfig" . | indent 4 }}
EOF

cat << EOF > "helm-charts/${SERVICE_NAME}/templates/deployment.yaml"
---
${LICENSE_TEXT}

apiVersion: apps/v1beta2
kind: Deployment
metadata:
  name: {{ template "${SERVICE_NAME}.fullname" . }}
  labels:
    app: {{ template "${SERVICE_NAME}.name" . }}
    chart: {{ template "${SERVICE_NAME}.chart" . }}
    release: {{ .Release.Name }}
    heritage: {{ .Release.Service }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ template "${SERVICE_NAME}.name" . }}
      release: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ template "${SERVICE_NAME}.name" . }}
        release: {{ .Release.Name }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: {{ tpl .Values.${SERVICE_NAME}_synchronizerImage . | quote }}
          imagePullPolicy: {{ .Values.imagePullPolicy }}
          resources:
{{ toYaml .Values.resources | indent 12 }}
          volumeMounts:
            - name: ${SERVICE_NAME}-config
              mountPath: /opt/xos/synchronizers/${SERVICE_NAME}/config.yaml
              subPath: config.yaml
            - name: certchain-volume
              mountPath: /usr/local/share/ca-certificates/local_certs.crt
              subPath: config/ca_cert_chain.pem
      volumes:
        - name: ${SERVICE_NAME}-config
          configMap:
            name: ${SERVICE_NAME}
            items:
              - key: serviceConfig
                path: config.yaml
        - name: certchain-volume
          configMap:
            name: ca-certificates
            items:
              - key: chain
                path: config/ca_cert_chain.pem
    {{- with .Values.nodeSelector }}
      nodeSelector:
{{ toYaml . | indent 8 }}
    {{- end }}
    {{- with .Values.affinity }}
      affinity:
{{ toYaml . | indent 8 }}
    {{- end }}
    {{- with .Values.tolerations }}
      tolerations:
{{ toYaml . | indent 8 }}
    {{- end }}
EOF

echo 'Done! Check the newly created service repo with service_lint.sh'
