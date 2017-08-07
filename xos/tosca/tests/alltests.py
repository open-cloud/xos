
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


from enginetest import EngineTest
from coarsetenancytest import CoarseTenancyTest
from porttest import PortTest
from networktest import NetworkTest
from servicetest import ServiceTest
from usertest import UserTest
from computetest import ComputeTest
from sitetest import SiteTest
from deploymenttest import DeploymentTest
from nodetest import NodeTest
from slicetest import SliceTest
from controllertest import ControllerTest
from imagetest import ImageTest

if __name__ == "__main__":
    EngineTest()
    SiteTest()
    DeploymentTest()
    ControllerTest()
    NodeTest()
    NetworkTest()
    PortTest()
    CoarseTenancyTest()
    ServiceTest()
    UserTest()
    SliceTest()
    ComputeTest()
    ImageTest()
