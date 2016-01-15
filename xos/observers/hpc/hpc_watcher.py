"""
    hpc_watcher.py

    Daemon to watch the health of HPC and RR instances.

    This deamon uses HpcHealthCheck objects in the Data Model to conduct
    periodic tests of HPC and RR nodes. Two types of Health Checks are
    supported:

       kind="dns": checks the request routers to make sure that a DNS
         name is resolveable and returns the right kind of records.

         resource_name should be set to the domain name to lookup.

         result_contains is option and can be used to hold "A", "CNAME", or
            a particular address or hostname that should be contained in the
            query's answer.

       kind="http": checks the hpc nodes to make sure that a URL can be
         retrieved from the node.

         resource_name should be set to the HostName:Url to fetch. For
         example, cdn-stream.htm.fiu.edu:/hft2441/intro.mp4

     In addition to the above, HPC heartbeat probes are conducted, similar to
     the ones that dnsredir conducts.

     The results of health checks are stored in a tag attached to the Instance
     the healthcheck was conducted against. If all healthchecks of a particular
     variety were successful for a instance, then "success" will be stored in
     the tag. Otherwise, the first healthcheck to fail will be stored in the
     tag.

     Ubuntu prereqs:
         apt-get install python-pycurl
         pip install dnslib
"""

import os
import socket
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from django.contrib.contenttypes.models import ContentType
from core.models import *
from services.hpc.models import *
from services.requestrouter.models import *
django.setup()
import time
import pycurl
import traceback
import json
from StringIO import StringIO

from dnslib.dns import DNSRecord,DNSHeader,DNSQuestion,QTYPE
from dnslib.digparser import DigParser

from threading import Thread, Condition

"""
from dnslib import *
q = DNSRecord(q=DNSQuestion("cdn-stream.htm.fiu.edu"))
a_pkt = q.send("150.135.65.10", tcp=False, timeout=10)
a = DNSRecord.parse(a_pkt)

from dnslib import *
q = DNSRecord(q=DNSQuestion("onlab.vicci.org"))
a_pkt = q.send("150.135.65.10", tcp=False, timeout=10)
a = DNSRecord.parse(a_pkt)
"""

class WorkQueue:
    def __init__(self):
        self.job_cv = Condition()
        self.jobs = []
        self.result_cv = Condition()
        self.results = []
        self.outstanding = 0

    def get_job(self):
        self.job_cv.acquire()
        while not self.jobs:
            self.job_cv.wait()
        result = self.jobs.pop()
        self.job_cv.release()
        return result

    def submit_job(self, job):
        self.job_cv.acquire()
        self.jobs.append(job)
        self.job_cv.notify()
        self.job_cv.release()
        self.outstanding = self.outstanding + 1

    def get_result(self):
        self.result_cv.acquire()
        while not self.results:
            self.result_cv.wait()
        result = self.results.pop()
        self.result_cv.release()
        self.outstanding = self.outstanding - 1
        return result

    def submit_result(self, result):
        self.result_cv.acquire()
        self.results.append(result)
        self.result_cv.notify()
        self.result_cv.release()

