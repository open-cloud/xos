#if [[ ! -e ./vbng-observer.py ]]; then
#    ln -s ../../xos-observer.py vbng-observer.py
#fi

export XOS_DIR=/opt/xos
nohup python vbng-synchronizer.py  -C $XOS_DIR/synchronizers/vbng/vbng_synchronizer_config > /dev/null 2>&1 &
