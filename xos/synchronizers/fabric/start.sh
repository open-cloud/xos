export XOS_DIR=/opt/xos
nohup python fabric-synchronizer.py  -C $XOS_DIR/synchronizers/fabric/fabric_synchronizer_config > /dev/null 2>&1 &
