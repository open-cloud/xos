#! /bin/bash
echo "Waiting for XOS to come up"
until http 0.0.0.0:80 &> /dev/null
do
    sleep 1
    RUNNING_CONTAINER=`sudo docker ps|grep "xos"|awk '{print $$NF}'`
    if [[ $RUNNING_CONTAINER == "" ]]; then
        echo Container may have failed. check with \"make showlogs\'
        exit 1
    fi
done
echo "XOS is ready"
