export XOS_DIR=/opt/xos
nohup python vtn-synchronizer.py  -C $XOS_DIR/observers/vtn/vtn_observer_config > /dev/null 2>&1 &
