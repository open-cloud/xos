from bigquery_analytics import BigQueryAnalytics
import datetime
import re
import os
import sys
import time
import json
import traceback
import urllib2

if os.path.exists("/home/smbaker/projects/vicci/plstackapi/planetstack"):
    sys.path.append("/home/smbaker/projects/vicci/plstackapi/planetstack")
else:
    sys.path.append("/opt/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from django.conf import settings
from django import db
from django.db import connection
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice, Service

BLUE_LOAD=5000000
RED_LOAD=15000000

glo_cached_queries = {}

class PlanetStackAnalytics(BigQueryAnalytics):
    def __init__(self, tableName=None):
        if not tableName:
            tableName = settings.BIGQUERY_TABLE

        BigQueryAnalytics.__init__(self, tableName)

    def service_to_sliceNames(self, serviceName):
        service=Service.objects.get(name=serviceName)
        try:
            slices = service.slices.all()
        except:
            # BUG in data model -- Slice.service has related name 'service' and
            #                      it should be 'slices'
            slices = service.service.all()

        return [slice.name for slice in slices]

    def compose_query(self, slice=None, site=None, node=None, service=None, event="libvirt_heartbeat", timeBucket="60", avg=[], sum=[], count=[], computed=[], val=[], groupBy=["Time"], orderBy=["Time"], tableName=None, latest=False, maxAge=60*60):
        if tableName is None:
            tableName = self.tableName

        maxAge = maxAge * 1000
        tablePart = "[%s.%s@-%d--1]" % ("vicci", tableName, maxAge)

        fields = []
        fieldNames = []
        srcFieldNames = ["time"]

        fields.append("SEC_TO_TIMESTAMP(INTEGER(TIMESTAMP_TO_SEC(time)/%s)*%s) as Time" % (str(timeBucket),str(timeBucket)))
        #fields.append("INTEGER(TIMESTAMP_TO_SEC(time)/%s)*%s as Time" % (str(timeBucket),str(timeBucket)))

        for fieldName in avg:
            fields.append("AVG(%s) as avg_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("avg_%s" % fieldName.replace("%",""))
            srcFieldNames.append(fieldName)

        for fieldName in sum:
            fields.append("SUM(%s) as sum_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("sum_%s" % fieldName.replace("%",""))
            srcFieldNames.append(fieldName)

        for fieldName in count:
            fields.append("COUNT(distinct %s) as count_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("count_%s" % fieldName.replace("%",""))
            srcFieldNames.append(fieldName)

        for fieldName in val:
            fields.append(fieldName)
            fieldNames.append(fieldName)
            srcFieldNames.append(fieldName)

        for fieldName in computed:
            operator = "/"
            parts = fieldName.split("/")
            computedFieldName = "computed_" + parts[0].replace("%","")+"_div_"+parts[1].replace("%","")
            if len(parts)==1:
                operator = "*"
                parts = computed.split("*")
                computedFieldName = "computed_" + parts[0].replace("%","")+"_mult_"+parts[1].replace("%","")
            fields.append("SUM(%s)%sSUM(%s) as %s" % (parts[0], operator, parts[1], computedFieldName))
            fieldNames.append(computedFieldName)
            srcFieldNames.append(parts[0])
            srcFieldNames.append(parts[1])

        for fieldName in groupBy:
            if (fieldName not in ["Time"]):
                fields.append(fieldName)
                fieldNames.append(fieldName)
                srcFieldNames.append(fieldName)

        fields = ", ".join(fields)

        where = []

        if slice:
            where.append("%%slice='%s'" % slice)
        if site:
            where.append("%%site='%s'" % site)
        if node:
            where.append("%%hostname='%s'" % node)
        if event:
            where.append("event='%s'" % event)
        if service:
            sliceNames = self.service_to_sliceNames(service)
            if sliceNames:
                where.append("(" + " OR ".join(["%%slice='%s'" % sliceName for sliceName in sliceNames]) +")")

        if where:
            where = " WHERE " + " AND ".join(where)
        else:
            where =""

        if groupBy:
            groupBySub = " GROUP BY " + ",".join(groupBy + ["%hostname"])
            groupBy = " GROUP BY " + ",".join(groupBy)
        else:
            groupBySub = " GROUP BY %hostname"
            groupBy = ""

        if orderBy:
            orderBy = " ORDER BY " + ",".join(orderBy)
        else:
            orderBy = ""

        if latest:
            latestFields = ["table1.%s as %s" % (x,x) for x in srcFieldNames]
            latestFields = ", ".join(latestFields)
            tablePart = """(SELECT %s FROM %s AS table1
                            JOIN
                                (SELECT %%hostname, event, max(time) as maxtime from %s GROUP BY %%hostname, event) AS latest
                            ON
                                table1.%%hostname = latest.%%hostname AND table1.event = latest.event AND table1.time = latest.maxtime)""" % (latestFields, tablePart, tablePart)

        if computed:
            subQuery = "SELECT %%hostname, %s FROM %s" % (fields, tablePart)
            if where:
                subQuery = subQuery + where
            subQuery = subQuery + groupBySub

            sumFields = []
            for fieldName in fieldNames:
                if fieldName.startswith("avg"):
                    sumFields.append("AVG(%s) as avg_%s"%(fieldName,fieldName))
                    sumFields.append("MAX(%s) as max_%s"%(fieldName,fieldName))
                elif (fieldName.startswith("count")) or (fieldName.startswith("sum")) or (fieldName.startswith("computed")):
                    sumFields.append("SUM(%s) as sum_%s"%(fieldName,fieldName))
                else:
                    sumFields.append(fieldName)

            sumFields = ",".join(sumFields)

            query = "SELECT %s, %s FROM (%s)" % ("Time", sumFields, subQuery)
            if groupBy:
                query = query + groupBy
            if orderBy:
                query = query + orderBy
        else:
            query = "SELECT %s FROM %s" % (fields, tablePart)
            if where:
                query = query + " " + where
            if groupBy:
                query = query + groupBy
            if orderBy:
                query = query + orderBy

        return query

    def get_list_from_req(self, req, name, default=[]):
        value = req.GET.get(name, None)
        if not value:
            return default
        value=value.replace("@","%")
        return value.split(",")

    def format_result(self, format, result, query, dataSourceUrl):
        if (format == "json_dicts"):
            result = {"query": query, "rows": result, "dataSourceUrl": dataSourceUrl}
            return ("application/javascript", json.dumps(result))

        elif (format == "json_arrays"):
            new_result = []
            for row in result:
                new_row = []
                for key in sorted(row.keys()):
                    new_row.append(row[key])
                new_result.append(new_row)
                new_result = {"query": query, "rows": new_result}
            return ("application/javascript", json.dumps(new_result))

        elif (format == "html_table"):
            new_rows = []
            for row in result:
                new_row = []
                for key in sorted(row.keys()):
                    new_row.append("<TD>%s</TD>" % str(row[key]))
                new_rows.append("<TR>%s</TR>" % "".join(new_row))

            new_result = "<TABLE>%s</TABLE>" % "\n".join(new_rows)

            return ("text/html", new_result)

    def merge_datamodel_sites(self, rows, slice=None):
        """ For a query that included "site" in its groupby, merge in the
            opencloud site information.
        """

        if slice:
            try:
                slice = Slice.objects.get(name=slice)
            except:
                slice = None

        for row in rows:
            sitename = row["site"]
            try:
                model_site = Site.objects.get(name=sitename)
            except:
                # we didn't find it in the data model
                continue

            allocated_slivers = 0
            if model_site and slice:
                for sliver in slice.slivers.all():
                    if sliver.node.site == model_site:
                        allocated_slivers = allocated_slivers + 1

            row["lat"] = float(model_site.location.latitude)
            row["long"] = float(model_site.location.longitude)
            row["url"] = model_site.site_url
            row["numNodes"] = model_site.nodes.count()
            row["allocated_slivers"] = allocated_slivers

            max_cpu = row.get("max_avg_cpu", row.get("max_cpu",0))
            cpu=float(max_cpu)/100.0
            row["hotness"] = max(0.0, ((cpu*RED_LOAD) - BLUE_LOAD)/(RED_LOAD-BLUE_LOAD))

    def compose_latest_query(self, fieldNames=None, groupByFields=["%hostname", "event"]):
        """ Compose a query that returns the 'most recent' row for each (hostname, event)
            pair.
        """

        if not fieldNames:
            fieldNames = ["%hostname", "%bytes_sent", "%bytes_hit", "%healthy", "time", "event", "%site", "%elapsed", "%slice", "%cpu"]

        fields = ["table1.%s AS %s" % (x,x) for x in fieldNames]
        fields = ", ".join(fields)

        tableDesc = "%s.%s" % (self.projectName, self.tableName)

        groupByOn = ["table1.time = latest.maxtime"]
        for field in groupByFields:
            groupByOn.append("table1.%s = latest.%s" % (field, field))

        groupByOn = " AND ".join(groupByOn)
        groupByFields = ", ".join(groupByFields)

        base_query = "SELECT %s FROM [%s@-3600000--1] AS table1 JOIN (SELECT %s, max(time) as maxtime from [%s@-3600000--1] GROUP BY %s) AS latest ON %s" % \
                      (fields, tableDesc, groupByFields, tableDesc, groupByFields, groupByOn)

        return base_query

    def get_cached_query_results(self, q, wait=True):
        global glo_cached_queries

        if q in glo_cached_queries:
            if (time.time() - glo_cached_queries[q]["time"]) <= 60:
                print "using cached query"
                return glo_cached_queries[q]["rows"]

        if not wait:
            return None

        print "refreshing cached query"
        result = self.run_query(q)
        glo_cached_queries[q] = {"time": time.time(), "rows": result}

        return result

    def process_request(self, req):
        print req.GET

        tqx = req.GET.get("tqx", None)

        slice = req.GET.get("slice", None)
        site = req.GET.get("site", None)
        node = req.GET.get("node", None)
        service = req.GET.get("service", None)
        event = req.GET.get("event", "libvirt_heartbeat")

        format = req.GET.get("format", "json_dicts")

        timeBucket = int(req.GET.get("timeBucket", 60))
        avg = self.get_list_from_req(req, "avg")
        sum = self.get_list_from_req(req, "sum")
        count = self.get_list_from_req(req, "count")
        computed = self.get_list_from_req(req, "computed")
        groupBy = self.get_list_from_req(req, "groupBy", ["Time"])
        orderBy = self.get_list_from_req(req, "orderBy", ["Time"])

        maxRows = req.GET.get("maxRows", None)
        mergeDataModelSites = req.GET.get("mergeDataModelSites", None)

        maxAge = int(req.GET.get("maxAge", 60*60))

        cached = req.GET.get("cached", None)
        cachedGroupBy = self.get_list_from_req(req, "cachedGroupBy", ["doesnotexist"])

        q = self.compose_query(slice, site, node, service, event, timeBucket, avg, sum, count, computed, [], groupBy, orderBy, maxAge=maxAge)

        print q

        dataSourceUrl = "http://" + req.META["SERVER_NAME"] + ":" + req.META["SERVER_PORT"] + req.META["PATH_INFO"] + "?" + req.META["QUERY_STRING"].replace("format=","origFormat=").replace("%","%25") + "&format=charts";

        if (format=="dataSourceUrl"):
            result = {"dataSourceUrl": dataSourceUrl}
            return ("application/javascript", result)

        elif (format=="raw"):
            result = self.run_query_raw(q)
            result["dataSourceUrl"] = dataSourceUrl

            result = json.dumps(result);

            return ("application/javascript", result)

        elif (format=="nodata"):
            result = {"dataSourceUrl": dataSourceUrl, "query": q}
            result = json.dumps(result);
            return {"application/javascript", result}

        elif (format=="charts"):
            bq_result = self.run_query_raw(q)

            # cloudscrutiny code is probably better!
            table = {}
            table["cols"] = self.schema_to_cols(bq_result["schema"])
            rows = []
            if "rows" in bq_result:
                for row in bq_result["rows"]:
                    rowcols = []
                    for (colnum,col) in enumerate(row["f"]):
                        if (colnum==0):
                            dt = datetime.datetime.fromtimestamp(float(col["v"]))
                            rowcols.append({"v": 'new Date("%s")' % dt.isoformat()})
                        else:
                            try:
                                rowcols.append({"v": float(col["v"])})
                            except:
                                rowcols.append({"v": col["v"]})
                    rows.append({"c": rowcols})
            table["rows"] = rows

            if tqx:
                reqId = tqx.strip("reqId:")
            else:
                reqId = "0"

            result = {"status": "okColumnChart", "reqId": reqId, "table": table, "version": "0.6"}

            result = "google.visualization.Query.setResponse(" + json.dumps(result) + ");"

            def unquote_it(x): return x.group()[1:-1].replace('\\"', '"')

            p = re.compile(r'"new Date\(\\"[^"]*\\"\)"')
            result=p.sub(unquote_it, result)

            return ("application/javascript", result)

        else:
            if cached:
                results = self.get_cached_query_results(self.compose_latest_query())

                filter={}
                if slice:
                    filter["slice"] = slice
                if site:
                    filter["site"] = site
                if node:
                    filter["hostname"] = node
                if event:
                    filter["event"] = event

                result = self.postprocess_results(results, filter=filter, sum=sum, count=count, avg=avg, computed=computed, maxDeltaTime=120, groupBy=cachedGroupBy)
            else:
                result = self.run_query(q)

            if maxRows:
                result = result[-int(maxRows):]

            if mergeDataModelSites:
                self.merge_datamodel_sites(result)

            return self.format_result(format, result, q, dataSourceUrl)

def DoPlanetStackAnalytics(request):
    bq = PlanetStackAnalytics()
    result = bq.process_request(request)

    return result

def main():
    bq = PlanetStackAnalytics(tableName="demoevents")

    q = bq.compose_latest_query(groupByFields=["%hostname", "event", "%slice"])
    results = bq.run_query(q)

    #results = bq.postprocess_results(results,
    #                                 filter={"slice": "HyperCache"},
    #                                 groupBy=["site"],
    #                                 computed=["bytes_sent/elapsed"],
    #                                 sum=["bytes_sent", "computed_bytes_sent_div_elapsed"], avg=["cpu"],
    #                                 maxDeltaTime=60)

    results = bq.postprocess_results(results, filter={"slice": "HyperCache"}, maxi=["cpu"], count=["hostname"], computed=["bytes_sent/elapsed"], groupBy=["Time", "site"], maxDeltaTime=80)

    bq.dump_table(results)

    sys.exit(0)

    q=bq.compose_query(sum=["%bytes_sent"], avg=["%cpu"], latest=True, groupBy=["Time", "%site"])
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(avg=["%cpu","%bandwidth"], count=["%hostname"], slice="HyperCache")
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(computed=["%bytes_sent/%elapsed"])
    print
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(timeBucket=60*60, avg=["%cpu"], count=["%hostname"], computed=["%bytes_sent/%elapsed"])
    print
    print q
    bq.dump_table(bq.run_query(q))

if __name__ == "__main__":
    main()





