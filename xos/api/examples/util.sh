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
