#! /bin/bash

display_usage() { 
    echo -e "\nUsage:\n$0 [xos-listen-port] [name] \n" 
} 

if [  $# -lt 2 ] 
then 
    display_usage
    exit 1
fi 

echo "Waiting for $2 to be onboarded"
while [[ 1 ]]; do
    STATUS=`curl 0.0.0.0:$1/api/utility/onboarding/$2/ready/ 2> /dev/null`
    if [[ "$STATUS" == "true" ]]; then
        echo "$2 is onboarded"
        exit 0
    fi
    echo -ne "."
    sleep 1
#    RUNNING_CONTAINER=`sudo docker ps|grep "xos"|awk '{print $$NF}'`
#    if [[ $RUNNING_CONTAINER == "" ]]; then
#        echo Container may have failed. check with \"make showlogs\'
#        exit 1
#    fi
done

