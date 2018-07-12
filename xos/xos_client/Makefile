all: chameleon_protos xosapi_install

xosapi/chameleon:
	cd xosapi ;\
	ln -s ../../../../../component/chameleon chameleon

chameleon_protos: | xosapi/chameleon
	cd xosapi/chameleon/protos; VOLTHA_BASE=anything make

xosapi_install:
	python ./setup.py install
