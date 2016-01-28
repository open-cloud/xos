# Autoscaling Application
The auto-scaling app uses monitoring data to decide when to scale a service up/down.

It is treated as an application rather than yet another
service because it offers only a GUI front-end; it is not
modelled as a service that other services can build upon.

#How to

Ensure that the CORD config is installed and then run:

`python xos_auto_scaling_app.py`

This command will start the autoscaling application and start REST server on 9991 port.

## To verify the autoscaling application:
1) Login to cloudlab compute nodes <br/>
2) On each compute node, open /etc/ceilometer/pipeline.yaml file<br/>
3) Change the polling interval for "cpu_source" meters from 600 to poll interval period that u wish (eg. 60) as shown below.<br/>
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
3b) Also ensure the publisher in "cpu_sink" contains the following URL "udp://"IP of Ceilometer PUB-SUB":5004" as shown below.<br/>
```
    - name: cpu_sink
      transformers:
          - name: "rate_of_change"
            parameters:
                target:
                    name: "cpu_util"
                    unit: "%"
                    type: "gauge"
                    scale: "100.0 / (10**9 * (resource_metadata.cpu_number or 1))"
      publishers:
          - notifier://
```

To:
```
    - name: cpu_sink
      transformers:
          - name: "rate_of_change"
            parameters:
                target:
                    name: "cpu_util"
                    unit: "%"
                    type: "gauge"
                    scale: "100.0 / (10**9 * (resource_metadata.cpu_number or 1))"
      publishers:
          - notifier://
          - udp://10.11.10.1:5004
```
4) sudo service ceilometer-agent-compute restart<br/>
5) With this change, the autoscaling application should start receiving the CPU utilization samples every 60 seconds<br/>
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
