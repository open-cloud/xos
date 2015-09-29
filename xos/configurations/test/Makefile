MYIP=`hostname -i`

test: common_cloudlab
	cat ../common/Dockerfile.common Dockerfile.test > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/test/Dockerfile .
	sudo docker run -d --add-host="ctl:$(MYIP)" -p 9999:8000 xos

common_cloudlab:
	make -C ../common -f Makefile.cloudlab
