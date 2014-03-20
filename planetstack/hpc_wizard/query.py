import re
import base64
import requests
import urllib
import json
import httplib2
import threading
import os
import time
import traceback

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow,run

"""
yum -y install python-httplib2
easy_install python_gflags
easy_install google_api_python_client
"""


PROJECT_NUMBER = '549187599759'

FLOW = flow_from_clientsecrets('/opt/planetstack/hpc_wizard/client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')

MINUTE_MS = 60*1000
HOUR_MS = 60*60*1000

class HpcQuery:
    def __init__(self):
        self.mapping = json.loads(self.fetch_mapping(table="demoevents"))
        self.reverse_mapping = {v:k for k, v in self.mapping.items()}

    def fetch_mapping(self, m=0, table="events"):
	req = 'http://cloud-scrutiny.appspot.com/command?action=get_allocations&multiplexer=%d&table=%s'% (m,table)
	resp = requests.get(req)
	if (resp.status_code==200):
		return resp.text
	else:
		raise Exception('Error accessing register allocations: %d'%resp.status_code)

    def run_query_old(self, query):
        req = 'http://cloud-scrutiny.appspot.com/command?action=send_query&q=%s' % urllib.quote(query)
	resp = requests.get(req)
	if (resp.status_code==200):
		return resp.text
	else:
		raise Exception('Error running query: %d'%resp.status_code)
        return resp

    def run_query(self, query):
	storage = Storage('/opt/planetstack/hpc_wizard/bigquery_credentials.dat')
 	credentials = storage.get()

	if credentials is None or credentials.invalid:
		credentials = run(FLOW, storage)

	http = httplib2.Http()
	http = credentials.authorize(http)

	service = build('bigquery', 'v2', http=http)

        body = {"query": query}
        response = service.jobs().query(projectId=PROJECT_NUMBER, body=body).execute()

        fieldNames = []
        for field in response["schema"]["fields"]:
            fieldNames.append(field["name"])

        result = []
        if "rows" in response:
            for row in response["rows"]:
                this_result = {}
                for (i,column) in enumerate(row["f"]):
                    this_result[self.reverse_mapping.get(fieldNames[i],fieldNames[i])] = column["v"]
                result.append(this_result)

        return result

    def remap(self, match):
        token = match.group()[1:]
        if token in self.mapping:
            return self.mapping[token]
        else:
            raise Exception('unknown token %s' % token)

    def get_usage(self, cp=None, hostname=None, site=None, slice=None, timeStart=-HOUR_MS, timeStop=-1, groupBy=["%hostname", "%cp"]):
        where = []
        if slice is not None:
            where.append("%slice='" + slice + "'")
        if cp is not None:
            where.append("%cp='" + cp + "'")
        if hostname is not None:
            where.append("%hostname='" + hostname + "'")
        if site is not None:
            where.append("%hostname contains " + site)
        where.append("%bytes_sent>0")
        where = "WHERE " + " AND ".join(where)

        if timeStart is not None:
             tableName = "[vicci.demoevents@%d-%d]" % (timeStart,timeStop)
        else:
             tableName = "[vicci.demoevents]"

        query = "SELECT %hostname,%cp,sum(%bytes_sent) as sum_bytes_sent,sum(%bytes_hit) as sum_bytes_hit, AVG(%bandwidth) as avg_bandwidth," + \
                " MAX(TIMESTAMP_TO_MSEC(time))-MIN(TIMESTAMP_TO_MSEC(time)) as time_delta FROM " + \
                tableName + " " + where

        if groupBy:
            query = query + " GROUP BY " + ",".join(groupBy)

        p = re.compile('%[a-zA-z_]*')
        query = p.sub(self.remap, query)

        rows = self.run_query(query)

        for row in rows:
            row["sum_bytes_sent"] = int(row.get("sum_bytes_sent",0))
            row["sum_bytes_hit"] = int(row.get("sum_bytes_hit",0))
            row["avg_bandwidth"] = int(float(row.get("avg_bandwidth",0)))
            row["time_delta"] = float(row.get("time_delta",0.0))/1000.0

            elapsed = (timeStop-timeStart)/1000
            KBps = int(row.get("sum_bytes_sent",0)) / elapsed / 1024
            row["KBps"] = KBps

        return rows

    def sites_from_usage(self, rows, nodes_to_sites={}):
        sites = {}
        for row in rows:
            hostname = row["hostname"]

            if hostname in nodes_to_sites:
                site_name = nodes_to_sites[hostname]
            else:
                parts = hostname.split(".")
                if len(parts)<=2:
                    continue
                site_name = parts[1]

            if not (site_name in sites):
                row = row.copy()
                row["site"] = site_name
                row["max_avg_bandwidth"] = row["avg_bandwidth"]
                # sites table doesn't care about hostnames or avg_bandwidth
                del row["hostname"]
                del row["avg_bandwidth"]
                sites[site_name] = row
            else:
                site_row = sites[site_name]
                site_row["sum_bytes_sent"] = site_row["sum_bytes_sent"] + row["sum_bytes_sent"]
                site_row["sum_bytes_hit"] = site_row["sum_bytes_hit"] + row["sum_bytes_hit"]
                site_row["max_avg_bandwidth"] = max(site_row["max_avg_bandwidth"], row["avg_bandwidth"])
                site_row["time_delta"] = max(site_row["time_delta"], row["time_delta"])

        return sites.values()

    def get_usage_sites(self, cp=None, slice=None, timeStart=-HOUR_MS, timeStop=-1):
        rows = self.get_usage(cp=cp, slice=slice, timeStart=timeStart, timeStop=timeStop)

        return self.sites_from_usage(rows)

    def dump_table(self, rows, keys=None):
        if not keys:
            keys = rows[0].keys()

        lens = {}
        for key in keys:
            lens[key] = len(key)

        for row in rows:
            for key in keys:
                thislen = len(str(row.get(key,"")))
                lens[key] = max(lens.get(key,0), thislen)

        for key in keys:
            print "%*s" % (lens[key], key),
        print

        for row in rows:
            for key in keys:
                print "%*s" % (lens[key], str(row.get(key,""))),
            print

