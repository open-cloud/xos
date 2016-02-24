export XOS_DIR=/opt/xos
nohup python hpc-synchronizer.py  -C $XOS_DIR/synchronizers/hpc/hpc_synchronizer_config > /dev/null 2>&1 &
