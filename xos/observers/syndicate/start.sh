export XOS_DIR=/opt/xos
nohup python syndicate-backend.py  -C $XOS_DIR/observers/syndicate/syndicate_observer_config > /dev/null 2>&1 &
