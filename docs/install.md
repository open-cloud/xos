# Installing XOS

This section described how to deploy XOS. It is a minimal deployment
that includes the set of micro-services that make up XOS itself, plus
optionally, an example service (a web server running in a Kubernetes pod).
For an example of how XOS is integrated into a larger system, see the
[CORD Installation Guide](https://guide.opencord.org/).

XOS runs on any version of Kubernetes (1.10 or greater), and uses the
Helm client-side tool. If you are new to Kubernetes, we recommend this [tutorial](https://kubernetes.io/docs/tutorials/) as a good place to start.

Although you are free to set up Kubernetes and Helm in whatever way
makes sense to you, the following walks through an example
installation sequence on  MacOS. It was tested on version 10.12.6.

## Prerequisites

You need to install Docker. Visit `https://docs.docker.com/docker-for-mac/install/` for instructions.

You also need to install VirtualBox. Visit `https://www.virtualbox.org/wiki/Downloads` for instructions.

The following assumes you've installed the Homebrew package manager. Visit
`https://brew.sh/` for instructions.

## Install Minikube and Kubectl

To install Minikube, run the following command:

```shell
curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.28.0/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
```
To install Kubectl, run the following command:

```shell
brew install kubectl
```

## Install Helm and Tiller

The following installs both Helm and Tiller.

```shell
brew install kubernetes-helm
```

## Bring Up a Kubernetes Cluster

Start a minikube cluster as follows. This automatically runs inside VirtualBox.

```shell
minikube start
```

To see that it's running, type

```shell
kubectl cluster-info
```

You should see something like the following

```shell
Kubernetes master is running at https://192.168.99.100:8443
KubeDNS is running at https://192.168.99.100:8443/api/v1/namespaces/kube-system/services/kube-dns:dn s/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

You can also see how the cluster is configured by looking at `~/.kube/config`.
Other tools described on this page use this configuration file to find your cluster.

If you want, you can see minikube running by looking at the VirtualBox dashboard. 
Or alternatively, you can visit the Minikube dashboard:

```shell
minikube dashboard
```

As a final setp, you need to start Tiller on the Kubernetes cluster.

```shell
helm init
```

## Download XOS Helm-Charts

The helm charts used to deploy XOS are currently bundled in the CORD
`helm-chart` repository. The rest of this section assumes all you download
this repository into directory `$SRC_DIR`.

```shell
mkdir $SRC_DIR
cd $SRC_DIR
git clone https://gerrit.opencord.org/helm-charts
cd helm-charts
```

While downloading the simple `helm-charts` repository is sufficient
for bringing up XOS, you may also want to download the XOS source
code, for example, so you can walk through the
[XOS tutorial](tutorials/basic_synchronizer.md). The easiest way to do
this uses the `repo` tool, as described [here](repo.md).

## Bring Up XOS 

To deploy `xos-core` (plus affiliated micro-services) into your 
Kubernetes cluster, execute the following from the `$SRC_DIR/helm-charts`
directory:

```shell 
helm dep update xos-core 
helm install xos-core -n xos-core 
```

You also need to start the Kafka message bus to catch event 
notifications send by the various components:

```shell 
helm repo add incubator http://storage.googleapis.com/kubernetes-charts-incubator 
helm install -f examples/kafka-single.yaml --version 0.8.8 -n cord-kafka incubator/kafka 
```

Use `kubectl get pods` to verify that all containers that implement XOS 
(and Kafka) are successfully running. You should see output that looks 
something like this:

```shell 
NAME                             READY     STATUS    RESTARTS   AGE 
cord-kafka-0                     1/1       Running   0          3m  
cord-kafka-zookeeper-0           1/1       Running   0          3m  
xos-chameleon-58c5b847d6-48jvf   1/1       Running   0          11m 
xos-core-7dc45f677b-pzhm6        1/1       Running   0          11m 
xos-db-c49549b7f-mzs4n           1/1       Running   0          11m 
xos-gui-7c96669d8c-8zkhq         1/1       Running   0          11m 
xos-tosca-7f6cf85657-gzddq       1/1       Running   0          11m 
xos-ws-5f47ff7d94-xg9f5          1/1       Running   0          11m 
```

## Bring Up Monitoring and Logging 

Although not required, we recommend that you also bring up two 
auxilary services to capture and display monitoring and logging 
information. This is done by executing the following Helm charts. 

Monitoring (once running, access [Grafana](http://docs.grafana.org/) 
Dashboard at port 31300):


```shell 
helm dep update nem-monitoring 
helm install -n nem-monitoring nem-monitoring 
```

Logging (once running, access 
[Kabana](https://www.elastic.co/guide/en/kibana/current/index.html) 
Dashboard at port 30601):

```shell 
helm dep up logging 
helm install -f examples/logging-single.yaml -n logging logging 
```

> **Note:** The `-f examples/logging-single.yaml` option says to 
> not use persistent storage, which is fine for development or demo 
> purposes, but not for operational deployments. 

## Bring Up a Service 

Optionally, you can bring up a simple service to be managed by XOS. 
This involves deploying two additional helm charts: `base-kubernetes`
and `demo-simpleexampleservice`. Again from the `$SRC_DIR/helm-charts`
directory, execute the following:

```shell 
helm dep update xos-profiles/base-kubernetes 
helm install xos-profiles/base-kubernetes -n base-kubernetes 
helm dep update xos-profiles/demo-simpleexampleservice 
helm install xos-profiles/demo-simpleexampleservice -n demo-simpleexampleservice 
```

When all the containers are successfully up and running, `kubectl get 
pod` will return output that looks something like this:


```shell 
NAME                                           READY     STATUS    RESTARTS   AGE 
base-kubernetes-kubernetes-75d68b65bc-h594m    1/1       Running     0          6m 
base-kubernetes-tosca-loader-ltdzg             0/1       Completed   4          6m 
cord-kafka-0                                   1/1       Running     1          15m 
cord-kafka-zookeeper-0                         1/1       Running     0          15m 
demo-simpleexampleservice-cc8fbfb7-s4r68       1/1       Running     0          5m 
demo-simpleexampleservice-tosca-loader-46qtg   0/1       Completed   4          5m 
xos-chameleon-58c5b847d6-rcqff                 1/1       Running     0          16m 
xos-core-7dc45f677b-27vc9                      1/1       Running     0          16m 
xos-db-c49549b7f-589n6                         1/1       Running     0          16m 
xos-gui-7c96669d8c-gcwsv                       1/1       Running     0          16m 
xos-tosca-7f6cf85657-bf276                     1/1       Running     0          16m 
xos-ws-5f47ff7d94-mpn7g                        1/1       Running     0          16m 
```

The two `tosca-loader` items with `Completed` status are jobs, as 
opposed to pods. Their job is to load TOSCA-based provisioning and 
configuration information into XOS, and so they run to complettion and 
then terminate. It is not uncommon to see them in an `Error` state as 
they retry while waiting for the corresponding services to come 
on-line. 

## Visit XOS Dashboard 

Finally, to view the XOS dashboard, run the following:

```shell 
minikube service xos-gui 
```

This will launch a window in your default browser. Administrator login 
and password are defined in `$SRC_DIR/helm-charts/xos-core/values.yaml`. 

## Next Steps 

This completes the installation process. At this point, you can either 
drill down on the internals of 
[Simple Example Service](simpleexampleservice/simple-example-service.md),
or you can work through the [XOS tutorial](tutorials/basic_synchronizer.md).
