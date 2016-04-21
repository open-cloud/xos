export XOS_DIR=/opt/xos
cp /root/setup/node_key $XOS_DIR/synchronizers/vtr/node_key
chmod 0600 $XOS_DIR/synchronizers/vtr/node_key
python vtr-synchronizer.py  -C $XOS_DIR/synchronizers/vtr/vtn_vtr_synchronizer_config
