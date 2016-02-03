#!/bin/sh
rm -f /usr/share/easy-rsa/vars
cp -r /usr/share/easy-rsa/* .
source vars
sh clean-all
sh build-ca --batch
cat keys/ca.crt
