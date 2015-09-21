export XOS_DIR=/opt/xos

echo $XOS_DIR/observers/helloworld/helloworld_config
python helloworld-observer.py -C $XOS_DIR/observers/helloworld/helloworld_config
