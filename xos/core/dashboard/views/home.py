from view_common import *
from django.http import HttpResponseRedirect
import sys


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class LoggedInView(TemplateView):
    def get(self, request, name="root", *args, **kwargs):
        if request.user.login_page:
            return HttpResponseRedirect(request.user.login_page)
        else:
            return HttpResponseRedirect("/admin/")


class DashboardDynamicView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    head_wholePage_template = r"""{% extends "admin/wholePage.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context = getDashboardContext(request.user, context)

        if name == "root":
            # maybe it is a bit hacky, didn't want to mess up everything @teone
            user_dashboards = request.user.get_dashboards()
            first_dasboard_name = user_dashboards[0].id
            return self.singleDashboardView(request, first_dasboard_name, context)
            # return self.multiDashboardView(request, context)
        elif kwargs.get("wholePage", None):
            return self.singleFullView(request, name, context)
        else:
            return self.singleDashboardView(request, name, context)

    def readTemplate(self, fn):
        TEMPLATE_DIRS = [XOS_DIR + "/templates/admin/dashboard/",
                         XOS_DIR + "/core/xoslib/dashboards/"]

        for template_dir in TEMPLATE_DIRS:
            pathname = os.path.join(template_dir, fn) + ".html"
            if os.path.exists(pathname):
                break
        else:
            return "failed to find %s in %s" % (fn, TEMPLATE_DIRS)

        template = open(pathname, "r").read()
        if (fn == "tenant"):
            # fix for tenant view - it writes html to a div called tabs-5
            template = '<div id="tabs-5"></div>' + template
        return template

    def embedDashboardUrl(self, url):
        if url.startswith("template:"):
            fn = url[9:]
            return self.readTemplate(fn)
        elif url.startswith("http"):
            return '<iframe src="%s" width="100%%" height="100%%" style="min-height: 1024px;" frameBorder="0"></iframe>' % url
        else:
            return "don't know how to load dashboard %s" % url

    def embedDashboardView(self, view, i=0):
        body = ""
        url = view.url
        if (view.controllers.all().count() > 0):
            body = body + 'Controller: <select id="dashselect-%d">' % i
            body = body + '<option value="None">(select a controller)</option>'
            for j, controllerdashboard in enumerate(view.controllerdashboardviews.all()):
                body = body + '<option value="%d">%s</option>' % (j, controllerdashboard.controller.name)
            body = body + '</select><hr>'

            for j, controllerdashboard in enumerate(view.controllerdashboardviews.all()):
                body = body + '<script type="text/template" id="dashtemplate-%d-%d">\n%s\n</script>\n' % (i,j, self.embedDashboardUrl(controllerdashboard.url));

            body = body + '<div id="dashcontent-%d" class="dashcontent"></div>\n' % i

            body = body + """<script>
                             $("#dashselect-%d").change(function() {
                                 v=$("#dashselect-%d").val();
                                 if (v=="None") {
                                     $("#dashcontent-%d").html("");
                                     return;
                                 }
                                 $("#dashcontent-%d").html( $("#dashtemplate-%d-" + v).html() );
                             });
                             //$("#dashcontent-%d").html( $("#dashtemplate-%d-0").html() );
                             </script>
                          """ % (i, i, i, i, i, i, i)
        else:
            body = body + self.embedDashboardUrl(url)
        return body

    def multiDashboardView(self, request, context):
        head_template = self.head_template
        tail_template = self.tail_template

        dashboards = request.user.get_dashboards()

        if not request.user.is_appuser:
            # customize is a special dashboard they always get
            customize = DashboardView.objects.filter(name="Customize")
            if customize:
                dashboards.append(customize[0])

        tabs = []
        bodies = []

        i = 0
        for view in dashboards:
            # don't display disabled dashboards
            if (not view.enabled):
                continue

            tabs.append('<li><a href="#dashtab-%d">%s</a></li>\n' % (i, view.name))
            body = '<div id="dashtab-%d">%s</div>\n' % (i, self.embedDashboardView(view, i))

            bodies.append(body)
            i = i + 1

        # embed content provider dashboards
        for cp in ContentProvider.objects.all():
            if request.user in cp.users.all():
                tabs.append('<li><a href="#dashtab-%d">%s</a></li>\n' % (i, cp.name))

                body = ""
                body = body + '<div id="dashtab-%d">\n' % i
                body = body + self.embedDashboardUrl("http:/admin/hpc/contentprovider/%s/%s/embeddedfilteredchange" % (cp.serviceProvider.hpcService.id, cp.id))
                body = body + '</div>\n'

                bodies.append(body)
                i = i + 1

        if (len(tabs) == 1) and (len(bodies) == 1):
            # there is only one dashboard, so optimize out the tabbing
            contents = bodies[0]
        else:
            contents = """
             <div id="hometabs" >
             <ul id="suit_form_tabs" class="nav nav-tabs nav-tabs-suit" data-tab-prefix="suit-tab">
             %s
             </ul>
             %s
             </div>
            """ % ("\n".join(tabs), "\n".join(bodies))

        t = template.Template(head_template + contents + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            context=context,
            **response_kwargs)

    def singleDashboardView(self, request, id, context):
        head_template = self.head_template
        tail_template = self.tail_template

        # if id is a number, load by datamodel,
        # else look directly for the template
        if(isInt(id)):
            view = DashboardView.objects.get(id=id)
            t = template.Template(head_template + self.embedDashboardView(view) + self.tail_template)
        else:
            t = template.Template(head_template + self.readTemplate("xos" + id) + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            context=context,
            **response_kwargs)

    def singleFullView(self, request, id, context):
        head_template = self.head_wholePage_template
        tail_template = self.tail_template

        view = DashboardView.objects.get(id=id)

        t = template.Template(head_template + self.embedDashboardView(view) + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            context=context,
            **response_kwargs)
