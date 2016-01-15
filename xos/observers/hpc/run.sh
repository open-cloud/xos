#if [[ ! -e ./hpc-backend.py ]]; then
#    ln -s ../xos-observer.py hpc-backend.py
#fi

export XOS_DIR=/opt/xos
python hpc-observer.py  -C $XOS_DIR/observers/hpc/hpc_observer_config
