
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


source ./config.sh

function lookup_account_num {
    ID=`curl -f -s -u $AUTH -X GET $HOST/api/tenant/cord/account_num_lookup/$1/`
    if [[ $? != 0 ]]; then
        echo "function lookup_account_num with arguments $1 failed" >&2
        echo "See CURL output below:" >&2
        curl -s -u $AUTH -X GET $HOST/api/tenant/cord/account_num_lookup/$1/ >&2
        exit -1
    fi
    # echo "(mapped account_num $1 to id $ID)" >&2
    echo $ID
}

function lookup_slice_id {
    JSON=`curl -f -s -u $AUTH -X GET $HOST/xos/slices/?name=$1`
    if [[ $? != 0 ]]; then
        echo "function lookup_slice_id with arguments $1 failed" >&2
        echo "See CURL output below:" >&2
        curl -s -u $AUTH -X GET $HOST/xos/slices/?name=$1 >&2
        exit -1
    fi
    ID=`echo $JSON | python -c "import json,sys; print json.load(sys.stdin)[0].get('id','')"`
    #echo "(mapped slice_name to id $ID)" >&2
    echo $ID
}

function lookup_subscriber_volt {
    JSON=`curl -f -s -u $AUTH -X GET $HOST/api/tenant/cord/subscriber/$1/`
    if [[ $? != 0 ]]; then
        echo "function lookup_subscriber_volt failed to read subscriber with arg $1" >&2
        echo "See CURL output below:" >&2
        curl -s -u $AUTH -X GET $HOST/api/tenant/cord/account_num_lookup/$1/ >&2
        exit -1
    fi
    ID=`echo $JSON | python -c "import json,sys; print json.load(sys.stdin)['related'].get('volt_id','')"`
    if [[ $ID == "" ]]; then
        echo "there is no volt for this subscriber" >&2
        exit -1
    fi

    # echo "(found volt id %1)" >&2

    echo $ID
}

function lookup_subscriber_vsg {
    JSON=`curl -f -s -u $AUTH -X GET $HOST/api/tenant/cord/subscriber/$1/`
    if [[ $? != 0 ]]; then
        echo "function lookup_subscriber_vsg failed to read subscriber with arg $1" >&2
        echo "See CURL output below:" >&2
        curl -s -u $AUTH -X GET $HOST/api/tenant/cord/account_num_lookup/$1/ >&2
        exit -1
    fi
    ID=`echo $JSON | python -c "import json,sys; print json.load(sys.stdin)['related'].get('vsg_id','')"`
    if [[ $ID == "" ]]; then
        echo "there is no vsg for this subscriber" >&2
        exit -1
    fi

    # echo "(found vsg id %1)" >&2

    echo $ID
}

