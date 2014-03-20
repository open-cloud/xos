from bigquery_analytics import BigQueryAnalytics
import json
import traceback

class PlanetStackAnalytics(BigQueryAnalytics):
    def __init__(self, tableName="demoevents"):
        BigQueryAnalytics.__init__(self, tableName)

    def compose_query(self, slice=None, site=None, node=None, timeField="MinuteTime", avg=[], sum=[], count=[], computed=[], groupBy=["MinuteTime"], orderBy=["MinuteTime"], tableName="demoevents"):
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

        fields = ", ".join(fields)

        where = []

        if slice:
            where.append("%%slice='%s'" % slice)
        if site:
            where.append("%%site='%s'" % site)
        if node:
            where.append("%%hostname='%s'" % node)

        if where:
            where = " WHERE " + " AND ".join(where)
        else:
            where =""

        if groupBy:
            groupBy = " GROUP BY " + ",".join(groupBy)
        else:
            groupBy = ""

        if orderBy:
            orderBy = " ORDER BY " + ",".join(orderBy)
        else:
            orderBy = ""

        if computed:
            subQuery = "SELECT %%hostname, %s FROM [%s]" % (fields, tablePart)
            if where:
                subQuery = subQuery + where
            subQuery = subQuery + " GROUP BY %s,%%hostname" % timeField

            sumFields = []
            for fieldName in fieldNames:
                if fieldName.startswith("avg"):
                    sumFields.append("AVG(%s) as avg_%s"%(fieldName,fieldName))
                else:
                    sumFields.append("SUM(%s) as sum_%s"%(fieldName,fieldName))

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

    def process_request(self, req):
        print req.GET

        tqx = req.GET.get("reqId", None)

        slice = req.GET.get("slice", None)
        site = req.GET.get("site", None)
        node = req.GET.get("node", None)

        format = req.GET.get("format", "json_dicts")

        timeField = req.GET.get("timeField", "MinuteTime")
        avg = self.get_list_from_req(req, "avg")
        sum = self.get_list_from_req(req, "sum")
        count = self.get_list_from_req(req, "count")
        computed = self.get_list_from_req(req, "computed")
        groupBy = self.get_list_from_req(req, "groupBy", ["MinuteTime"])
        orderBy = self.get_list_from_req(req, "orderBy", ["MinuteTime"])

        maxRows = req.GET.get("maxRows", None)

        q = self.compose_query(slice, site, node, timeField, avg, sum, count, computed, groupBy, orderBy)

        print q

        if (format=="raw"):
            result = self.run_query_raw(q)
            result["reqId"] = 0        # XXX FIXME
            return ("application/javascript", json.dumps(result))
        else:
            result = self.run_query(q)

            if maxRows:
                result = result[-int(maxRows):]

            return self.format_result(format, result, q)


def DoPlanetStackAnalytics(request):
    bq = PlanetStackAnalytics()
    result = bq.process_request(request)

    return result

def main():
    bq = PlanetStackAnalytics()

    q=bq.compose_query(avg=["%cpu"], count=["%hostname"], slice="HyperCache")
    print q
    bq.dump_table(bq.run_query(q))

    q=bq.compose_query(computed=["%bytes_sent/%elapsed"])
    print
    print q
    bq.dump_table(bq.run_query(q))
    #print bq.run_query_raw(q)

    q=bq.compose_query(timeField="HourTime", avg=["%cpu"], count=["%hostname"], computed=["%bytes_sent/%elapsed"], groupBy=["HourTime"], orderBy=["HourTime"])
    print
    print q
    bq.dump_table(bq.run_query(q))

if __name__ == "__main__":
    main()





