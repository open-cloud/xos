#!/bin/sh

DEVSTACK_ROOT=$1

source $DEVSTACK_ROOT/openrc admin admin
echo export OS_TENANT_NAME=$OS_TENANT_NAME
echo export OS_USERNAME=$OS_USERNAME
echo export OS_PASSWORD=$OS_PASSWORD
echo export OS_AUTH_URL=$OS_AUTH_URL
