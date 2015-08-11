#! /bin/bash

rm -rf /tmp/tosca_install
mkdir /tmp/tosca_install
cd /tmp/tosca_install
git clone https://github.com/openstack/heat-translator.git
cd heat-translator
git reset --hard a951b93c16e54046ed2d233d814860181c772e30
rm -rf /opt/tosca
mkdir /opt/tosca
cp -a /tmp/tosca_install/heat-translator/translator /opt/tosca/
echo > /opt/tosca/translator/__init__.py
