Quick Start Notes:

1) cd protos

2) make install-protoc

3) apt-get -y install cython

4) python -m pip install grpcio grpcio-tools

5) make rebuild-protos

6) make

7) cd ..

8) source env.sh

9) python ./grpc_server.py

Note: If you don't run env.sh before running grpc_server.sh, things break.
