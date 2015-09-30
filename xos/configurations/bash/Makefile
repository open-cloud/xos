MYIP:=$(shell hostname -i)

test: common_cloudlab
	cat ../common/Dockerfile.common Dockerfile.bash > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/bash/Dockerfile .
	sudo docker run -i --tty --add-host="ctl:$(MYIP)" -p 9999:8000 xos

common_cloudlab:
	make -C ../common -f Makefile.cloudlab
