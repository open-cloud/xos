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

# service_lint.sh
# Performs various linting tasks on a service directory

set -u -o pipefail

LINE_MAX=99

echo "Checking python code with flake8: $(flake8 --version)"
flake8 --max-line-length=${LINE_MAX}

# NOTE: not checking helm templates!
echo -n "Checking YAML with yamllint: "; yamllint --version
yamllint --strict -d "{line-length: {max: ${LINE_MAX}}}" helm-charts/*/*.yaml

echo "Checking helm charts with helm: $(helm version --client)"
helm lint --strict helm-charts/*
