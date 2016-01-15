#if [[ ! -e ./vcpe-observer.py ]]; then
#    ln -s ../../xos-observer.py vcpe-observer.py
#fi

export XOS_DIR=/opt/xos
python vcpe-observer.py  -C $XOS_DIR/observers/vcpe/vcpe_observer_config
