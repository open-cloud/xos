from bigquery_analytics import BigQueryAnalytics
import os
import sys
import json
import traceback

if os.path.exists("/home/smbaker/projects/vicci/plstackapi/planetstack"):
    sys.path.append("/home/smbaker/projects/vicci/plstackapi/planetstack")
else:
    sys.path.append("/opt/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from django import db
from django.db import connection
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice, Service

BLUE_LOAD=5000000
RED_LOAD=15000000

class PlanetStackAnalytics(BigQueryAnalytics):
    def __init__(self, tableName="demoevents"):
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

    def compose_query(self, slice=None, site=None, node=None, service=None, timeField="MinuteTime", avg=[], sum=[], count=[], computed=[], groupBy=["MinuteTime"], orderBy=["MinuteTime"], tableName="demoevents"):
        tablePart = "%s.%s@-3600000--1" % ("vicci", tableName)

        fields = []
        fieldNames = []

        if (timeField=="MinuteTime"):
            fields.append("INTEGER(TIMESTAMP_TO_SEC(time)/60)*60 as MinuteTime")
        elif (timeField=="HourTime"):
            fields.append("INTEGER(TIMESTAMP_TO_SEC(time)/60/60)*60*60 as HourTime")
        elif (timeField=="DayTime"):
            fields.append("INTEGER(TIMESTAMP_TO_SEC(time)/60/60/24)*60*60*24 as DayTime")

        for fieldName in avg:
            fields.append("AVG(%s) as avg_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("avg_%s" % fieldName.replace("%",""))

        for fieldName in sum:
            fields.append("SUM(%s) as sum_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("sum_%s" % fieldName.replace("%",""))

        for fieldName in count:
            fields.append("COUNT(distinct %s) as count_%s" % (fieldName, fieldName.replace("%","")))
            fieldNames.append("count_%s" % fieldName.replace("%",""))

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

        for fieldName in groupBy:
            if (fieldName not in ["MinuteTime", "HourTime", "DayTime"]):
                fields.append(fieldName)
                fieldNames.append(fieldName)

        fields = ", ".join(fields)

        where = []

        if slice:
            where.append("%%slice='%s'" % slice)
        if site:
            where.append("%%site='%s'" % site)
        if node:
            where.append("%%hostname='%s'" % node)
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

        if computed:
            subQuery = "SELECT %%hostname, %s FROM [%s]" % (fields, tablePart)
            if where:
                subQuery = subQuery + where
            subQuery = subQuery + groupBySub
            #subQuery = subQuery + " GROUP BY %s,%%hostname" % timeField

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

            query = "SELECT %s, %s FROM (%s)" % (timeField, sumFields, subQuery)
            if groupBy:
                query = query + groupBy
            if orderBy:
                query = query + orderBy
        else:
            query = "SELECT %s FROM [%s]" % (fields, tablePart)
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
        return value.split(",")

    def format_result(self, format, result, query):
        if (format == "json_dicts"):
            result = {"query": query, "rows": result}
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

        elif (format == "json_hpcdash"):
            new_rows = {}
            for row in result:
                new_row = {"lat": float(row.get("lat", 0)),
                           "long": float(row.get("long", 0)),
                           "health": 0,
                           "numNodes": int(row.get("numNodes",0)),
                           "numHPCSlivers": int(row.get("sum_count_hostname", 0)),
                           "siteUrl": row.get("url", ""),
                           "hot": float(row.get("hotness", 0.0)),
                           "load": int(float(row.get("max_avg_cpu", 0)))}
                new_rows[row["site"]] = new_row
            return ("application/javascript", json.dumps(new_rows))

    def only_largest(self, rows, fieldName):
        """ Given a fieldName, only return the set of rows that had the
            maximum value of that fieldName.
        """
        maxVal = max( [int(row[fieldName]) for row in rows] )
        new_rows = [row for row in rows if int(row[fieldName])==maxVal]
        return new_rows

    def merge_datamodel_sites(self, rows):
        """ For a query that included "site" in its groupby, merge in the
            opencloud site information.
        """
        for row in rows:
            sitename = row["site"]
            try:
                model_site = Site.objects.get(name=sitename)
            except:
                # we didn't find it in the data model
                continue

            row["lat"] = float(model_site.location.latitude)
            row["long"] = float(model_site.location.longitude)
            row["url"] = model_site.site_url
            row["numNodes"] = model_site.nodes.count()

            if "max_avg_cpu" in row:
                cpu=float(row["max_avg_cpu"])/100.0
                row["hotness"] = max(0.0, ((cpu*RED_LOAD) - BLUE_LOAD)/(RED_LOAD-BLUE_LOAD))

    def process_request(self, req):
        print req.GET

        tqx = req.GET.get("reqId", None)

        slice = req.GET.get("slice", None)
        site = req.GET.get("site", None)
        node = req.GET.get("node", None)
        service = req.GET.get("service", None)

        format = req.GET.get("format", "json_dicts")

        timeField = req.GET.get("timeField", "MinuteTime")
        avg = self.get_list_from_req(req, "avg")
        sum = self.get_list_from_req(req, "sum")
        count = self.get_list_from_req(req, "count")
        computed = self.get_list_from_req(req, "computed")
        groupBy = self.get_list_from_req(req, "groupBy", ["MinuteTime"])
        orderBy = self.get_list_from_req(req, "orderBy", ["MinuteTime"])

        maxRows = req.GET.get("maxRows", None)
        onlyLargest = req.GET.get("onlyLargest", None)
        mergeDataModelSites = req.GET.get("mergeDataModelSites", None)

        q = self.compose_query(slice, site, node, service, timeField, avg, sum, count, computed, groupBy, orderBy)

        print q

        if (format=="raw"):
            result = self.run_query_raw(q)
            result["reqId"] = 0        # XXX FIXME
            return ("application/javascript", json.dumps(result))
        else:
            result = self.run_query(q)

            if onlyLargest:
                result = self.only_largest(result, onlyLargest)

            if mergeDataModelSites:
                self.merge_datamodel_sites(result)

            if maxRows:
                result = result[-int(maxRows):]

            return self.format_result(format, result, q)


def DoPlanetStackAnalytics(request):
    bq = PlanetStackAnalytics()
    result = bq.process_request(request)

    return result

def main():
    bq = PlanetStackAnalytics()

    """
    q=bq.compose_query(avg=["%cpu"], count=["%hostname"], slice="HyperCache")
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(computed=["%bytes_sent/%elapsed"])
    print
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(timeField="HourTime", avg=["%cpu"], count=["%hostname"], computed=["%bytes_sent/%elapsed"], groupBy=["HourTime"], orderBy=["HourTime"])
    print
    print q
    bq.dump_table(bq.run_query(q))
    """

    q=bq.compose_query(avg=["%cpu"], count=["%hostname"], computed=["%bytes_sent/%elapsed"], service="HPC Service", groupBy=["MinuteTime","%site"])
    print
    print q
    result=bq.run_query(q)
    result = bq.only_largest(result, "MinuteTime")
    bq.merge_datamodel_sites(result)
    #bq.dump_table(result)
    print bq.format_result("json_hpcdash", result, q)

if __name__ == "__main__":
    main()