class DnsResolver(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            job = self.queue.get_job()
            self.handle_job(job)
            self.queue.submit_result(job)

    def handle_job(self, job):
        domain = job["domain"]
        server = job["server"]
        port = job["port"]
        result_contains = job.get("result_contains", None)

        try:
            q = DNSRecord(q=DNSQuestion(domain)) #, getattr(QTYPE,"A")))

            a_pkt = q.send(server, port, tcp=False, timeout=10)
            a = DNSRecord.parse(a_pkt)

            found_record = False
            for record in a.rr:
                if (not result_contains):
                    QTYPE_A = getattr(QTYPE,"A")
                    QTYPE_CNAME = getattr(QTYPE, "CNAME")
                    if ((record.rtype==QTYPE_A) or (record.qtype==QTYPE_CNAME)):
                        found_record = True
                else:
                    tmp = QTYPE.get(record.rtype) + str(record.rdata)
                    if (result_contains in tmp):
                        found_record = True

            if not found_record:
                if result_contains:
                    job["status"] =  "%s,No %s records" % (domain, result_contains)
                else:
                    job["status"] =  "%s,No A or CNAME records" % domain

                return

        except Exception, e:
            job["status"] = "%s,Exception: %s" % (domain, str(e))
            return

        job["status"] = "success"

class HpcHeartbeat(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            job = self.queue.get_job()
            self.handle_job(job)
            self.queue.submit_result(job)

    def curl_error_message(self, e):
        if e.args[0] == 6:
            return "couldn't resolve host"
        if e.args[0] == 7:
            return "failed to connect"
        return "curl error %d" % e.args[0]

    def handle_job(self, job):
        server = job["server"]
        port = job["port"]

        try:
            buffer = StringIO()
            c = pycurl.Curl()

            c.setopt(c.URL, "http://%s:%s/heartbeat" % (server, port))
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.HTTPHEADER, ['host: hpc-heartbeat', 'X-heartbeat: 1'])
            c.setopt(c.TIMEOUT, 10)
            c.setopt(c.CONNECTTIMEOUT, 10)
            c.setopt(c.NOSIGNAL, 1)

            try:
                c.perform()
                response_code = c.getinfo(c.RESPONSE_CODE)
            except Exception, e:
                #traceback.print_exc()
                job["status"] = self.curl_error_message(e)
                return
            finally:
                c.close()

            if response_code != 200:
                job["status"] = "error response %d" % response_code
                return

        except Exception, e:
            job["status"] = "Exception: %s" % str(e)
            return

        job["status"] = "success"

class HpcFetchUrl(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            job = self.queue.get_job()
            self.handle_job(job)
            self.queue.submit_result(job)

    def curl_error_message(self, e):
        if e.args[0] == 6:
            return "couldn't resolve host"
        if e.args[0] == 7:
            return "failed to connect"
        return "curl error %d" % e.args[0]

    def handle_job(self, job):
        server = job["server"]
        port = job["port"]
        url = job["url"]
        domain = job["domain"]

        def progress(download_t, download_d, upload_t, upload_d):
            # limit download size to a megabyte
            if (download_d > 1024*1024):
                return 1
            else:
                return 0

        try:
            buffer = StringIO()
            c = pycurl.Curl()

            c.setopt(c.URL, "http://%s:%s/%s" % (server, port, url))
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.HTTPHEADER, ['host: ' + domain])
            c.setopt(c.TIMEOUT, 10)
            c.setopt(c.CONNECTTIMEOUT, 10)
            c.setopt(c.NOSIGNAL, 1)
            c.setopt(c.NOPROGRESS, 0)
            c.setopt(c.PROGRESSFUNCTION, progress)

            try:
                try:
                    c.perform()
                except Exception, e:
                    # prevent callback abort from raising exception
                    if (e.args[0] != pycurl.E_ABORTED_BY_CALLBACK):
                        raise
                response_code = c.getinfo(c.RESPONSE_CODE)
                bytes_downloaded = int(c.getinfo(c.SIZE_DOWNLOAD))
                total_time = float(c.getinfo(c.TOTAL_TIME))
            except Exception, e:
                #traceback.print_exc()
                job["status"] = self.curl_error_message(e)
                return
            finally:
                c.close()

            if response_code != 200:
                job["status"] = "error response %s" %  str(response_code)
                return

        except Exception, e:
            #traceback.print_exc()
            job["status"] = "Exception: %s" % str(e)
            return

        job["status"] = "success"
        job["bytes_downloaded"] = bytes_downloaded
        job["total_time"] = total_time

class WatcherWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            job = self.queue.get_job()
            self.handle_job(job)
            self.queue.submit_result(job)

    def curl_error_message(self, e):
        if e.args[0] == 6:
            return "couldn't resolve host"
        if e.args[0] == 7:
            return "failed to connect"
        return "curl error %d" % e.args[0]

    def handle_job(self, job):
        server = job["server"]
        port = job["port"]

        try:
            buffer = StringIO()
            c = pycurl.Curl()

            c.setopt(c.URL, "http://%s:%s/" % (server, port))
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.TIMEOUT, 10)
            c.setopt(c.CONNECTTIMEOUT, 10)
            c.setopt(c.NOSIGNAL, 1)

            try:
                c.perform()
                response_code = c.getinfo(c.RESPONSE_CODE)
            except Exception, e:
                #traceback.print_exc()
                job["status"] = json.dumps( {"status": self.curl_error_message(e)} )
                return
            finally:
                c.close()

            if response_code != 200:
                job["status"] = json.dumps( {"status": "error response %d" % response_code} )
                return

            d = json.loads(buffer.getvalue())
            d["status"] = "success";
            job["status"] = json.dumps(d)

        except Exception, e:
            job["status"] = json.dumps( {"status": "Exception: %s" % str(e)} )
            return

