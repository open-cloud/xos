#if [[ ! -e ./vcpe-observer.py ]]; then
#    ln -s ../../xos-observer.py vcpe-observer.py
#fi

export XOS_DIR=/opt/xos
nohup python vcpe-observer.py  -C $XOS_DIR/observers/vcpe/vcpe_observer_config > /dev/null 2>&1 &
