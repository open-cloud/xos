export XOS_DIR=/opt/xos
nohup python vnfm-synchronizer.py  -C $XOS_DIR/synchronizers/vnfm/vnfm_synchronizer_config > /dev/null 2>&1 &
