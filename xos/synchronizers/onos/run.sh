#if [[ ! -e ./vcpe-observer.py ]]; then
#    ln -s ../../xos-observer.py vcpe-observer.py
#fi

export XOS_DIR=/opt/xos
python onos-synchronizer.py  -C $XOS_DIR/synchronizers/onos/onos_synchronizer_config
