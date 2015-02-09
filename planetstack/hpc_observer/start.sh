export XOS_DIR=/opt/xos
nohup python hpc-backend.py  -C $XOS_DIR/hpc_observer/hpc_observer_config > /dev/null 2>&1 &