class BaseWatcher(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def get_public_ip(self, service, instance):
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

    def set_status(self, instance, service, kind, msg, check_error=True):
        #print instance.node.name, kind, msg
        if check_error:
            instance.has_error = (msg!="success")

        instance_type = ContentType.objects.get_for_model(instance)

        t = Tag.objects.filter(service=service, name=kind+".msg", content_type__pk=instance_type.id, object_id=instance.id)
        if t:
            t=t[0]
            if (t.value != msg):
                t.value = msg
                t.save()
        else:
            Tag(service=service, name=kind+".msg", content_object = instance, value=msg).save()

        t = Tag.objects.filter(service=service, name=kind+".time", content_type__pk=instance_type.id, object_id=instance.id)
        if t:
            t=t[0]
            t.value = str(time.time())
            t.save()
        else:
            Tag(service=service, name=kind+".time", content_object = instance, value=str(time.time())).save()

    def get_service_slices(self, service, kind=None):
        try:
            slices = service.slices.all()
        except:
            # buggy data model
            slices = service.service.all()

        if kind:
            return [x for x in slices if (kind in x.name)]
        else:
            return list(slices)

class RRWatcher(BaseWatcher):
    def __init__(self):
        BaseWatcher.__init__(self)

        self.resolver_queue = WorkQueue()
        for i in range(0,10):
            DnsResolver(queue = self.resolver_queue)

    def check_request_routers(self, service, instances):
        for instance in instances:
            instance.has_error = False

            try:
                ip = self.get_public_ip(service, instance)
            except Exception, e:
                self.set_status(instance, service, "watcher.DNS", "exception: %s" % str(e))
                continue
            if not ip:
                try:
                    ip = socket.gethostbyname(instance.node.name)
                except:
                    self.set_status(instance, service, "watcher.DNS", "dns resolution failure")
                    continue

            if not ip:
                self.set_status(instance, service, "watcher.DNS", "no IP address")
                continue

            checks = HpcHealthCheck.objects.filter(kind="dns")
            if not checks:
                self.set_status(instance, service, "watcher.DNS", "no DNS HealthCheck tests configured")

            for check in checks:
                self.resolver_queue.submit_job({"domain": check.resource_name, "server": ip, "port": 53, "instance": instance, "result_contains": check.result_contains})

        while self.resolver_queue.outstanding > 0:
            result = self.resolver_queue.get_result()
            instance = result["instance"]
            if (result["status"]!="success") and (not instance.has_error):
                self.set_status(instance, service, "watcher.DNS", result["status"])

        for instance in instances:
            if not instance.has_error:
                self.set_status(instance, service, "watcher.DNS", "success")

    def run_once(self):
        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService, "dnsdemux"):
                self.check_request_routers(hpcService, slice.instances.all())

        for rrService in RequestRouterService.objects.all():
            for slice in self.get_service_slices(rrService, "dnsdemux"):
                self.check_request_routers(rrService, slice.instances.all())

    def run(self):
        while True:
            self.run_once()
            time.sleep(10)

            django.db.reset_queries()

class HpcProber(BaseWatcher):
    def __init__(self):
        BaseWatcher.__init__(self)

        self.heartbeat_queue = WorkQueue()
        for i in range(0, 10):
            HpcHeartbeat(queue = self.heartbeat_queue)

    def probe_hpc(self, service, instances):
        for instance in instances:
            instance.has_error = False

            self.heartbeat_queue.submit_job({"server": instance.node.name, "port": 8009, "instance": instance})

        while self.heartbeat_queue.outstanding > 0:
            result = self.heartbeat_queue.get_result()
            instance = result["instance"]
            if (result["status"]!="success") and (not instance.has_error):
                self.set_status(instance, service, "watcher.HPC-hb", result["status"])

        for instance in instances:
            if not instance.has_error:
                self.set_status(instance, service, "watcher.HPC-hb", "success")

    def run_once(self):
        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService, "hpc"):
                self.probe_hpc(hpcService, slice.instances.all())

    def run(self):
        while True:
            self.run_once()
            time.sleep(10)

            django.db.reset_queries()

