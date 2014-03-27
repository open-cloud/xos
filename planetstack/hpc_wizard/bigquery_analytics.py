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
        p = re.compile('%[a-zA-z_]*')

        try:
            query = p.sub(self.remap, query)
        except MappingException:
            self.reload_mapping()
            query = p.sub(self.remap, query)

	storage = Storage('/opt/planetstack/hpc_wizard/bigquery_credentials.dat')
 	credentials = storage.get()

	if credentials is None or credentials.invalid:
		credentials = run(FLOW, storage)

	http = httplib2.Http()
	http = credentials.authorize(http)

	service = build('bigquery', 'v2', http=http)

        body = {"query": query,
                "timeoutMs": 30000}
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
