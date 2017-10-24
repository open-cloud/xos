
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

# Constants
OUTPUT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/out/")

TMP_TARGET_PATH = os.path.join(OUTPUT_DIR, 'tmp.xtarget')

# Store in this class the args to pass at the generator
class FakeArgs:
    pass

class XProtoTestHelpers:

    @staticmethod
    def write_tmp_target(target):
        tmp_file = open(TMP_TARGET_PATH, 'w')
        tmp_file.write(target)
        tmp_file.close()
        return TMP_TARGET_PATH

