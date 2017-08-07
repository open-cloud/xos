
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


echo add_subscriber
./add_subscriber.sh
echo -e "\n update_subscriber"
./update_subscriber.sh
echo -e "\n add_volt_to_subscriber"
./add_volt_to_subscriber.sh
echo -e "\n get_subscriber"
./get_subscriber.sh
echo -e "\n delete_volt_from_subscriber"
./delete_volt_from_subscriber.sh
echo -e "\n add_device_to_subscriber"
./add_device_to_subscriber.sh
echo -e "\n set_subscriber_device_feature"
./set_subscriber_device_feature.sh
echo -e "\n set_subscriber_device_identity"
./set_subscriber_device_identity.sh
echo -e "\n get_subscriber_device_feature"
./get_subscriber_device_feature.sh
echo -e "\n get_subscriber_device_identity"
./get_subscriber_device_identity.sh
echo -e "\n get_subscriber"
./get_subscriber.sh
echo -e "\n list_subscriber_devices"
./list_subscriber_devices.sh
echo -e "\n delete_subscriber_device"
./delete_subscriber_device.sh
echo -e "\n delete_subscriber"
./delete_subscriber.sh
