#! /bin/bash
INTERFACE=$1
tcpdump -n -e -i $INTERFACE -c 100 &
PID_TCPDUMP=$!
curl http://www.xosproject.org/ &> /dev/null &
PID_CURL=$!
sleep 30s
kill $PID_TCPDUMP
kill $PIUD_CURL
