.PHONY: build
	build: ; docker build --rm -t xosproject/nagios .

.PHONY: run
	run: ; docker run -d --name xosproject_nagios -p 8001:80 -t xosproject/nagios

.PHONY: stop
	stop: ; docker stop xosproject_nagios

.PHONY: rm
	rm: ; docker rm xosproject_nagios

