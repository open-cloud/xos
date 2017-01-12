cd protos
make rebuild-protos
make
cd ..
cd certs
make
cd ..
source env.sh
python ./grpc_server.py
