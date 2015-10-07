#if [[ ! -e ./hpc-backend.py ]]; then
#    ln -s ../xos-observer.py hpc-backend.py
#fi

export XOS_DIR=/opt/xos
python helloworld-observer.py  -C $XOS_DIR/observers/hello_world/helloworld_config
