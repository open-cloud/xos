cd protos
make rebuild-protos
make
cd ..
source env.sh
python ./core_main.py
