#if [[ ! -e ./hpc-backend.py ]]; then
#    ln -s ../xos-observer.py hpc-backend.py
#fi

export XOS_DIR=/opt/xos
python helloworld-synchronizer.py  -C $XOS_DIR/synchronizers/helloworld/helloworld_config
