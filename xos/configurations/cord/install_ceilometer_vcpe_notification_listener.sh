if [ -d /usr/lib/python2.7/dist-packages/ceilometer/network/ext_services ]; then
    echo "Seems VCPE notification listeners are already enabled in ceilometer... so exiting gracefully..."
    exit 0
fi
echo "Verifying if all the required files are present"
if [ ! -f ceilometer_vcpe_notification_agent.tar.gz ];
then
    echo "File ceilometer_vcpe_notification_agent.tar.gz not found"
    exit 1
fi
echo "Copying the ceilometer vcpe notification agent files /usr/lib/python2.7/dist-packages/ceilometer"
tar -xzf ceilometer_vcpe_notification_agent.tar.gz
sudo mv ceilometer/network/ext_services /usr/lib/python2.7/dist-packages/ceilometer/network/
sudo mv ceilometer-2015.1.1.egg-info/entry_points.txt /usr/lib/python2.7/dist-packages/ceilometer-*egg-info/
echo "Restarting ceilometer-agent-notification"
sudo service ceilometer-agent-notification restart
