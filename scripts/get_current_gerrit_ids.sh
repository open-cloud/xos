#!/usr/bin/env bash

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

# USAGE
# from the XOS folder: repo forall -c "bash $PWD/scripts/get_current_gerrit_ids.sh"

CHANGE_ID=$(git log -1 | grep Change-Id | cut -c16-)

CHANGE_NUMBER=$(curl -s https://gerrit.opencord.org/changes/$CHANGE_ID | tail -n +2 | jq ._number)

echo $(basename `pwd`):$CHANGE_NUMBER