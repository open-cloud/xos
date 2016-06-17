#! /bin/bash

display_usage() { 
    echo -e "\nUsage:\n$0 [fn] \n" 
} 

if [  $# -lt 1 ] 
then 
    display_usage
    exit 1
fi 

echo "Waiting for XOS to create file $1"

until find $1 &> /dev/null
do
    sleep 1
    echo -ne "."
    RUNNING_CONTAINER=`sudo docker ps|grep "xos"|awk '{print $$NF}'`
    if [[ $RUNNING_CONTAINER == "" ]]; then
        echo Container may have failed. check with \"make showlogs\'
        exit 1
    fi
done
echo "XOS is ready"
