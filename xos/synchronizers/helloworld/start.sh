export XOS_DIR=/opt/xos

echo $XOS_DIR/synchronizers/helloworld/helloworld_config
python helloworld-synchronizer.py -C $XOS_DIR/synchronizers/helloworld/helloworld_config
