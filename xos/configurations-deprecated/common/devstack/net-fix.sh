#!/bin/sh

PRIMARY=$( route | grep default | awk '{print $NF}' )
RULE="POSTROUTING -t nat -o $PRIMARY -s 172.24.4.0/24 -j MASQUERADE"

iptables -C $RULE || iptables -A $RULE
