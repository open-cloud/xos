import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from django.contrib.contenttypes.models import ContentType
from core.models import *
from hpc.models import *
from requestrouter.models import *
django.setup()
import time
import pycurl
import traceback
from StringIO import StringIO

from dnslib.dns import DNSRecord,DNSHeader,DNSQuestion,QTYPE
from dnslib.digparser import DigParser

from threading import Thread, Condition

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

        try:
            q = DNSRecord(q=DNSQuestion(domain, getattr(QTYPE,"A")))

            a_pkt = q.send(server, port, tcp=False, timeout=10)
            a = DNSRecord.parse(a_pkt)

            found_a_record = False
            for record in a.ar:
                if (record.rtype==QTYPE.A):
                    found_a_record=True

            if not found_a_record:
                job["status"] =  "%s,No A records" % domain
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
                job["status"] = "error response %d" % c.getinfo(c.RESPONSE_CODE)
                return

        except Exception, e:
            job["status"] = "Exception: %s" % str(e)
            return

        job["status"] = "success"

class HpcWatcher:
    def __init__(self):
        self.resolver_queue = WorkQueue()
        for i in range(0,10):
            DnsResolver(queue = self.resolver_queue)

        self.heartbeat_queue = WorkQueue()
        for i in range(0, 10):
            HpcHeartbeat(queue = self.heartbeat_queue)

    def set_status(self, sliver, service, kind, msg):
        #print sliver.node.name, kind, msg
        sliver.has_error = (msg!="success")

        sliver_type = ContentType.objects.get_for_model(sliver)

        t = Tag.objects.filter(service=service, name=kind+".msg", content_type__pk=sliver_type.id, object_id=sliver.id)
        if t:
            t=t[0]
            if (t.value != msg):
                t.value = msg
                t.save()
        else:
            Tag(service=service, name=kind+".msg", content_object = sliver, value=msg).save()

        t = Tag.objects.filter(service=service, name=kind+".time", content_type__pk=sliver_type.id, object_id=sliver.id)
        if t:
            t=t[0]
            t.value = str(time.time())
            t.save()
        else:
            Tag(service=service, name=kind+".time", content_object = sliver, value=str(time.time())).save()

    def check_request_routers(self, service, slivers):
        for sliver in slivers:
            sliver.has_error = False

            ip = sliver.get_public_ip()
            if not ip:
                self.set_status(sliver, service, "watcher.DNS", "no public IP")
                continue

            for domain in ["onlab.vicci.org"]:
                self.resolver_queue.submit_job({"domain": domain, "server": ip, "port": 53, "sliver": sliver})

        while self.resolver_queue.outstanding > 0:
            result = self.resolver_queue.get_result()
            sliver = result["sliver"]
            if (result["status"]!="success") and (not sliver.has_error):
                self.set_status(sliver, service, "watcher.DNS", result["status"])

        for sliver in slivers:
            if not sliver.has_error:
                self.set_status(sliver, service, "watcher.DNS", "success")

    def probe_hpc(self, service, slivers):
        for sliver in slivers:
            sliver.has_error = False

            self.heartbeat_queue.submit_job({"server": sliver.node.name, "port": 8009, "sliver": sliver})

        while self.heartbeat_queue.outstanding > 0:
            result = self.heartbeat_queue.get_result()
            sliver = result["sliver"]
            if (result["status"]!="success") and (not sliver.has_error):
                self.set_status(sliver, service, "watcher.HPC-hb", result["status"])

        for sliver in slivers:
            if not sliver.has_error:
                self.set_status(sliver, service, "watcher.HPC-hb", "success")

    def get_service_slices(self, service, kind):
        try:
            slices = service.slices.all()
        except:
            # buggy data model
            slices = service.service.all()

        return [x for x in slices if (kind in x.name)]

    def run_once(self):
        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService, "dnsdemux"):
                self.check_request_routers(hpcService, slice.slivers.all())

        for rrService in RequestRouterService.objects.all():
            for slice in self.get_service_slices(rrService, "dnsdemux"):
                self.check_request_routers(rrService, slice.slivers.all())

        for hpcService in HpcService.objects.all():
            for slice in self.get_service_slices(hpcService, "hpc"):
                self.probe_hpc(hpcService, slice.slivers.all())

    def run_loop(self):
        while True:
            self.run_once()
            time.sleep(10)

if __name__ == "__main__":
    if "--once" in sys.argv:
        HpcWatcher().run_once()
    else:
        HpcWatcher().run_loop()

