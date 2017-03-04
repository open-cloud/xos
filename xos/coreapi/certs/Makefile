all: ca.crt server.crt server.key client.crt client.key

ca.key:
	openssl genrsa -passout pass:1111 -des3 -out ca.key 4096

ca.crt: ca.key
	openssl req -passin pass:1111 -new -x509 -days 365 -key ca.key -out ca.crt -subj  "/C=US/ST=CA/L=Cupertino/O=YourCompany/OU=YourApp/CN=MyRootCA"

server.key:
	openssl genrsa -passout pass:1111 -des3 -out server.key 4096

server.csr: server.key
	openssl req -passin pass:1111 -new -key server.key -out server.csr -subj  "/C=US/ST=CA/L=Cupertino/O=YourCompany/OU=YourApp/CN=xos-core.cord.lab"

server.crt: ca.crt ca.key server.csr
	openssl x509 -req -passin pass:1111 -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt
	openssl rsa -passin pass:1111 -in server.key -out server.key

client.key:
	openssl genrsa -passout pass:1111 -des3 -out client.key 4096

client.csr: client.key
	openssl req -passin pass:1111 -new -key client.key -out client.csr -subj  "/C=US/ST=CA/L=Cupertino/O=YourCompany/OU=YourApp/CN=%CLIENT-COMPUTERNAME%"

client.crt: client.csr ca.key
	openssl x509 -passin pass:1111 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt
	openssl rsa -passin pass:1111 -in client.key -out client.key