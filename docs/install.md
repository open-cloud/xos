# Installing XOS

This section described how to deploy XOS. It is a minimal deployment
that includes the set of micro-services that make up XOS itself, plus
optionally, an example service (a web server running in a Kubernetes pod).
For an example of how XOS is integrated into a larger system, see the
[CORD Installation Guide](https://guide.opencord.org/).

XOS runs on any version of Kubernetes (1.10 or greater), and uses the
Helm client-side tool. If you are new to Kubernetes, we recommend this [tutorial](https://kubernetes.io/docs/tutorials/) as a good place to start.

Although you are free to set up Kubernetes and Helm in whatever way
makes sense for your system, the following walks you through an
example installation sequence on  MacOS. It was tested on version 10.12.6.

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
this repository into a directory named `~/xos`.

```shell
mkdir ~/xos
cd ~/xos
git clone https://gerrit.opencord.org/helm-charts
cd helm-charts
```

While downloading the simple `helm-charts` repository is sufficient
for bringing up XOS, you may also want to download the XOS source
code, for example, so you can walk through the
[XOS tutorial](tutorial/basic_synchronizer.md). The easiest way to do
this uses the `repo` tool, as described [here](repo.md).

## Bring Up XOS

To deploy `xos-core` (plus affiliated micro-services) into your
Kubernetes cluster, execute the following from the `~/xos/helm-charts`
directory:

```shell
helm dep update xos-core
helm install xos-core -n xos-core
```

Use `kubectl get pods` to verify that all containers that implement XOS
are successfully running. You should see output that looks something
like this:

```shell
NAME                                           READY     STATUS    RESTARTS   AGE
xos-chameleon-6f49b67f68-pdf6n                 1/1       Running   0          2m
xos-core-57fd788db-8b97d                       1/1       Running   0          2m
xos-db-f9ddc6589-rtrml                         1/1       Running   0          2m
xos-gui-7fcfcd4474-prhfb                       1/1       Running   0          2m
xos-redis-74c5cdc969-ppd7z                     1/1       Running   0          2m
xos-tosca-7c665f97b6-krp5k                     1/1       Running   0          2m
xos-ws-55d676c696-pxsqk                        1/1       Running   0          2m
```

## Bring Up a Service

Optionally, you can bring up a simple service to be managed by XOS.
This involves deploying two additional helm charts: `base-kubernetes`
and `demo-simpleexampleservice`. Again from the `~/xos/helm-charts`
directory, execute the following:

```shell
helm dep update xos-profiles/base-kubernetes
helm install xos-profiles/base-kubernetes -n base-kubernetes
helm dep update xos-profiles/demo-simpleexampleservice
helm install xos-profiles/demo-simpleexampleservice -n demo-simpleexampleservice
```

> **Note:** It will take some time for the various helm charts to
> deploy and the containers to come online. The `tosca-loader`
> container may error and retry several times as it waits for
> services to be dynamically loaded. This is normal, and eventually
> the `tosca-loader` will enter the completed state.

As before, when all the containers are successfully up and running,
`kubectl get pod` will return output that looks something like this:

```shell
NAME                                           READY     STATUS    RESTARTS   AGE
base-kubernetes-kubernetes-55c55bd897-rn9ln    1/1       Running   0          2m
base-kubernetes-tosca-loader-vs6pv             1/1       Running   1          2m
demo-simpleexampleservice-787454b84b-ckpn2     1/1       Running   0          1m
demo-simpleexampleservice-tosca-loader-4q7zg   1/1       Running   0          1m
xos-chameleon-6f49b67f68-pdf6n                 1/1       Running   0          12m
xos-core-57fd788db-8b97d                       1/1       Running   0          12m
xos-db-f9ddc6589-rtrml                         1/1       Running   0          12m
xos-gui-7fcfcd4474-prhfb                       1/1       Running   0          12m
xos-redis-74c5cdc969-ppd7z                     1/1       Running   0          12m
xos-tosca-7c665f97b6-krp5k                     1/1       Running   0          12m 
xos-ws-55d676c696-pxsqk                        1/1       Running   0          12m 
```

## Visit XOS Dashboard

Finally, to view the XOS dashboard, run the following:

```shell
minikube service xos-gui
```

This will launch a window in your default browser. Administrator login
and password are defined in `~/xos/helm-charts/xos-core/values.yaml`.

## Next Steps

This completes the installation process. At this point, you can
drill down on the internals of
[Simple Example Service](simpleexampleservice/simple-example-service.md).

