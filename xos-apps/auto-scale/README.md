#How to

Ensure that the CORD config is installed and then run:

`python xos_auto_scaling_app.py`

This command will start the autoscaling application and start REST server on 9991 port.

## To verify the autoscaling application:
1) Login to cloudlab compute nodes
2) On each compute node, open /etc/ceilometer/pipeline.yaml file
3) Change the polling interval for "cpu_source" meters from 600 to 60 as shown below
From:
```
    - name: cpu_source
      interval: 600
      meters:
          - "cpu"
      sinks:
          - cpu_sink
```

To:
```
    - name: cpu_source
      interval: 60
      meters:
          - "cpu"
      sinks:
          - cpu_sink
```
4) sudo service ceilometer-agent-compute restart
5) With this change, the autoscaling application should start receiving the CPU utilization samples every 60 seconds
6) The REST API to retrieve the cpu utilization samples from autoscaling application: http://<app_ip>:9991/autoscaledata 

## GUI (early development stage)

To run this sample you need to have `nodejs >= 4.0` installed on your local system. You can get it [here](https://nodejs.org/en/)

- Clone the repository locally
- Open `xos-apps/auto-scale/gui/env/default` and change it to:
```
module.exports = {
  host: 'http://<your.cord.installation.ip>:9991'
}
```
- From `xos-apps/auto-scale/gui` run `npm start`