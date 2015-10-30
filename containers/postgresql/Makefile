.PHONY: build
build: ; docker build --rm -t postgres .

.PHONY: run
run: ; docker run --rm -p 5432:5432 --name postgres-server postgres

.PHONY: stop
stop: ; docker stop postgres-server

.PHONY: rm
rm: ; docker rm postgres-server

.PHONE: rmi
rmi: ; docker rmi postgres

.PHONY: backup
backupvol: ; docker run --volumes-from postgres-server -v /backup:/backup postgres tar cvf /backup/backup-postgres.tar /var/lib/postgresql

.PHONY: restore
restorevol: ; docker run --volumes-from postgres-server -v /backup:/backup postgres cd /var/lib/postgresql && tar xvf /backup/backup-postgres.tar

