cd protos
make rebuild-protos
make
cd ..
source env.sh
python ./grpc_server.py