class HpcQueryThread(HpcQuery, threading.Thread):
    def __init__(self, interval=30, slice=None, timeStart=-HOUR_MS, cp=None, nodes_to_sites={}):
        threading.Thread.__init__(self)
        HpcQuery.__init__(self)
        self.daemon = True
        self.interval = interval
        self.timeStart = timeStart
        self.nodes_to_sites = nodes_to_sites
        self.slice = slice
        self.cp = cp
        self.data_version = 0
        self.please_die = False
        self.update_time = time.time()
        self.start()

    def is_stalled(self):
        if time.time()-self.update_time > 300:
            return True
        else:
            return False

    def run(self):
        while not self.please_die:
            try:
                self.rows = self.get_usage(timeStart=self.timeStart, cp=self.cp, slice=self.slice)
                self.site_rows = self.sites_from_usage(self.rows, self.nodes_to_sites)
                self.update_time = time.time()
                self.new_data()
                self.data_version += 1
            except:
                file("/tmp/hpcquery_fail.txt","a").write(traceback.format_exc() + "\n")
            time.sleep(self.interval)

    def new_data(self):
        pass

class HpcDumpThread(HpcQueryThread):
    def __init__(self, interval=30, slice=None, timeStart=-HOUR_MS, cp=None):
        HpcQueryThread.__init__(self, interval, slice, timeStart, cp)

    def new_data(self):
        os.system("clear")

        print "update %d, data for last %d minutes" % (self.data_version, -self.timeStart/1000/60)
        print

        self.dump_table(self.rows, ["hostname", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
        print
        self.dump_table(self.site_rows, ["site", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
        print


def main_old():
    hq = HpcQuery()
#    print hq.mapping

    print "5 minute"
    hq.dump_table(hq.get_usage(timeStart=-MINUTE_MS*5), ["hostname", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    print
    hq.dump_table(hq.get_usage_sites(timeStart=-MINUTE_MS*5), ["site", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    print

    print "1 hour"
    hq.dump_table(hq.get_usage(), ["hostname", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    print
    hq.dump_table(hq.get_usage_sites(), ["site", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    print

    print "24 hours"
    hq.dump_table(hq.get_usage(timeStart=-HOUR_MS*24), ["hostname", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    hq.dump_table(hq.get_usage_sites(timeStart=-HOUR_MS*24), ["site", "cp", "sum_bytes_sent", "sum_bytes_hit", "KBps"])
    print

def main():
    hd = HpcDumpThread()
    while True:
        time.sleep(30)

if __name__ == "__main__":
    main()
