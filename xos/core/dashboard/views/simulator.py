from view_common import *

class SimulatorView(View):
    def get(self, request, **kwargs):
        sim = json.loads(file("/tmp/simulator.json","r").read())
        text = "<html><head></head><body>"
        text += "Iteration: %d<br>" % sim["iteration"]
        text += "Elapsed since report %d<br><br>" % sim["elapsed_since_report"]
        text += "<table border=1>"
        text += "<tr><th>site</th><th>trend</th><th>weight</th><th>bytes_sent</th><th>hot</th></tr>"
        for site in sim["site_load"].values():
            text += "<tr>"
            text += "<td>%s</td><td>%0.2f</td><td>%0.2f</td><td>%d</td><td>%0.2f</td>" % \
                        (site["name"], site["trend"], site["weight"], site["bytes_sent"], site["load_frac"])
            text += "</tr>"
        text += "</table>"
        text += "</body></html>"
        return HttpResponse(text)