class HpcFetcher(BaseWatcher):
    def __init__(self):
        BaseWatcher.__init__(self)

        self.fetch_queue = WorkQueue()
        for i in range(0, 10):
            HpcFetchUrl(queue = self.fetch_queue)

    def fetch_hpc(self, service, instances):
        for instance in instances:
            instance.has_error = False
            instance.url_status = []

            checks = HpcHealthCheck.objects.filter(kind="http")
            if not checks:
                self.set_status(instance, service, "watcher.HPC-fetch", "no HTTP HealthCheck tests configured")

            for check in checks:
                if (not check.resource_name) or (":" not in check.resource_name):
                    self.set_status(instance, service, "watcher.HPC-fetch", "malformed resource_name: " + str(check.resource_name))
                    break

                (domain, url) = check.resource_name.split(":",1)

                self.fetch_queue.submit_job({"server": instance.node.name, "port": 80, "instance": instance, "domain": domain, "url": url})

        while self.fetch_queue.outstanding > 0:
            result = self.fetch_queue.get_result()
            instance = result["instance"]
            if (result["status"] == "success"):
                instance.url_status.append( (result["domain"] + result["url"], "success", result["bytes_downloaded"], result["total_time"]) )
            if (result["status"]!="success") and (not instance.has_error):
                self.set_status(instance, service, "watcher.HPC-fetch", result["status"])

        for instance in instances:
            self.set_status(instance, service, "watcher.HPC-fetch-urls", json.dumps(instance.url_status), check_error=False)
            if not instance.has_error:
                self.set_status(instance, service, "watcher.HPC-fetch", "success")

    def run_once(self):
        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService, "hpc"):
                try:
                    self.fetch_hpc(hpcService, slice.instances.all())
                except:
                    traceback.print_exc()

    def run(self):
        while True:
            self.run_once()
            time.sleep(10)

            django.db.reset_queries()

class WatcherFetcher(BaseWatcher):
    def __init__(self):
        BaseWatcher.__init__(self)

        self.fetch_queue = WorkQueue()
        for i in range(0, 10):
             WatcherWorker(queue = self.fetch_queue)

    def fetch_watcher(self, service, instances):
        for instance in instances:
            try:
                ip = self.get_public_ip(service, instance)
            except Exception, e:
                self.set_status(instance, service, "watcher.watcher", json.dumps({"status": "exception: %s" % str(e)}) )
                continue
            if not ip:
                try:
                    ip = socket.gethostbyname(instance.node.name)
                except:
                    self.set_status(instance, service, "watcher.watcher", json.dumps({"status": "dns resolution failure"}) )
                    continue

            if not ip:
                self.set_status(instance, service, "watcher.watcher", json.dumps({"status": "no IP address"}) )
                continue

            port = 8015
            if ("redir" in instance.slice.name):
                port = 8016
            elif ("demux" in instance.slice.name):
                port = 8017

            self.fetch_queue.submit_job({"server": ip, "port": port, "instance": instance})

        while self.fetch_queue.outstanding > 0:
            result = self.fetch_queue.get_result()
            instance = result["instance"]
            self.set_status(instance, service, "watcher.watcher", result["status"])

    def run_once(self):
        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService):
                self.fetch_watcher(hpcService, slice.instances.all())

    def run(self):
        while True:
            self.run_once()
            time.sleep(10)

            django.db.reset_queries()


if __name__ == "__main__":
    if "--once" in sys.argv:
        RRWatcher().run_once()
        HpcProber().run_once()
        HpcFetcher().run_once()
        WatcherFetcher().run_once()
    else:
        RRWatcher().start()
        HpcProber().start()
        HpcFetcher().start()
        WatcherFetcher().start()

        print "Running forever..."
        while True:
            time.sleep(60)

