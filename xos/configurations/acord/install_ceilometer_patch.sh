if [ -d /usr/lib/python2.7/dist-packages/ceilometer/network/ext_services ]; then
    echo "Seems VCPE notification listeners are already enabled in ceilometer... so exiting gracefully..."
    exit 0
fi
echo "Verifying if all the required files are present"
if [ ! -f openstack_ceilometer_patch.tar.gz ] || [ ! -f ceilometer_pub_sub.tar.gz ];
then
    echo "File openstack_ceilometer_patch.tar.gz or ceilometer_pub_sub.tar.gz not found"
    exit 1
fi
echo "Copying the ceilometer patch files to /usr/lib/python2.7/dist-packages/ceilometer"
tar -xzf openstack_ceilometer_patch.tar.gz
sudo mv ceilometer/network/ext_services /usr/lib/python2.7/dist-packages/ceilometer/network/
sudo mv ceilometer/network/statistics/onos /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/
sudo mv /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/__init__.py /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/orig_init.orig_py
sudo mv ceilometer/network/statistics/__init__.py /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/
sudo mv ceilometer-2015.1.1.egg-info/entry_points.txt /usr/lib/python2.7/dist-packages/ceilometer-*egg-info/
sudo mv pipeline.yaml /etc/ceilometer/
echo "Restarting ceilometer-agent-notification"
sudo service ceilometer-agent-notification restart
echo "Restarting ceilometer-agent-central"
sudo service ceilometer-agent-central restart
tar -xzf ceilometer_pub_sub.tar.gz
echo "Starting Ceilometer PUB/SUB service"
cd ceilometer_pub_sub
python sub_main.py &
