from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from services.hpc.models import *
from services.requestrouter.models import *
from django.forms import widgets
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
import json
import socket
import time

def lookup_tag(service, instance, name, default=None):
    instance_type = ContentType.objects.get_for_model(instance)
    t = Tag.objects.filter(service=service, name=name, content_type__pk=instance_type.id, object_id=instance.id)
    if t:
        return t[0].value
    else:
        return default

def lookup_time(service, instance, name):
    v = lookup_tag(service, instance, name)
    if v:
        return str(time.time() - float(v))
    else:
        return None

def json_default(d, default):
    if not d:
        return default
    return json.loads(d)

def compute_config_run(d):
    if not d:
        return "null"

    try:
        d = json.loads(d)
    except:
        return "error decoding json '%s'" % str(d)

    status = d.get("status", "null")
    if status!="success":
        return status

    config_run = d.get("config.run")
    if not config_run:
        return "null"

    try:
        config_run = max(0, int(time.time()) - int(float(config_run)))
    except:
        pass

    return config_run

# from hpc_watcher.py
def get_public_ip(service, instance):
    network_name = None
    if "hpc" in instance.slice.name:
        network_name = getattr(service, "watcher_hpc_network", None)
    elif "demux" in instance.slice.name:
        network_name = getattr(service, "watcher_dnsdemux_network", None)
    elif "redir" in instance.slice.name:
        network_name = getattr(service, "watcher_dnsredir_network", None)

    if network_name and network_name.lower()=="nat":
        return None

    if (network_name is None) or (network_name=="") or (network_name.lower()=="public"):
        return instance.get_public_ip()

    for ns in instance.ports.all():
        if (ns.ip) and (ns.network.name==network_name):
            return ns.ip

    raise ValueError("Couldn't find network %s" % str(network_name))

def getHpcDict(user, pk):
    hpc = HpcService.objects.get(pk=pk)
    slices = hpc.slices.all()

    dnsdemux_slice = None
    dnsredir_slice = None
    hpc_slice = None
    for slice in slices:
        if "dnsdemux" in slice.name:
            dnsdemux_service = hpc
            dnsdemux_slice = slice
        if "dnsredir" in slice.name:
            dnsredir_service = hpc
            dnsredir_slice = slice
        if "hpc" in slice.name:
            hpc_service = hpc
            hpc_slice = slice

    if not dnsdemux_slice:
        rr = RequestRouterService.objects.all()
        if rr:
            rr=rr[0]
            slices = rr.slices.all()
            for slice in slices:
                if "dnsdemux" in slice.name:
                    dnsdemux_service = rr
                    dnsdemux_slice = slice
                if "dnsredir" in slice.name:
                    dnsredir_service = rr
                    dnsredir_slice = slice

    if not dnsredir_slice:
        print "no dnsredir slice"
        return

    if not dnsdemux_slice:
        print "no dnsdemux slice"
        return

    #dnsdemux_has_public_network = False
    #for network in dnsdemux_slice.networks.all():
    #    if (network.template) and (network.template.visibility=="public") and (network.template.translation=="none"):
    #        dnsdemux_has_public_network = True

    nameservers = {}
    for nshc in hpc.hpchealthcheck_set.filter(kind="nameserver"):
        nameserver = nshc.resource_name
        try:
            nameservers[nameserver] = {"name": nameserver, "ip": socket.gethostbyname(nameserver), "hit": False}
        except:
            nameservers[nameserver] = {"name": nameserver, "ip": "exception", "hit": False}

    dnsdemux=[]
    for instance in dnsdemux_slice.instances.all():
        ip=None
        try:
            ip = get_public_ip(dnsdemux_service, instance)
        except Exception, e:
            ip = "Exception: " + str(e)
        if not ip:
            try:
                ip = socket.gethostbyname(instance.node.name)
            except:
                ip = "??? " + instance.node.name

        instance_nameservers = []
        for ns in nameservers.values():
            if ns["ip"]==ip:
                instance_nameservers.append(ns["name"])
                ns["hit"]=True

        # now find the dnsredir instance that is also on this node
        watcherd_dnsredir = "no-redir-instance"
        for dnsredir_instance in dnsredir_slice.instances.all():
            if dnsredir_instance.node == instance.node:
                watcherd_dnsredir = lookup_tag(dnsredir_service, dnsredir_instance, "watcher.watcher.msg")

        watcherd_dnsdemux = lookup_tag(dnsdemux_service, instance, "watcher.watcher.msg")

        dnsdemux.append( {"name": instance.node.name,
                       "watcher.DNS.msg": lookup_tag(dnsdemux_service, instance, "watcher.DNS.msg"),
                       "watcher.DNS.time": lookup_time(dnsdemux_service, instance, "watcher.DNS.time"),
                       "ip": ip,
                       "nameservers": instance_nameservers,
                       "dnsdemux_config_age": compute_config_run(watcherd_dnsdemux),
                       "dnsredir_config_age": compute_config_run(watcherd_dnsredir) })

    hpc=[]
    for instance in hpc_slice.instances.all():
        watcherd_hpc = lookup_tag(hpc_service, instance, "watcher.watcher.msg")

        hpc.append( {"name": instance.node.name,
                     "watcher.HPC-hb.msg": lookup_tag(hpc_service, instance, "watcher.HPC-hb.msg"),
                     "watcher.HPC-hb.time": lookup_time(hpc_service, instance, "watcher.HPC-hb.time"),
                     "watcher.HPC-fetch.msg": lookup_tag(hpc_service, instance, "watcher.HPC-fetch.msg"),
                     "watcher.HPC-fetch.time": lookup_time(hpc_service, instance, "watcher.HPC-fetch.time"),
                     "watcher.HPC-fetch.urls": json_default(lookup_tag(hpc_service, instance, "watcher.HPC-fetch-urls.msg"), []),
                     "config_age": compute_config_run(watcherd_hpc),

        })

    return { "id": pk,
             "dnsdemux": dnsdemux,
             "hpc": hpc,
             "nameservers": nameservers,}


class HpcList(APIView):
    method_kind = "list"
    method_name = "hpcview"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        results = []
        for hpc in HpcService.objects.all():
            results.append(getHpcDict(request.user, hpc.pk))
        return Response( results )

class HpcDetail(APIView):
    method_kind = "detail"
    method_name = "hpcview"

    def get(self, request, format=None, pk=0):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( [getHpcDict(request.user, pk)] )

