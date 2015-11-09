if [ -d /usr/share/xos-metering ]; then
    echo "Seems xos ceilometer dashboard is already installed... so exiting gracefully..."
    exit 0
fi
echo "Verifying if all the required files are present"
if [ ! -f xos_metering_dashboard.tar.gz ];
then
    echo "File xos_metering_dashboard.tar.gz not found"
    exit 1
fi
if [ ! -f etc_xos_metering.tar.gz ];
then
    echo "File etc_xos_metering.tar.gz not found"
    exit 1
fi
echo "Copying the xos ceilometer dashboard files /usr/share/ and /etc/apache2/"
tar -xzf xos_metering_dashboard.tar.gz
sudo mv xos-metering /usr/share/
tar -xzf etc_xos_metering.tar.gz
sudo mv xos-metering /etc/
sudo mv apache2/conf-available/xos-metering.conf /etc/apache2/conf-available/
cd /etc/apache2/conf-enabled/
sudo ln -s ../conf-available/xos-metering.conf xos-metering.conf
echo "Restarting apache2"
sudo service apache2 restart
