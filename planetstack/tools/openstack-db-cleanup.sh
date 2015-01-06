#! /bin/bash

# to install
#    chmod 0755 /opt/planetstack/openstack/openstack-db-cleanup.sh
#    ln -s /opt/planetstack/openstack/openstack-db-cleanup.sh /etc/cron.daily/openstack-db-cleanup.cron

mkdir -p /opt/planetstack/ovs-backups
BACKUP_NAME=/opt/planetstack/ovs-backups/backup-`date "+%Y-%M-%d"`.sql
mysqldump --create-options --routines --triggers --databases keystone ovs_quantum nova glance cinder > $BACKUP_NAME
gzip $BACKUP_NAME

mysql keystone -e "DELETE FROM token WHERE NOT DATE_SUB(CURDATE(),INTERVAL 2 DAY) <= expires;"
mysqlcheck --optimize --databases keystone ovs_quantum nova glance cinder

date >> /var/log/openstack-db-cleanup.log
mysql keystone -e "select count(*) from token;" >> /var/log/openstack-db-cleanup.log
