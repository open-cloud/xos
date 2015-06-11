#! /bin/bash

# put this in /opt/xerocole/start-bbs.sh
# make sure it's executable
# set it up in crontab
#   @reboot /opt/xerocole/start-bbs.sh

ulimit -n 200000
cd /opt/xerocole/answerx
/opt/xerocole/answerx/startStop checkconfig answerx
/opt/xerocole/answerx/startStop start answerx
cd /opt/xerocole/namecontrols
nohup /opt/xerocole/namecontrols/broadbandshield &
