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

