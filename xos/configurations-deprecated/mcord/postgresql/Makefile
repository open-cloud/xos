IMAGE_NAME:=xosproject/xos-postgres
CONTAINER_NAME:=xos-db-postgres
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} .

.PHONY: run
run: ; docker run -d -p 5432:5432 --name ${CONTAINER_NAME} ${IMAGE_NAME}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}

.PHONE: rmi
rmi: ; docker rmi ${IMAGE_NAME}

.PHONY: backup
backupvol: ; docker run --volumes-from ${CONTAINER_NAME} -v /backup:/backup postgres tar cvf /backup/backup-postgres.tar /var/lib/postgresql

.PHONY: restore
restorevol: ; docker run --volumes-from ${CONTAINER_NAME} -v /backup:/backup postgres cd /var/lib/postgresql && tar xvf /backup/backup-postgres.tar

