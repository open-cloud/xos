hpcobserver.tar.gz:
	rm -rf BUILD/hpc_observer
	mkdir -p BUILD/hpc_observer
	mkdir -p BUILD/hpc_observer/steps
	mkdir -p BUILD/hpc_observer/deleters
	cp hpclib.py hpc_observer_config run.sh start.sh  stop.sh BUILD/hpc_observer/
	cp steps/*.py BUILD/hpc_observer/steps/
	cp deleters/*.py BUILD/hpc_observer/deleters/
	mkdir -p TARS
	cd BUILD; tar -czf ../TARS/hpc_observer.tar.gz hpc_observer

upload: hpcobserver.tar.gz
	scp TARS/hpc_observer.tar.gz root@viccidev1.cs.princeton.edu:/opt/planetstack/

up_install: upload
	ssh root@viccidev1.cs.princeton.edu -C "cd /opt/planetstack; tar -xzf hpc_observer.tar.gz"
