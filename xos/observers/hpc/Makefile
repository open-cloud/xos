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
