#if [[ ! -e ./vbng-observer.py ]]; then
#    ln -s ../../xos-observer.py vbng-observer.py
#fi

export XOS_DIR=/opt/xos
python vbng-synchronizer.py  -C $XOS_DIR/synchronizers/vbng/vbng_synchronizer_config
