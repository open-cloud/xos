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

try:
    FLOW = flow_from_clientsecrets('/opt/planetstack/hpc_wizard/client_secrets.json',
                                   scope='https://www.googleapis.com/auth/bigquery')
except:
    print "exception while initializing bigquery flow"
    traceback.print_exc()
    FLOW = None

MINUTE_MS = 60*1000
HOUR_MS = 60*60*1000

# global to hold cached mappings
mappings = {}
reverse_mappings = {}

def to_number(s):
   try:
       if "." in str(s):
           return float(s)
       else:
           return int(s)
   except:
       return 0

class MappingException(Exception):
    pass

class BigQueryAnalytics:
    def __init__(self, table = "demoevents"):
        self.projectName = "vicci"
        self.tableName = table

    def reload_mapping(self):
        global mappings, reverse_mappings
        mappings[self.tableName] = json.loads(self.fetch_mapping(table=self.tableName))
        reverse_mappings[self.tableName] = {v:k for k, v in mappings[self.tableName].items()}

    def fetch_mapping(self, m=0, table="events"):
	req = 'http://cloud-scrutiny.appspot.com/command?action=get_allocations&multiplexer=%d&table=%s'% (m,table)
	resp = requests.get(req)
	if (resp.status_code==200):
		return resp.text
	else:
		raise Exception('Error accessing register allocations: %d'%resp.status_code)

    def run_query_raw(self, query):
        try:
            file("/tmp/query_log","a").write("query %s\n" % query)
        except:
            pass

        p = re.compile('%[a-zA-z_]*')

        try:
            query = p.sub(self.remap, query)
        except MappingException:
            self.reload_mapping()
            query = p.sub(self.remap, query)

        try:
            file("/tmp/query_log","a").write("remapped query %s\n" % query)
        except:
            pass

	storage = Storage('/opt/planetstack/hpc_wizard/bigquery_credentials.dat')
 	credentials = storage.get()

	if credentials is None or credentials.invalid:
		credentials = run(FLOW, storage)

	http = httplib2.Http()
	http = credentials.authorize(http)

	service = build('bigquery', 'v2', http=http)

        body = {"query": query,
                "timeoutMs": 60000}
        response = service.jobs().query(projectId=PROJECT_NUMBER, body=body).execute()

        return response

    def translate_schema(self, response):
        for field in response["schema"]["fields"]:
            field["name"] = reverse_mappings[self.tableName].get(field["name"], field["name"])

    def run_query(self, query):
        response = self.run_query_raw(query)

        fieldNames = []
        for field in response["schema"]["fields"]:
            fieldNames.append(field["name"])

        result = []
        if "rows" in response:
            for row in response["rows"]:
                this_result = {}
                for (i,column) in enumerate(row["f"]):
                    this_result[reverse_mappings[self.tableName].get(fieldNames[i],fieldNames[i])] = column["v"]
                result.append(this_result)

        return result

    """ Filter_results, groupby_results, do_computed_fields, and postprocess_results
        are all used for postprocessing queries. The idea is to do one query that
        includes the ungrouped and unfiltered data, and cache it for multiple
        consumers who will filter and group it as necessary.

        TODO: Find a more generalized source for these sorts operations. Perhaps
        put the results in SQLite and then run SQL queries against it.
    """

    def filter_results(self, rows, name, value):
        result = [row for row in rows if row.get(name)==value]
        return result

    def groupby_results(self, rows, groupBy=[], sum=[], count=[], avg=[], maxi=[]):
        new_rows = {}
        for row in rows:
            groupby_key = [row.get(k, None) for k in groupBy]

            if str(groupby_key) not in new_rows:
                new_row = {}
                for k in groupBy:
                    new_row[k] = row.get(k, None)

                new_rows[str(groupby_key)] = new_row
            else:
                new_row = new_rows[str(groupby_key)]

            for k in sum:
                new_row["sum_" + k] = new_row.get("sum_" + k, 0) + to_number(row.get(k,0))

            for k in avg:
                new_row["avg_" + k] = new_row.get("avg_" + k, 0) + to_number(row.get(k,0))
                new_row["avg_base_" + k] = new_row.get("avg_base_"+k,0) + 1

            for k in maxi:
                new_row["max_" + k] = max(new_row.get("max_" + k, 0), to_number(row.get(k,0)))

            for k in count:
                v = row.get(k,None)
                dl = new_row["distinct_" + k] = new_row.get("distinct_" + k, [])
                if (v not in dl):
                    dl.append(v)

                #new_row["count_" + k] = new_row.get("count_" + k, 0) + 1

        for row in new_rows.values():
            for k in avg:
                row["avg_" + k] = float(row["avg_" + k]) / row["avg_base_" + k]
                del row["avg_base_" + k]

            for k in count:
                new_row["count_" + k] = len(new_row.get("distinct_" + k, []))

        return new_rows.values()

    def do_computed_fields(self, rows, computed=[]):
        computedFieldNames=[]
        for row in rows:
            for k in computed:
                if "/" in k:
                    parts = k.split("/")
                    computedFieldName = "computed_" + parts[0].replace("%","")+"_div_"+parts[1].replace("%","")
                    try:
                        row[computedFieldName] = to_number(row[parts[0]]) / to_number(row[parts[1]])
                    except:
                        pass

                    if computedFieldName not in computedFieldNames:
                        computedFieldNames.append(computedFieldName)
        return (computedFieldNames, rows)

    def postprocess_results(self, rows, filter={}, groupBy=[], sum=[], count=[], avg=[], computed=[], maxi=[], maxDeltaTime=None):
        sum = [x.replace("%","") for x in sum]
        count = [x.replace("%","") for x in count]
        avg = [x.replace("%","") for x in avg]
        computed = [x.replace("%","") for x in computed]
        maxi = [x.replace("%","") for x in maxi]
        groupBy = [x.replace("%","") for x in groupBy]

        for (k,v) in filter.items():
            rows = self.filter_results(rows, k, v)

        if rows:
            if maxDeltaTime is not None:
                maxTime = max([float(row["time"]) for row in rows])
                rows = [row for row in rows if float(row["time"])>=maxTime-maxDeltaTime]

        (computedFieldNames, rows) = self.do_computed_fields(rows, computed)
        sum = sum + computedFieldNames
        rows = self.groupby_results(rows, groupBy, sum, count, avg, maxi)
        return rows

    def remap(self, match):
        if not self.tableName in mappings:
            raise MappingException("no mapping for table %s" % self.tableName)

        mapping = mappings[self.tableName]

        token = match.group()[1:]
        if token in mapping:
            return mapping[token]
        else:
            raise MappingException('unknown token %s' % token)

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

    def schema_to_cols(self, schema):
        fields = schema["fields"]

        colTypes = {"STRING": "string", "INTEGER": "number", "FLOAT": "number", "TIMESTAMP": "date"}

        cols = []
        i=0
        for field in fields:
            col = {"type": colTypes[field["type"]],
                   "id": "Col%d" % i,
                   "label": reverse_mappings[self.tableName].get(field["name"],field["name"])}
            cols.append(col)
            i=i+1

        return cols

def main():
    bq = BigQueryAnalytics()

    rows = bq.run_query("select %hostname,SUM(%bytes_sent) from [vicci.demoevents] group by %hostname")

    bq.dump_table(rows)

if __name__ == "__main__":
    main()
