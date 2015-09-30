MYIP:=$(shell hostname -i)

test: common_cloudlab
	cat ../common/Dockerfile.common Dockerfile.develserver > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/develserver/Dockerfile .
	sudo docker run -d --add-host="ctl:$(MYIP)" -p 9999:8000 xos
	echo "devel server should now be running in the background..."

common_cloudlab:
	make -C ../common -f Makefile.cloudlab
